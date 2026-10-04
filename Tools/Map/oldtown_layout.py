"""Cidade Antiga W1.5 organic layout (pure Python).

Grows the Old Town as nine neighbourhoods with their own orientation, block sizes, warp and character,
around hand-authored main streets that front every hero location, the R02/R09 arterials and the old railway.
Produces: street graph (main/local/alley/passage/service + arterials), plazas, hero site plans, lots with
building family variants, infrastructure/vegetation/lighting points for the production core, and metrics.
"""
import json
import math
import random
import zlib
from pathlib import Path

from sa_geom import (OBB, Noise2, SpatialHash, chaikin, dist, lerp, norm, obb_overlap, perp, point_seg, resample,
                     segment_obb, seg_intersection, sub)
from urban_fabric import (CHARACTER, MAIN_STREET_BIAS, OLDTOWN_VARIANTS, STREET, LotPacker, StreetGraph, carriageway,
                          organic_grid, pick, remove_hitting, remove_near_parallel, stitch_dead_ends)

REGION = {"x_max": -1250.0, "z_min": -3880.0, "z_max": -480.0}

NEIGHBOURHOODS = [
    {"id": "estacao", "name": "Largo da Estação", "seed": (-3400, -1900), "character": "core_rail", "orient": 6, "spacing": (55, 85), "warp": 7, "wl": 260},
    {"id": "vila_horizonte", "name": "Vila Horizonte", "seed": (-2500, -1650), "character": "core_mixed", "orient": 14, "spacing": (60, 100), "warp": 9, "wl": 300},
    {"id": "imperial", "name": "Bairro Imperial", "seed": (-2000, -2350), "character": "core_stately", "orient": -9, "spacing": (70, 115), "warp": 8, "wl": 320},
    {"id": "oficinas", "name": "Bairro das Oficinas", "seed": (-3150, -2600), "character": "workshops", "orient": 4, "spacing": (80, 125), "warp": 11, "wl": 360},
    {"id": "alto_aurora", "name": "Alto da Aurora", "seed": (-2250, -850), "character": "residential_low", "orient": 20, "spacing": (85, 135), "warp": 15, "wl": 420},
    {"id": "mercado_norte", "name": "Mercado Norte", "seed": (-3200, -1050), "character": "mixed_low", "orient": -4, "spacing": (75, 120), "warp": 12, "wl": 380},
    {"id": "leste_antigo", "name": "Leste Antigo", "seed": (-1600, -1750), "character": "mixed_low", "orient": 27, "spacing": (80, 130), "warp": 13, "wl": 400},
    {"id": "porto_seco", "name": "Porto Seco", "seed": (-2600, -3450), "character": "depots", "orient": 0, "spacing": (110, 170), "warp": 6, "wl": 500},
    {"id": "vila_sul", "name": "Vila Sul", "seed": (-1700, -3000), "character": "residential_low", "orient": -15, "spacing": (85, 135), "warp": 14, "wl": 420},
]
HOOD_BY_ID = {h["id"]: h for h in NEIGHBOURHOODS}
ARTERIALS_IN_OLD = ("R02", "R09")


def rail_x(z):
    """Main railway centre-line x at a given z (parallel to R07, 70 m east)."""
    return -3900.0 + 600.0 * (z + 3000.0) / 5500.0 + 70.0


def load_heroes(root):
    p = Path(root) / "ArtSource" / "Blender" / "World" / "OldTown" / "oldtown_heroes_v1.json"
    return json.loads(p.read_text(encoding="utf-8"))


def rect_obb(r, pad=0.0):
    x0, z0, x1, z1 = r
    return OBB(((x0 + x1) / 2, (z0 + z1) / 2), (1.0, 0.0), (x1 - x0) / 2 + pad, (z1 - z0) / 2 + pad)


class OldTown:
    def __init__(self, root, spec, seed=1505):
        self.root = Path(root)
        self.spec = spec
        self.data = load_heroes(root)
        self.rng = random.Random(seed)
        self.errors, self.warnings = [], []
        self.core = tuple(self.data["productionCore"])
        warp_rng = random.Random(seed + 7)
        self._hwx, self._hwz = Noise2(warp_rng, 700, 2), Noise2(warp_rng, 700, 2)
        self.graph = StreetGraph()
        self._build_obstacles()
        self._build_skeleton()
        self._build_grid()
        self._refine_network()
        self._pack_lots()
        self._infrastructure()
        self.metrics = self._metrics()

    # ---------------------------------------------------------------- regions
    def in_region(self, p):
        x, z = p
        return REGION["z_min"] <= z <= REGION["z_max"] and x <= REGION["x_max"] and x >= rail_x(z) + 16.0

    def hood_of(self, p):
        x, z = p
        wx, wz = x + 130 * self._hwx(x, z), z + 130 * self._hwz(x, z)
        return min(NEIGHBOURHOODS, key=lambda h: (wx - h["seed"][0]) ** 2 + (wz - h["seed"][1]) ** 2)["id"]

    def in_core(self, p):
        x0, z0, x1, z1 = self.core
        return x0 <= p[0] <= x1 and z0 <= p[1] <= z1

    # ---------------------------------------------------------------- obstacles
    def _build_obstacles(self):
        d = self.data
        self.hero_obbs = {h["id"]: rect_obb(h["lot"]) for h in d["heroes"]}
        self.special_obbs = {s["id"]: rect_obb(s["rect"]) for s in d["specialLots"]}
        self.plaza_obbs = {p["id"]: rect_obb(p["rect"]) for p in d["plazas"]}
        self.landmark_obbs = {}
        for lm in d["landmarks"]:
            self.landmark_obbs[lm["id"]] = rect_obb(lm["rect"])
            self.landmark_obbs[lm["id"] + ".platform"] = rect_obb(lm["platform"])
        self.rail = [r for r in self.spec.get("railways", []) if r["kind"] == "main"][0]
        self.rail_obbs = []
        for rail in self.spec.get("railways", []):
            for a, b in zip(rail["points"], rail["points"][1:]):
                self.rail_obbs.append(segment_obb(tuple(a), tuple(b), rail["width"] + 6))
        # Campaign/life footprints that fall inside the Old Town area but are not hero site plans.
        self.other_obbs = {}
        for loc in self.spec["campaignLocations"] + self.spec["lifeLocations"]:
            if loc["id"] in self.hero_obbs or loc["id"] in self.special_obbs:
                continue
            w, dd = loc.get("width", 20), loc.get("depth", 20)
            if self.in_region((loc["x"], loc["z"])):
                self.other_obbs[loc["id"]] = OBB.axis_aligned(loc["x"], loc["z"], w, dd)

    def street_obstacles(self, hero_pad=4.0):
        out = [o.grown(hero_pad) for o in self.hero_obbs.values()]
        out += [o.grown(2.0) for o in self.special_obbs.values()]
        out += [o.grown(1.0) for o in self.plaza_obbs.values()]
        out += [o.grown(2.0) for o in self.landmark_obbs.values()]
        out += [o.grown(2.0) for o in self.other_obbs.values()]
        out += self.rail_obbs
        return out

    # ---------------------------------------------------------------- skeleton
    def _clip(self, pts, margin=120.0):
        out, cur = [], []
        for p in resample(pts, 40.0):
            inside = (REGION["z_min"] - margin <= p[1] <= REGION["z_max"] + margin and p[0] <= REGION["x_max"] + margin
                      and p[0] >= rail_x(p[1]) - margin)
            if inside:
                cur.append(p)
            elif cur:
                if len(cur) > 1:
                    out.append(cur)
                cur = []
        if len(cur) > 1:
            out.append(cur)
        return out

    def _build_skeleton(self):
        self.main_polys = {}
        for rid in ARTERIALS_IN_OLD:
            road = next(r for r in self.spec["roads"] if r["id"] == rid)
            for k, piece in enumerate(self._clip(road["points"])):
                self.graph.add_polyline(piece, "arterial", name=road["name"], zone="arterial", road=rid)
        for sid, s in self.data["mainStreets"].items():
            pts = [tuple(p) for p in s["points"]]
            if s["cls"] == "main":
                pts = resample(chaikin(pts, 2), 40.0)
            self.main_polys[sid] = pts
            self.graph.add_polyline(pts, s["cls"], name=s["name"], zone="main", street_id=sid)
        self.guide_classes = {"arterial", "main", "collector", "alley", "service"}

    # ---------------------------------------------------------------- organic grid
    def _build_grid(self):
        for h in NEIGHBOURHOODS:
            hid = h["id"]
            rng = random.Random(zlib.crc32(hid.encode()) ^ 1505)
            organic_grid(self.graph, lambda p, hid=hid: self.in_region(p) and self.hood_of(p) == hid, h["seed"], h["orient"],
                         h["spacing"], h["warp"], h["wl"], rng, cls="local", zone=hid, extent=(1700, 1700))

    def _refine_network(self):
        g = self.graph
        self.removed = {}
        self.removed["obstacles"] = remove_hitting(g, self.street_obstacles(), {"local"})
        guides = [eid for eid, e in g.edges.items() if e["cls"] in self.guide_classes]
        self.removed["parallel"] = remove_near_parallel(g, guides, 26.0, 35.0, {"local"})
        g.split_crossings({"arterial", "main", "collector", "alley", "service"})
        # Group local pieces by grid side so whole sides can be merged away.
        sides = {}
        for eid, e in g.edges.items():
            if e["cls"] == "local" and "grid" in e:
                sides.setdefault((e["zone"], e["grid"]), []).append(eid)
        side_keys = sorted(sides)
        self.rng.shuffle(side_keys)
        deg = g.degree()
        merged = deadend = 0
        n_merge = int(len(side_keys) * .07)
        n_dead = int(len(side_keys) * .04)
        for key in side_keys:
            pieces = [e for e in sides[key] if e in g.edges]
            if not pieces:
                continue
            ends = self._side_ends(pieces)
            if merged < n_merge and ends and all(deg.get(n, 0) >= 3 for n in ends):
                for e in pieces:
                    ed = g.edges.pop(e)
                    deg[ed["a"]] -= 1
                    deg[ed["b"]] -= 1
                merged += 1
            elif deadend < n_dead and len(pieces) >= 2:
                e = pieces[len(pieces) // 2]
                ed = g.edges.pop(e)
                deg[ed["a"]] -= 1
                deg[ed["b"]] -= 1
                deadend += 1
        self.removed["merged_sides"] = merged
        self.removed["dead_end_cuts"] = deadend
        self.stitched = stitch_dead_ends(g, 75.0, self.rng, cls="local",
                                         zone_of=lambda n: self.hood_of(g.nodes[n]), obstacles=self.street_obstacles())
        self._alleys_and_passages(sides)
        self.pruned = g.prune_to({"arterial", "main"})

    def _side_ends(self, pieces):
        g = self.graph
        count = {}
        for e in pieces:
            for n in (g.edges[e]["a"], g.edges[e]["b"]):
                count[n] = count.get(n, 0) + 1
        return [n for n, c in count.items() if c == 1]

    def _insert_point(self, eid, p):
        g = self.graph
        e = g.edges.pop(eid)
        n = g.node(p)
        extra = {k: v for k, v in e.items() if k not in ("a", "b", "cls", "name", "zone")}
        g.add_edge(e["a"], n, e["cls"], e["name"], e["zone"], **extra)
        g.add_edge(n, e["b"], e["cls"], e["name"], e["zone"], **extra)
        return n

    def _alleys_and_passages(self, sides):
        g = self.graph
        obst = self.street_obstacles(hero_pad=2.0)
        oh = SpatialHash(100.0)
        for o in obst:
            oh.insert(o.aabb(), o)
        keys = sorted(sides)
        self.rng.shuffle(keys)
        self.alleys = self.passages = 0
        for key in keys:
            pieces = [e for e in sides[key] if e in g.edges]
            if not pieces:
                continue
            roll = self.rng.random()
            if roll > .075:
                continue
            kind = "alley" if roll < .055 else "passage"
            eid = pieces[len(pieces) // 2]
            a, b = g.seg(eid)
            if dist(a, b) < 20:
                continue
            mid = lerp(a, b, .5)
            u = norm(sub(b, a))
            n = perp(u)
            if self.rng.random() < .5:
                n = (-n[0], -n[1])
            reach = self.rng.uniform(24, 40) if kind == "alley" else 95.0
            start = (mid[0] + n[0] * STREET["local"]["total"] / 2, mid[1] + n[1] * STREET["local"]["total"] / 2)
            far = (mid[0] + n[0] * reach, mid[1] + n[1] * reach)
            hit_pt, hit_e = None, None
            h = g.edge_hash()
            aabb = (min(start[0], far[0]), min(start[1], far[1]), max(start[0], far[0]), max(start[1], far[1]))
            best_t = 2.0
            for oe in h.query(aabb):
                if oe == eid or oe not in g.edges:
                    continue
                c, d = g.seg(oe)
                r = seg_intersection(start, far, c, d)
                if r and r[1] < best_t:
                    best_t, hit_pt, hit_e = r[1], r[0], oe
            if kind == "alley":
                if hit_pt is not None:
                    continue
                end = far
            else:
                if hit_pt is None or g.edges[hit_e]["cls"] not in ("local", "main"):
                    continue
                end = hit_pt
            s = segment_obb(mid, end, STREET[kind]["total"] + 2)
            if any(obb_overlap(s, o) for o in oh.query(s.aabb())):
                continue
            n0 = self._insert_point(eid, mid)
            if kind == "alley":
                g.add_edge(n0, g.node(end), "alley", zone=key[0])
                self.alleys += 1
            else:
                n1 = self._insert_point(hit_e, end)
                g.add_edge(n0, n1, "passage", zone=key[0])
                self.passages += 1

    # ---------------------------------------------------------------- lots
    def _pack_lots(self):
        g = self.graph
        packer = LotPacker(g, self.rng)
        packer.block_streets()
        for o in self.hero_obbs.values():
            packer.block(o.grown(1.5), "hero")
        for o in self.special_obbs.values():
            packer.block(o.grown(1.0), "special")
        for o in self.plaza_obbs.values():
            packer.block(o, "plaza")
        for o in self.landmark_obbs.values():
            packer.block(o.grown(1.0), "landmark")
        for o in self.other_obbs.values():
            packer.block(o.grown(1.0), "other")
        for o in self.rail_obbs:
            packer.block(o, "rail")
        # Hero forecourts stay open between the facade and the street.
        for h in self.data["heroes"]:
            for pk in h.get("parking", []):
                if pk.get("kind") in ("car", "dropoff", "truck"):
                    packer.block(rect_obb(pk["rect"]), "parking")
        variants_by_family = {}
        for v in OLDTOWN_VARIANTS:
            variants_by_family.setdefault(v["family"], []).append(v)
        rng = self.rng

        def choose(side, p, e):
            if not self.in_region(p):
                return None
            hood = HOOD_BY_ID[self.hood_of(p)]
            weights = dict(CHARACTER[hood["character"]])
            if e["cls"] in ("main", "arterial"):
                weights = {k: w * MAIN_STREET_BIAS.get(k, 1.0) for k, w in weights.items()}
            if abs(p[0] - rail_x(p[1])) < 160:
                weights["armazem"] = weights.get("armazem", 0) * 2.5 + 8
                weights["deposito"] = weights.get("deposito", 0) * 1.5 + 4
            r = rng.random()
            core = self.in_core(p)
            if r < (.035 if core else .06):
                return {"family": "vacant", "variant": "vacant", "w": rng.uniform(10, 22), "d": rng.uniform(16, 28),
                        "setback": 0.0, "gap": 0.0, "hood": hood["id"], "height": 0.0}
            if r < (.06 if core else .08):
                return {"family": "parking", "variant": "parking", "w": rng.uniform(18, 30), "d": rng.uniform(20, 30),
                        "setback": 0.0, "gap": 0.0, "hood": hood["id"], "height": 0.0}
            fam = pick(rng, weights)
            v = rng.choice(variants_by_family[fam])
            gap = 0.0 if v["attached"] else rng.uniform(1.5, 3.0)
            if v["attached"] and rng.random() < .12:
                gap = rng.uniform(1.0, 1.6)  # narrow side passage between attached buildings
            return {"family": fam, "variant": v["id"], "w": v["w"], "d": v["d"], "setback": v["setback"], "gap": gap,
                    "hood": hood["id"], "height": v["height"], "floors": v["floors"], "min_d": v["d"] * .99, "shrinkable": False}

        for c in ("arterial", "main", "local"):
            chains = packer.chains({c})
            rng.shuffle(chains)
            for ch in chains:
                packer.pack_chain(ch, choose)
        self.lots = packer.lots
        for k, lot in enumerate(self.lots):
            lot["id"] = f"OT_LOT_{k:05d}"
            lot["core"] = self.in_core(lot["obb"].c)

    # ---------------------------------------------------------------- infrastructure / vegetation / lighting
    def _infrastructure(self):
        g = self.graph
        rng = random.Random(1506)
        deg = g.degree()
        inc = g.incident()
        pts = {k: [] for k in ("pole", "pole_transformer", "streetlight_head", "manhole", "storm_inlet", "hydrant", "telecom_box",
                               "electric_box", "water_meter", "street_sign", "stop_sign", "traffic_light", "tree", "bench", "bollard")}
        pole_count = 0
        for eid, e in g.edges.items():
            if e["cls"] in ("passage", "alley", "service"):
                continue
            a, b = g.seg(eid)
            mid = lerp(a, b, .5)
            if not self.in_core(mid):
                continue
            L = dist(a, b)
            u = norm(sub(b, a))
            n = perp(u)
            cw = carriageway(e["cls"])
            sw = STREET[e["cls"]]["sidewalk"]
            rot = math.atan2(u[1], u[0])
            side = 1 if (eid % 2) else -1
            # Poles with luminaires on one side, alternating per edge.
            t = 6.0
            while t < L - 4:
                k = pole_count
                pole_count += 1
                p = (a[0] + u[0] * t + n[0] * side * (cw / 2 + .55), a[1] + u[1] * t + n[1] * side * (cw / 2 + .55))
                kind = "pole_transformer" if k % 5 == 4 else "pole"
                pts[kind].append((p[0], p[1], rot + (0 if side > 0 else math.pi)))
                head = (p[0] - n[0] * side * 1.6, p[1] - n[1] * side * 1.6)
                pts["streetlight_head"].append((head[0], head[1], rot))
                if k % 3 == 1:
                    q = (a[0] + u[0] * (t + 1.4) + n[0] * side * (cw / 2 + sw - .4), a[1] + u[1] * (t + 1.4) + n[1] * side * (cw / 2 + sw - .4))
                    pts["telecom_box"].append((q[0], q[1], rot))
                t += 32.0 + rng.uniform(-3, 3)
            t = 20.0
            while t < L - 10:
                pts["manhole"].append((a[0] + u[0] * t, a[1] + u[1] * t, rot))
                t += 45.0
            for end, sgn in ((a, 1), (b, -1)):
                nid = e["a"] if sgn > 0 else e["b"]
                if deg.get(nid, 0) >= 3:
                    for s2 in (1, -1):
                        q = (end[0] + u[0] * sgn * 8 + n[0] * s2 * (cw / 2 - .3), end[1] + u[1] * sgn * 8 + n[1] * s2 * (cw / 2 - .3))
                        pts["storm_inlet"].append((q[0], q[1], rot))
            t = 50.0
            while t < L - 10:
                q = (a[0] + u[0] * t - n[0] * side * (cw / 2 + .5), a[1] + u[1] * t - n[1] * side * (cw / 2 + .5))
                pts["hydrant"].append((q[0], q[1], rot))
                t += 115.0
            if e["cls"] in ("main", "arterial") and sw >= 3.0:
                t = 9.0
                while t < L - 6:
                    for s2 in (1, -1):
                        q = (a[0] + u[0] * t + n[0] * s2 * (cw / 2 + 1.0), a[1] + u[1] * t + n[1] * s2 * (cw / 2 + 1.0))
                        pts["tree"].append((q[0], q[1], rng.uniform(0, 6.28)))
                    t += 15.0 + rng.uniform(-2, 2)
        # Junction furniture: name signs, stop signs on minor approaches, traffic lights on main/arterial crossings.
        for nid, eids in inc.items():
            if deg.get(nid, 0) < 3 or not self.in_core(g.nodes[nid]):
                continue
            p = g.nodes[nid]
            classes = [g.edges[e]["cls"] for e in eids]
            major = len({g.edges[e].get("name") or e for e in eids if g.edges[e]["cls"] in ("main", "arterial")})
            corner_r = max(carriageway(c) for c in classes) / 2 + 1.2
            ang0 = rng.uniform(0, 6.28)
            pts["street_sign"].append((p[0] + math.cos(ang0) * corner_r, p[1] + math.sin(ang0) * corner_r, ang0))
            if major >= 2 and deg[nid] >= 3:
                for k2 in range(4):
                    ang = ang0 + k2 * math.pi / 2 + math.pi / 4
                    pts["traffic_light"].append((p[0] + math.cos(ang) * (corner_r + 1), p[1] + math.sin(ang) * (corner_r + 1), ang + math.pi))
            elif major >= 1:
                for e in eids:
                    if g.edges[e]["cls"] == "local":
                        other = g.edges[e]["b"] if g.edges[e]["a"] == nid else g.edges[e]["a"]
                        d = norm(sub(g.nodes[other], p))
                        q = (p[0] + d[0] * (corner_r + 3) + perp(d)[0] * -3.5, p[1] + d[1] * (corner_r + 3) + perp(d)[1] * -3.5)
                        pts["stop_sign"].append((q[0], q[1], math.atan2(d[1], d[0])))
        # Lot frontage meters and boxes (core).
        for lot in self.lots:
            if not lot["core"] or lot["family"] in ("vacant", "parking"):
                continue
            f = lot["front"]
            o = lot["obb"]
            back = norm(sub(o.c, f))
            along = perp(back)
            q = (f[0] + back[0] * (lot.get("setback", 0) + .2) + along[0] * (o.hw * .6), f[1] + back[1] * (lot.get("setback", 0) + .2) + along[1] * (o.hw * .6))
            pts["water_meter"].append((q[0], q[1], lot["rot"]))
            if lot["family"] in ("comercio_residencia", "pequeno_comercial", "predio_4a6", "oficina", "armazem"):
                q2 = (q[0] - along[0] * 1.2, q[1] - along[1] * 1.2)
                pts["electric_box"].append((q2[0], q2[1], lot["rot"]))
        # Plazas: trees on a loose grid, benches and bollards on the edges.
        for pl in self.data["plazas"]:
            x0, z0, x1, z1 = pl["rect"]
            x = x0 + 8
            while x < x1 - 6:
                z = z0 + 8
                while z < z1 - 6:
                    edge = min(x - x0, x1 - x, z - z0, z1 - z) < 14
                    if rng.random() < (.45 if edge else .12):
                        pts["tree"].append((x + rng.uniform(-2, 2), z + rng.uniform(-2, 2), rng.uniform(0, 6.28)))
                    elif rng.random() < .25:
                        pts["bench"].append((x, z, rng.choice((0, math.pi / 2))))
                    z += 11
                x += 11
            for k2 in range(int((x1 - x0) // 3)):
                pts["bollard"].append((x0 + 1.5 + k2 * 3, z0 + .5, 0.0))
        # Back-yard trees in houses (whole Old Town, lighter density).
        for lot in self.lots:
            if lot["family"] == "casa_terrea" and rng.random() < .45:
                o = lot["obb"]
                q = (o.c[0] + o.v[0] * (o.hd + 3), o.c[1] + o.v[1] * (o.hd + 3))
                pts["tree"].append((q[0], q[1], rng.uniform(0, 6.28)))
        self.points = pts

    # ---------------------------------------------------------------- metrics
    def _metrics(self):
        g = self.graph
        deg = g.degree()
        cls_len = {}
        for eid, e in g.edges.items():
            a, b = g.seg(eid)
            cls_len[e["cls"]] = cls_len.get(e["cls"], 0) + dist(a, b)
        dead_ends = sum(1 for n, d in deg.items() if d == 1)
        # Orientation spread of local streets (12 bins of 15 degrees, normalised entropy 0..1).
        bins = [0.0] * 12
        for eid, e in g.edges.items():
            if e["cls"] != "local":
                continue
            a, b = g.seg(eid)
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180
            bins[int(ang // 15) % 12] += dist(a, b)
        tot = sum(bins) or 1
        ent = -sum((v / tot) * math.log(v / tot) for v in bins if v > 0) / math.log(12)
        fam = {}
        var = set()
        for lot in self.lots:
            fam[lot["family"]] = fam.get(lot["family"], 0) + 1
            var.add(lot["variant"])
        core_lots = [l for l in self.lots if l["core"] and l["family"] not in ("vacant", "parking")]
        x0, z0, x1, z1 = self.core
        core_area = (x1 - x0) * (z1 - z0)
        cover = sum(l["obb"].hw * l["obb"].hd * 4 for l in core_lots) / core_area
        heights = [l["floors"] for l in self.lots if l.get("floors")]
        return {
            "neighbourhoods": len(NEIGHBOURHOODS),
            "streetKmByClass": {k: round(v / 1000, 2) for k, v in sorted(cls_len.items())},
            "deadEnds": dead_ends,
            "alleys": self.alleys,
            "passages": self.passages,
            "plazas": len(self.data["plazas"]),
            "stitchedSeams": self.stitched,
            "removed": self.removed,
            "prunedFragments": self.pruned,
            "orientationEntropy": round(ent, 3),
            "lots": len(self.lots),
            "lotsByFamily": dict(sorted(fam.items())),
            "variantsUsed": len(var),
            "coreBuildings": len(core_lots),
            "coreCoverage": round(cover, 3),
            "floorsRange": [min(heights), max(heights)] if heights else None,
            "infrastructure": {k: len(v) for k, v in self.points.items()},
        }

    # ---------------------------------------------------------------- checks used by the validator
    def checks(self):
        g = self.graph
        hard = {**self.hero_obbs, **self.special_obbs, **self.landmark_obbs, **self.other_obbs}
        h = SpatialHash(100.0)
        for k, o in hard.items():
            h.insert(o.aabb(), (k, o))
        for eid, e in g.edges.items():
            a, b = g.seg(eid)
            s = segment_obb(a, b, STREET[e["cls"]]["total"])
            for k, o in h.query(s.aabb()):
                if obb_overlap(s, o):
                    self.errors.append(f"old town street {e.get('name') or e['cls']} ({e['cls']}) overlaps {k}")
        lot_hash = SpatialHash(60.0)
        for lot in self.lots:
            for k, o in h.query(lot["obb"].aabb()):
                if obb_overlap(lot["obb"], o):
                    self.errors.append(f"lot {lot['id']} overlaps {k}")
            for other in lot_hash.query(lot["obb"].aabb()):
                if obb_overlap(lot["obb"].grown(-0.05), other["obb"].grown(-0.05)):
                    self.errors.append(f"lots overlap {lot['id']} / {other['id']}")
            lot_hash.insert(lot["obb"].aabb(), lot)
        # Every hero fronts its street within 35 m of its lot.
        for hero in self.data["heroes"]:
            sid = hero["street"]
            o = self.hero_obbs[hero["id"]]
            best = 1e9
            for eid, e in g.edges.items():
                if e.get("street_id") == sid or e.get("road") == sid or (sid.startswith("largo") and e["cls"] in ("main", "arterial")):
                    a, b = g.seg(eid)
                    for c in o.corners():
                        best = min(best, point_seg(c, a, b)[0])
            if sid.startswith("largo"):
                pl = self.plaza_obbs.get(sid)
                if pl and obb_overlap(o.grown(8), pl):
                    best = 0
            if best > 42:
                self.errors.append(f"hero {hero['id']} does not front its street {sid} (nearest {best:.0f} m)")
        m = self.metrics
        if m["orientationEntropy"] < .6:
            self.errors.append(f"old town street orientation too uniform (entropy {m['orientationEntropy']})")
        if m["deadEnds"] < 25 or m["alleys"] < 25 or m["passages"] < 5:
            self.warnings.append(f"old town irregularity low: dead ends {m['deadEnds']}, alleys {m['alleys']}, passages {m['passages']}")
        if m["variantsUsed"] < 35:
            self.warnings.append(f"only {m['variantsUsed']} building variants used")
        return self.errors, self.warnings
