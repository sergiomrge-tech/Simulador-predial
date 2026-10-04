"""Deterministic Santa Aurora masterplan layout, revision W1.5 (pure Python, no Blender).

Shared by Tools/Map/validate_masterplan.py, Tools/Map/masterplan_routes.py and the Blender generators,
so what is validated is exactly what is generated.

W1.5 adds: terrain (sa_terrain), smoothed arterials with roundabouts, the western railway, the organic
Old Town (oldtown_layout), transition zones, densified district fabric (urban_fabric) including the
industrial composer, vegetation points and the scale/skyline/coverage checks.
Coordinates are spec metres: x = east, z = north. Blender maps spec z -> Blender Y.
Everything here is planning geometry; production art follows the Art Bible (never low-poly as final).
"""
import json
import math
import random
import zlib
from pathlib import Path

from oldtown_layout import OldTown
from sa_geom import (OBB, Noise2, SpatialHash, chaikin, dist, fillet_polyline, lerp, norm, obb_overlap, perp, point_seg,
                     polyline_length, resample, segment_obb, segs_cross, sub)
from sa_terrain import Terrain
from urban_fabric import (GENERIC, PROFILES, SKYLINE_TARGETS, STREET, LotPacker, StreetGraph, compose_industrial,
                          organic_grid, pick, remove_hitting, remove_near_parallel, stitch_dead_ends)

ROAD_WIDTH = {"arterial": 30.0, "collector": 18.0, "local": 12.0, "driveway": 8.0}
SETBACK = 6.0
ACCESS_MAX_GAP = 90.0
FILLET = {"arterial": 160.0, "collector": 90.0}
DISTRICT_ORDER = ["civic", "expansion", "industrial", "corporate", "technology"]
DISTRICT_PROFILE = {"expansion": "expansion", "civic": "civic", "corporate": "corporate", "industrial": "industrial", "technology": "technology"}
CORPORATE_PEAK = (2400.0, -200.0)
TECH_PEAK = (2550.0, 2650.0)
# Prototype locomotion (FacilityOps/Assets/_Game/Scripts/Runtime/Interaction.cs): walk 3 m/s, sprint 5 m/s.
WALK_MS, SPRINT_MS = 3.0, 5.0

# Composite massing inside campaign footprints outside the Old Town: (dx, dz, w, d, h, role).
CAMPAIGN_MASSING = {
    "school":        [(-30, 30, 36, 60, 9, "classroom_wing"), (20, 45, 56, 30, 9, "classroom_wing"), (25, -35, 46, 40, 8, "gym_kitchen")],
    "recurringcondo": [(0, 0, 130, 160, 4, "podium_garage"), (-34, -40, 30, 36, 50, "tower_a"), (34, 40, 30, 36, 50, "tower_b"), (0, -82, 16, 10, 5, "portaria")],
    "lostcondo":     [(0, 0, 145, 185, 4, "podium_garage"), (-40, -55, 28, 34, 56, "tower_a"), (40, -10, 28, 34, 56, "tower_b"), (-20, 60, 28, 34, 56, "tower_c")],
    "hotel":         [(0, 0, 90, 112, 9, "podium_service"), (0, 10, 40, 72, 41, "guest_tower"), (35, -50, 18, 14, 6, "service_dock")],
    "smallhospital": [(0, 10, 70, 100, 20, "main_ward"), (-38, -40, 36, 56, 12, "outpatient"), (40, -55, 26, 30, 8, "technical_entry")],
    "companyhq":     [(-25, -40, 60, 56, 9, "offices"), (15, 30, 90, 70, 10, "fleet_workshop"), (50, -55, 20, 30, 5, "loading")],
    "mall":          [(0, 10, 210, 220, 18, "mall_box"), (-75, -105, 70, 40, 24, "garage_tower"), (90, -100, 30, 40, 8, "service_dock")],
    "hospital0317":  [(0, 0, 90, 150, 28, "hot_wing"), (-60, 60, 50, 80, 20, "ward_b"), (60, -60, 45, 80, 16, "hvac_plant"), (60, 80, 40, 50, 9, "technical_route")],
    "blackouttower": [(0, 0, 90, 104, 12, "podium"), (0, 5, 44, 50, 114, "office_tower")],
    "vertice":       [(0, 15, 60, 92, 31, "headquarters"), (0, -55, 110, 36, 10, "service_podium")],
    "logistics":     [(0, 40, 200, 190, 14, "warehouse"), (0, -105, 220, 60, 1, "truck_yard"), (-95, -60, 30, 20, 8, "office")],
    "factory":       [(-30, 50, 210, 170, 16, "production_hall"), (100, 70, 60, 70, 11, "utilities"), (100, -60, 50, 40, 8, "office_gate"),
                      (-110, -90, 50, 60, 12, "substation"), (55, -10, 6, 6, 48, "chimney"), (-30, -120, 200, 80, 1, "yard")],
    "drainage":      [(-15, 10, 56, 72, 12, "pump_hall"), (30, -40, 54, 56, 5, "reservoir"), (35, 50, 22, 26, 8, "control_room")],
    "datacenter":    [(-20, 20, 120, 150, 14, "data_halls"), (65, 20, 40, 90, 10, "cooling_plant"), (-20, -85, 120, 40, 4, "power_yard"),
                      (0, 0, 190, 2, 3, "perimeter_s"), (0, 0, 190, 2, 3, "perimeter_n"), (0, 0, 2, 230, 3, "perimeter_w"), (0, 0, 2, 230, 3, "perimeter_e")],
    "smarttower":    [(0, 0, 104, 124, 10, "podium"), (0, 0, 46, 52, 91, "smart_tower")],
    "central":       [(-100, 120, 100, 70, 24, "administrative_centre"), (40, 140, 70, 60, 20, "urban_monitoring"),
                      (130, 120, 70, 70, 14, "municipal_datacentre"), (140, 30, 14, 14, 62, "telecom_mast"),
                      (-120, 10, 70, 60, 14, "emergency_centre"), (-120, -100, 60, 70, 10, "electrical_distribution"),
                      (-30, -150, 70, 40, 8, "generators"), (60, -150, 50, 40, 9, "pumps_drainage"),
                      (130, -100, 60, 70, 11, "hvac_plant"), (120, -20, 40, 40, 16, "automation_controller"),
                      (0, 0, 220, 8, 2, "service_tunnel_ew"), (0, 0, 8, 300, 2, "service_tunnel_ns")],
}


def load_spec(root):
    path = Path(root) / "ArtSource" / "Blender" / "World" / "masterplan_spec_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(root):
    path = Path(root) / "ArtSource" / "Blender" / "World" / "structure_registry_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def rect(cx, cz, w, d, pad=0.0):
    return (cx - w / 2 - pad, cz - d / 2 - pad, cx + w / 2 + pad, cz + d / 2 + pad)


def rects_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def point_in_rect(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def point_seg_dist(p, a, b):
    d, q, _ = point_seg(p, a, b)
    return d, q


def segs_intersect(a, b, c, d):
    return segs_cross(a, b, c, d)


def seg_rect_dist(a, b, r):
    """Exact distance between a segment and an axis-aligned rectangle, plus closest pair (on_seg, on_rect)."""
    if point_in_rect(a, r):
        return 0.0, a, a
    corners = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    for i in range(4):
        if segs_cross(a, b, corners[i], corners[(i + 1) % 4]):
            return 0.0, a, a
    best = None
    for p in (a, b):
        dx = max(r[0] - p[0], 0, p[0] - r[2])
        dz = max(r[1] - p[1], 0, p[1] - r[3])
        q = (min(max(p[0], r[0]), r[2]), min(max(p[1], r[1]), r[3]))
        dd = math.hypot(dx, dz)
        if best is None or dd < best[0]:
            best = (dd, p, q)
    for c in corners:
        dd, q, _ = point_seg(c, a, b)
        if dd < best[0]:
            best = (dd, q, c)
    return best


def polyline_segments(points):
    return [(tuple(points[i]), tuple(points[i + 1])) for i in range(len(points) - 1)]


def circle(centre, r, n=48):
    return [(centre[0] + r * math.cos(2 * math.pi * k / n), centre[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]


class Layout:
    def __init__(self, spec, registry=None, root=None, seed=20261003):
        self.spec = spec
        self.registry = registry or {"locations": []}
        self.root = Path(root) if root else Path(__file__).resolve().parents[2]
        self.rng = random.Random(seed)
        self.errors, self.warnings = [], []
        w = spec["world"]
        self.world = (w["minX"], w["minZ"], w["maxX"], w["maxZ"])
        self.districts = {d["id"]: d for d in spec["districts"]}
        self.campaign = spec["campaignLocations"]
        self.life = spec["lifeLocations"]
        self.open_spaces = spec.get("openSpaces", [])
        self.canal = spec.get("canal")
        self.zones = spec.get("transitionZones", [])
        self.terrain = Terrain(spec)
        self.campaign_rects = {l["id"]: rect(l["x"], l["z"], l["width"], l["depth"]) for l in self.campaign}
        self.life_rects = {l["id"]: rect(l["x"], l["z"], 20, 20) for l in self.life}
        self.open_rects = {o["id"]: rect(o["x"], o["z"], o["width"], o["depth"]) for o in self.open_spaces}
        self._build_roads()
        self._build_rail()
        self.oldtown = OldTown(self.root, spec)
        self._build_zone_fabrics()
        self._collect_streets()
        self._build_driveways()
        self._build_vegetation()

    # ---------------------------------------------------------------- ownership
    def zone_of(self, p):
        for z in self.zones:
            if point_in_rect(p, z["bounds"]):
                return z["id"]
        if self.oldtown.in_region(p):
            return "old"
        for did in DISTRICT_ORDER:
            if point_in_rect(p, self.districts[did]["bounds"]):
                return did
        return "reserve"

    def district_of_zone(self, zid):
        return {"T_old_exp": "transition", "T_old_north": "transition", "T_ind_civic": "transition", "T_exp_civic": "transition",
                "T_civic_corp": "transition", "T_corp_tech": "transition", "T_canal": "transition", "T_exp_east": "transition"}.get(zid, zid)

    # ---------------------------------------------------------------- roads
    def _build_roads(self):
        self.roads = []
        self.roundabouts = []
        rbs = self.spec.get("roundabouts", [])
        for r in self.spec["roads"]:
            ctrl = [tuple(p) for p in (r.get("points") or [r["from"], r["to"]])]
            pts = fillet_polyline(ctrl, FILLET[r["class"]], seg_len=15.0)
            pieces = [pts]
            for rb in rbs:
                if r["id"] not in rb["roads"]:
                    continue
                c, rad = tuple(rb["centre"]), rb["radius"]
                new = []
                for piece in pieces:
                    cur = []
                    for p in resample(piece, 6.0):
                        if dist(p, c) > rad - 2.0:
                            cur.append(p)
                        else:
                            if len(cur) > 1:
                                new.append(cur)
                            cur = []
                    if len(cur) > 1:
                        new.append(cur)
                pieces = new
            for k, piece in enumerate(pieces):
                self.roads.append({"id": r["id"] if len(pieces) == 1 else f"{r['id']}.{k}", "base": r["id"], "name": r["name"],
                                   "class": r["class"], "width": ROAD_WIDTH[r["class"]], "points": piece, "control": ctrl})
        for rb in rbs:
            ring = circle(tuple(rb["centre"]), rb["radius"], 56)
            self.roundabouts.append({**rb, "ring": ring})
            self.roads.append({"id": rb["id"], "base": rb["id"], "name": rb["name"], "class": "arterial", "width": 12.0,
                               "points": ring, "control": ring, "roundabout": True})

    def road_segments(self):
        for road in self.roads:
            for a, b in polyline_segments(road["points"]):
                yield road, a, b

    def _build_rail(self):
        self.rails = []
        for r in self.spec.get("railways", []):
            pts = fillet_polyline([tuple(p) for p in r["points"]], 250.0 if r["kind"] == "main" else 80.0, 15.0)
            self.rails.append({**r, "geom": pts})

    def corridor_obbs(self, extra=0.0, include_canal=True):
        out = []
        for road, a, b in self.road_segments():
            out.append(segment_obb(a, b, road["width"] + 2 * extra))
        for r in self.rails:
            for a, b in polyline_segments(r["geom"]):
                out.append(segment_obb(a, b, r["width"] + 6 + 2 * extra))
        if include_canal and self.canal:
            for a, b in polyline_segments(self.canal["points"]):
                out.append(segment_obb(tuple(a), tuple(b), self.canal["width"] + 2 * 20 + 2 * extra))
        return out

    def footprint_obbs(self, pad=0.0):
        out = [OBB.axis_aligned((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, r[2] - r[0], r[3] - r[1]).grown(pad)
               for r in list(self.campaign_rects.values()) + list(self.life_rects.values())]
        out += [OBB.axis_aligned((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, r[2] - r[0], r[3] - r[1]).grown(pad) for r in self.open_rects.values()]
        for rb in self.roundabouts:
            c, rad = rb["centre"], rb["radius"]
            out.append(OBB(tuple(c), (1.0, 0.0), rad + 18, rad + 18))
        return out

    # ---------------------------------------------------------------- zone fabrics
    def _zone_bounds(self, zid):
        for z in self.zones:
            if z["id"] == zid:
                return z["bounds"], z["profile"]
        return self.districts[zid]["bounds"], DISTRICT_PROFILE[zid]

    def _build_zone_fabrics(self):
        self.zone_graphs = {}
        self.buildings = []   # generic massing volumes (not Old Town)
        self.cylinders = []
        self.open_pads = []
        zone_ids = [z["id"] for z in self.zones] + DISTRICT_ORDER
        obst = self.footprint_obbs(pad=6.0) + [o.grown(1.0) for o in self.oldtown.rail_obbs]
        canal_obbs = []
        if self.canal:
            for a, b in polyline_segments(self.canal["points"]):
                canal_obbs.append(segment_obb(tuple(a), tuple(b), self.canal["width"] + 2 * 22))
        obst += canal_obbs
        for zid in zone_ids:
            bounds, prof_id = self._zone_bounds(zid)
            prof = PROFILES[prof_id]
            rng = random.Random(zlib.crc32(zid.encode()) ^ 77)
            g = StreetGraph()
            x0, z0, x1, z1 = bounds
            margin = 260.0
            for road in self.roads:
                pts = [p for p in resample(road["points"], 30.0)
                       if x0 - margin <= p[0] <= x1 + margin and z0 - margin <= p[1] <= z1 + margin]
                if len(pts) > 1:
                    g.add_polyline(pts, "arterial" if road["class"] == "arterial" else "collector", name=road["name"], zone="spec", road=road["base"])
            # Old Town main streets that leave the Old Town (into T_old_north / T_old_exp) are guides too.
            for sid, pts in self.oldtown.main_polys.items():
                ins = [p for p in pts if x0 - margin <= p[0] <= x1 + margin and z0 - margin <= p[1] <= z1 + margin]
                if len(ins) > 1:
                    g.add_polyline(ins, "main", name=self.oldtown.data["mainStreets"][sid]["name"], zone="spec")
            cls = prof["street"]
            organic_grid(g, lambda p, zid=zid: self.zone_of(p) == zid, ((x0 + x1) / 2, (z0 + z1) / 2), prof["orient"], prof["spacing"],
                         prof["warp"], prof["wl"], rng, cls=cls, zone=zid, extent=((x1 - x0) / 2 + 200, (z1 - z0) / 2 + 200))
            remove_hitting(g, obst, {cls})
            guides = [eid for eid, e in g.edges.items() if e["zone"] == "spec"]
            remove_near_parallel(g, guides, 30.0, 35.0, {cls})
            g.split_crossings({"arterial", "collector", "main"})
            stitch_dead_ends(g, 90.0, rng, cls=cls, zone_of=None, obstacles=obst)
            g.prune_to({"arterial", "collector", "main"})
            self.zone_graphs[zid] = g
            self._pack_zone(zid, g, prof, rng, obst)

    def _pack_zone(self, zid, g, prof, rng, obst):
        packer = LotPacker(g, rng)
        packer.block_streets()
        for o in obst:
            packer.block(o, "obstacle")
        # Lots of neighbouring zones are already placed: block them so seams never overlap.
        for b in self.buildings:
            packer.block(b["lot"], "lot")
        zb, _ = self._zone_bounds(zid)
        near = (zb[0] - 300, zb[1] - 300, zb[2] + 300, zb[3] + 300)
        for lot in self.oldtown.lots:
            if point_in_rect(lot["obb"].c, near):
                packer.block(lot["obb"], "old_lot")
        og = self.oldtown.graph
        for e in og.edges.values():
            a, b = og.nodes[e["a"]], og.nodes[e["b"]]
            if point_in_rect(a, near):
                packer.block(segment_obb(a, b, STREET[e["cls"]]["total"]), "old_street")
        dist_name = self.district_of_zone(zid)

        def choose(side, p, e):
            if self.zone_of(p) != zid:
                return None
            fam = pick(rng, prof["fam"])
            f = GENERIC[fam]
            w = rng.uniform(*f["w"])
            d = rng.uniform(*f["d"])
            return {"family": fam, "w": w, "d": d, "setback": f["setback"] * rng.uniform(.6, 1.2),
                    "gap": 0.0 if f["attached"] else (rng.uniform(2, 5) if "tight" in f["tags"] else rng.uniform(4, 12)),
                    "min_d": d * .6, "shrinkable": True}

        order = [c for c in ("arterial", "collector", "main", "industrial", "local") if any(e["cls"] == c for e in g.edges.values())]
        for c in order:
            # Spec roads are shared between zones: choose() only accepts lots whose frontage lies inside this zone.
            chains = packer.chains({c})
            rng.shuffle(chains)
            for ch in chains:
                packer.pack_chain(ch, choose)
        for lot in packer.lots:
            self._lot_to_volumes(zid, dist_name, lot, rng)

    def _floors_for(self, zid, fam, f, c, rng):
        lo, hi = f["floors"]
        if hi == 0:
            return 0
        u = rng.random()
        if fam in ("office_tower",):
            closeness = max(0.0, 1 - dist(c, CORPORATE_PEAK) / 1700.0)
            u = min(1.0, u ** 1.4 * (.35 + .9 * closeness))
        elif fam in ("campus_tower",):
            closeness = max(0.0, 1 - dist(c, TECH_PEAK) / 1500.0)
            u = min(1.0, u ** 1.2 * (.4 + .8 * closeness))
        elif fam in ("condo_slab", "tower_res", "mid_res"):
            u = u ** 1.1
        return lo + int(round((hi - lo) * u))

    def _lot_to_volumes(self, zid, dist_name, lot, rng):
        fam = lot["family"]
        f = GENERIC[fam]
        obb = lot["obb"]
        base = {"zone": zid, "district": dist_name, "family": fam, "lot": obb}
        if "open" in f["tags"]:
            self.open_pads.append({**base, "kind": fam, "obb": obb})
            self.buildings.append({**base, "kind": "pad", "obb": obb, "h": 0.0, "floors": 0, "hidden": True})
            return
        if "composite" in f["tags"]:
            for part in compose_industrial(lot, rng):
                if part["kind"] in ("tank", "silo", "chimney"):
                    self.cylinders.append({**base, **part})
                elif part["kind"] in ("yard", "truck_parking"):
                    self.open_pads.append({**base, "kind": part["kind"], "obb": part["obb"]})
                else:
                    self.buildings.append({**base, "kind": part["kind"], "obb": part["obb"], "h": part["h"], "floors": 1 if part["kind"] == "shed" else 2,
                                           "roof": part.get("roof", "flat")})
            self.buildings.append({**base, "kind": "pad", "obb": obb, "h": 0.0, "floors": 0, "hidden": True})
            return
        floors = self._floors_for(zid, fam, f, obb.c, rng)
        h = floors * f["fh"]
        if f["podium"]:
            pf, ph = f["podium"]
            self.buildings.append({**base, "kind": "podium", "obb": obb, "h": pf * ph, "floors": pf})
            shrink = rng.uniform(.55, .78)
            tower = OBB(obb.c, obb.u, obb.hw * shrink, obb.hd * shrink)
            self.buildings.append({**base, "kind": "tower", "obb": tower, "h": pf * ph + h, "floors": pf + floors, "is_main": True})
        else:
            self.buildings.append({**base, "kind": "block", "obb": obb, "h": h, "floors": floors, "is_main": True})

    # ---------------------------------------------------------------- streets (all)
    def _collect_streets(self):
        """local_edges: zone -> list of (a, b, cls) for everything that is not a spec road (used by routes/drawing)."""
        self.local_edges = {}
        g = self.oldtown.graph
        self.local_edges["old"] = [(g.nodes[e["a"]], g.nodes[e["b"]], e["cls"]) for e in g.edges.values() if e["cls"] != "arterial"]
        for zid, zg in self.zone_graphs.items():
            self.local_edges[zid] = [(zg.nodes[e["a"]], zg.nodes[e["b"]], e["cls"]) for e in zg.edges.values()
                                     if e["zone"] != "spec"]

    def network_segments(self, vehicles=True):
        for road in self.roads:
            for a, b in polyline_segments(road["points"]):
                yield road["class"], road["width"], road["id"], a, b
        for zid, edges in self.local_edges.items():
            for a, b, cls in edges:
                if vehicles and cls == "passage":
                    continue
                yield cls, STREET[cls]["total"], f"{cls}.{zid}", a, b

    # ---------------------------------------------------------------- access
    def _build_driveways(self):
        segs = list(self.network_segments())
        h = SpatialHash(200.0)
        for s in segs:
            a, b = s[3], s[4]
            h.insert((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), s)
        targets = [(l["id"], "campaign", self.campaign_rects[l["id"]]) for l in self.campaign]
        anchored = {o["anchor"]: self.open_rects[o["id"]] for o in self.open_spaces if o.get("anchor")}
        targets += [(l["id"], "life", anchored.get(l["id"], self.life_rects[l["id"]])) for l in self.life]
        self.access = {}
        self.driveways = []
        for tid, kind, r in targets:
            best = None
            for reach in (150, 400, 1200):
                for cls, width, rid, a, b in h.query((r[0] - reach, r[1] - reach, r[2] + reach, r[3] + reach)):
                    d, on_seg, on_rect = seg_rect_dist(a, b, r)
                    gap = max(0.0, d - width / 2)
                    if best is None or gap < best[0]:
                        best = (gap, rid, cls, on_seg, on_rect)
                if best:
                    break
            gap, rid, cls, on_seg, on_rect = best
            self.access[tid] = {"kind": kind, "road": rid, "roadClass": cls, "gap": round(gap, 1)}
            limit = 130.0 if tid in ("leisure.park", "leisure.fishing") else ACCESS_MAX_GAP
            if gap > limit:
                self.errors.append(f"no plausible road access for {tid}: nearest {rid} at {gap:.0f} m")
                continue
            if gap > 1.0:
                self.driveways.append({"target": tid, "road": rid, "a": on_rect, "b": on_seg, "gap": round(gap, 1)})

    # ---------------------------------------------------------------- vegetation
    def _build_vegetation(self):
        rng = random.Random(4242)
        trees = []
        blockers = SpatialHash(80.0)
        for b in self.buildings:
            if b["kind"] != "pad":
                blockers.insert(b["obb"].aabb(), b["obb"])
        for lot in self.oldtown.lots:
            blockers.insert(lot["obb"].aabb(), lot["obb"])
        for o in self.footprint_obbs(2.0):
            blockers.insert(o.aabb(), o)

        def free(p):
            box = OBB(p, (1.0, 0.0), 1.5, 1.5)
            return all(not obb_overlap(box, o) for o in blockers.query(box.aabb()))

        for road in self.roads:
            if road.get("roundabout"):
                continue
            off_side = road["width"] / 2 - (3.0 if road["class"] == "arterial" else 2.0) + 1.0
            step = 15.0 if road["class"] == "arterial" else 18.0
            pts = resample(road["points"], step)
            for a, b in zip(pts, pts[1:]):
                u = norm(sub(b, a))
                n = perp(u)
                for s in ((1, -1) if road["class"] == "arterial" else (1,)):
                    p = (a[0] + n[0] * s * off_side, a[1] + n[1] * s * off_side)
                    if rng.random() < .85 and free(p):
                        trees.append((p[0], p[1], rng.uniform(.8, 1.25), "street"))
                if road["class"] == "arterial" and rng.random() < .6:
                    trees.append((a[0], a[1], rng.uniform(.7, 1.0), "median"))
        for pad in self.open_pads:
            if pad["kind"] in ("green", "sports"):
                o = pad["obb"]
                n = int(o.hw * o.hd * 4 / (180 if pad["kind"] == "green" else 900))
                for _ in range(n):
                    du, dv = rng.uniform(-o.hw, o.hw), rng.uniform(-o.hd, o.hd)
                    if pad["kind"] == "sports" and abs(dv) < o.hd - 6 and abs(du) < o.hw - 6:
                        continue
                    trees.append((o.c[0] + o.u[0] * du + o.v[0] * dv, o.c[1] + o.u[1] * du + o.v[1] * dv, rng.uniform(.8, 1.4), "park"))
        for osp in self.open_spaces:
            if osp.get("kind") == "water":
                continue
            r = self.open_rects[osp["id"]]
            for _ in range(int((r[2] - r[0]) * (r[3] - r[1]) / 220)):
                trees.append((rng.uniform(r[0], r[2]), rng.uniform(r[1], r[3]), rng.uniform(.8, 1.5), "park"))
        if self.canal:
            pts = resample([tuple(p) for p in self.canal["points"]], 12.0)
            for a, b in zip(pts, pts[1:]):
                n = perp(norm(sub(b, a)))
                for s in (1, -1):
                    for off in (40.0, 52.0):
                        p = (a[0] + n[0] * s * (off + rng.uniform(-3, 3)), a[1] + n[1] * s * (off + rng.uniform(-3, 3)))
                        if rng.random() < .7 and free(p):
                            trees.append((p[0], p[1], rng.uniform(.9, 1.4), "canal"))
        # Reserve belts: clustered woods, sparse fields.
        noise = Noise2(random.Random(99), 600, 2)
        x0, z0, x1, z1 = self.world
        x = x0 + 10
        while x < x1:
            z = z0 + 10
            while z < z1:
                p = (x + rng.uniform(-8, 8), z + rng.uniform(-8, 8))
                if self.zone_of(p) == "reserve" and noise(*p) > .15 and rng.random() < .55 and free(p):
                    trees.append((p[0], p[1], rng.uniform(.8, 1.6), "woods"))
                z += 24
            x += 24
        for kind, pts_ in (("old", self.oldtown.points.get("tree", ())),):
            for p in pts_:
                trees.append((p[0], p[1], rng.uniform(.8, 1.2), "old"))
        self.trees = trees

    # ---------------------------------------------------------------- campaign massing
    def campaign_volumes(self, loc):
        heroes = {h["id"]: h for h in self.oldtown.data["heroes"]}
        if loc["id"] in heroes:
            out = []
            for bld in heroes[loc["id"]]["buildings"]:
                x0, z0, x1, z1 = bld["rect"]
                h = bld["ground_h"] + bld["fh"] * (bld["floors"] - 1)
                out.append({"role": bld["role"], "x": (x0 + x1) / 2, "z": (z0 + z1) / 2, "w": x1 - x0, "d": z1 - z0, "h": float(h)})
            for it in heroes[loc["id"]].get("roof_items", []):
                x0, z0, x1, z1 = it["rect"]
                top = max(v["h"] for v in out)
                out.append({"role": it["role"], "x": (x0 + x1) / 2, "z": (z0 + z1) / 2, "w": x1 - x0, "d": z1 - z0, "h": top + it["h"]})
            return out
        parts = CAMPAIGN_MASSING.get(loc["id"])
        x, z, W, D = loc["x"], loc["z"], loc["width"], loc["depth"]
        if not parts:
            return [{"role": "envelope", "x": x, "z": z, "w": W - 4, "d": D - 4, "h": 12.0}]
        out = []
        for dx, dz, w, d, h, role in parts:
            if role == "perimeter_s":
                dx, dz = 0, -D / 2 + 1
            elif role == "perimeter_n":
                dx, dz = 0, D / 2 - 1
            elif role == "perimeter_w":
                dx, dz = -W / 2 + 1, 0
            elif role == "perimeter_e":
                dx, dz = W / 2 - 1, 0
            out.append({"role": role, "x": x + dx, "z": z + dz, "w": w, "d": d, "h": float(h)})
        return out

    # ---------------------------------------------------------------- reports
    def all_building_obbs(self):
        for b in self.buildings:
            if b["kind"] != "pad":
                yield b["district"], b["zone"], b["obb"], b["h"], b.get("floors", 0), b.get("is_main", False)
        for lot in self.oldtown.lots:
            if lot["family"] not in ("vacant", "parking"):
                yield "old", "old", lot["obb"], lot["height"], lot["floors"], True

    def checks(self):
        errs, warns = self.oldtown.checks()
        self.errors += errs
        self.warnings += warns
        # Campaign/life overlaps.
        for lid, lr in self.life_rects.items():
            for cid, cr in self.campaign_rects.items():
                if rects_overlap(lr, cr):
                    self.errors.append(f"life marker {lid} overlaps campaign footprint {cid}")
        for i, a in enumerate(self.campaign):
            for b in self.campaign[i + 1:]:
                if rects_overlap(self.campaign_rects[a["id"]], self.campaign_rects[b["id"]]):
                    self.errors.append(f"campaign footprints overlap: {a['id']} / {b['id']}")
        # Spec roads, rail and canal vs footprints.
        fp = {**{k: v for k, v in self.campaign_rects.items()}, **self.life_rects}
        for road, a, b in self.road_segments():
            for k, r in fp.items():
                d, _, _ = seg_rect_dist(a, b, r)
                if d < road["width"] / 2 + 3.0:
                    self.errors.append(f"road {road['id']} encroaches {k} (clear {d - road['width'] / 2:.1f} m)")
        for rail in self.rails:
            for a, b in polyline_segments(rail["geom"]):
                for k, r in fp.items():
                    if seg_rect_dist(a, b, r)[0] < rail["width"] / 2 + 3:
                        self.errors.append(f"rail {rail['id']} encroaches {k}")
        if self.canal:
            for a, b in polyline_segments(self.canal["points"]):
                for k, r in fp.items():
                    if seg_rect_dist(tuple(a), tuple(b), r)[0] < self.canal["width"] / 2 + 6:
                        self.errors.append(f"canal crosses {k}")
        # Zone streets vs footprints.
        fobb = {k: OBB.axis_aligned((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, r[2] - r[0], r[3] - r[1]) for k, r in fp.items()}
        fh = SpatialHash(150.0)
        for k, o in fobb.items():
            fh.insert(o.aabb(), (k, o))
        for zid, edges in self.local_edges.items():
            if zid == "old":
                continue
            for a, b, cls in edges:
                s = segment_obb(a, b, STREET[cls]["total"])
                for k, o in fh.query(s.aabb()):
                    if obb_overlap(s, o):
                        self.errors.append(f"{zid} street overlaps {k}")
        # Buildings vs footprints and each other.
        bh = SpatialHash(80.0)
        for b in self.buildings:
            if b["kind"] in ("pad",):
                continue
            o = b["obb"]
            for k, fo in fh.query(o.aabb()):
                if obb_overlap(o, fo):
                    self.errors.append(f"{b['zone']} {b['kind']} overlaps footprint {k}")
        lot_hash = SpatialHash(80.0)
        for b in self.buildings:
            if b["kind"] != "pad":
                continue
            for other in lot_hash.query(b["lot"].aabb()):
                if obb_overlap(b["lot"].grown(-.05), other.grown(-.05)):
                    self.errors.append(f"lots overlap in {b['zone']}")
                    break
            lot_hash.insert(b["lot"].aabb(), b["lot"])
        for lot in self.oldtown.lots:
            for other in lot_hash.query(lot["obb"].aabb()):
                if obb_overlap(lot["obb"].grown(-.05), other.grown(-.05)):
                    self.errors.append(f"old town lot {lot['id']} overlaps a zone lot")
                    break
        report = self._report()
        return report

    def _grades(self):
        out = {}
        for road in self.roads:
            pts = resample(road["points"], 20.0)
            hs = [self.terrain.surface(*p) for p in pts]
            mx = 0.0
            for i in range(len(pts) - 2):
                L = dist(pts[i], pts[i + 2])
                if L > 0:
                    mx = max(mx, abs(hs[i + 2] - hs[i]) / L)
            out[road["id"]] = round(mx * 100, 2)
        return out

    def _report(self):
        t = self.terrain
        # Terrain statistics on a 100 m lattice.
        x0, z0, x1, z1 = self.world
        hs = []
        for ix in range(80):
            for iz in range(80):
                hs.append(t.surface(x0 + ix * 100 + 50, z0 + iz * 100 + 50))
        city_mean = sum(hs) / len(hs)
        drainage = next(l for l in self.campaign if l["id"] == "drainage")
        dr_h = t.surface(drainage["x"], drainage["z"])
        tech_hs = [t.surface(x, z) for x in range(1000, 3900, 200) for z in range(1200, 3800, 200)]
        old_hs = [t.surface(x, z) for x in range(-3600, -1300, 200) for z in range(-3400, -600, 200)]
        terrain = {"minSurface": round(min(hs), 1), "maxSurface": round(max(hs), 1), "meanSurface": round(city_mean, 1),
                   "drainageSurface": round(dr_h, 1), "drainageToCanalM": round(t.canal_distance(drainage["x"], drainage["z"])),
                   "technologyMean": round(sum(tech_hs) / len(tech_hs), 1), "oldTownMean": round(sum(old_hs) / len(old_hs), 1),
                   "maxRoadGradePct": self._grades()}
        if dr_h > city_mean - 5:
            self.errors.append("drainage pump house is not in a low position")
        if terrain["technologyMean"] < city_mean + 5:
            self.errors.append("technology district is not elevated")
        for rid, g in terrain["maxRoadGradePct"].items():
            lim = 6.0 if rid.startswith(("R01", "R02", "R03", "R04", "R05", "R06", "R09")) else 8.0
            if g > lim:
                self.errors.append(f"road {rid} max grade {g}% above {lim}%")
        # Coverage and skyline per district/zone.
        area = {}
        for did, d in self.districts.items():
            bx0, bz0, bx1, bz1 = d["bounds"]
            area[did] = (bx1 - bx0) * (bz1 - bz0)
        cover, floors_by, counts = {}, {}, {}
        for dname, zid, obb, h, floors, is_main in self.all_building_obbs():
            key = zid if zid.startswith("T_") else dname
            cover[key] = cover.get(key, 0.0) + obb.hw * obb.hd * 4
            counts[key] = counts.get(key, 0) + (1 if is_main else 0)
            if is_main and floors:
                floors_by.setdefault(key, []).append(floors)
        # Campaign massing counts toward coverage of the zone that owns it.
        for loc in self.campaign:
            zk = self.zone_of((loc["x"], loc["z"]))
            zk = zk if zk.startswith("T_") or zk in ("old", "reserve") else loc["district"]
            for v in self.campaign_volumes(loc):
                if v["h"] > 1.5 and v["role"] not in ("yard", "truck_yard") and not v["role"].startswith(("perimeter", "service_tunnel")):
                    cover[zk] = cover.get(zk, 0.0) + v["w"] * v["d"]
        # Owned area per zone measured on a 50 m lattice (zones override nominal district bounds).
        owned = {}
        for ix in range(int(x0), int(x1), 50):
            for iz in range(int(z0), int(z1), 50):
                k = self.zone_of((ix + 25, iz + 25))
                owned[k] = owned.get(k, 0) + 2500
        coverage = {k: round(c / owned[k], 3) for k, c in cover.items() if owned.get(k)}
        skyline = {}
        for k, fl in floors_by.items():
            fl.sort()
            skyline[k] = {"p10": fl[len(fl) // 10], "median": fl[len(fl) // 2], "p90": fl[(len(fl) * 9) // 10], "max": fl[-1], "count": len(fl)}
        for did, (lo, hi) in SKYLINE_TARGETS.items():
            s = skyline.get(did)
            if not s:
                self.errors.append(f"no buildings in {did}")
                continue
            if s["median"] < lo or s["median"] > hi or s["max"] > hi + 2:
                self.errors.append(f"skyline of {did} outside target {lo}-{hi} floors: {s}")
        if coverage.get("industrial", 0) < .2:
            self.errors.append(f"industrial coverage too low: {coverage.get('industrial')}")
        for z in self.zones:
            if counts.get(z["id"], 0) < 25:
                self.errors.append(f"transition zone {z['id']} has only {counts.get(z['id'], 0)} buildings")
        # Cells without urban use (no buildings and no streets).
        used = set()

        def cell(p):
            return (int((p[0] - x0) // 1000), int((p[1] - z0) // 1000))

        for _, _, obb, _, _, _ in self.all_building_obbs():
            used.add(cell(obb.c))
        for zid, edges in self.local_edges.items():
            for a, b, _ in edges:
                used.add(cell(a))
        for road, a, b in self.road_segments():
            used.add(cell(a))
        unused = [f"SA_M{ix:02d}_{iz:02d}" for ix in range(8) for iz in range(8) if (ix, iz) not in used]
        if len(unused) > 5:
            self.errors.append(f"{len(unused)} macro cells without urban use: {unused}")
        # Industrial composition counters.
        ind = {}
        for b in self.buildings:
            if b["district"] == "industrial" and b["kind"] != "pad":
                ind[b["kind"]] = ind.get(b["kind"], 0) + 1
        for c in self.cylinders:
            ind[c["kind"]] = ind.get(c["kind"], 0) + 1
        # Scale: straight-line crossing times with prototype locomotion.
        diag = math.hypot(x1 - x0, z1 - z0)
        scale = {"worldKm": [(x1 - x0) / 1000, (z1 - z0) / 1000], "areaKm2": (x1 - x0) * (z1 - z0) / 1e6,
                 "diagonalKm": round(diag / 1000, 2), "walkAcrossMin": round((x1 - x0) / WALK_MS / 60, 1),
                 "sprintAcrossMin": round((x1 - x0) / SPRINT_MS / 60, 1), "sprintDiagonalMin": round(diag / SPRINT_MS / 60, 1)}
        street_km = {}
        for zid, edges in self.local_edges.items():
            for a, b, cls in edges:
                street_km[cls] = street_km.get(cls, 0) + dist(a, b) / 1000
        for road in self.roads:
            street_km[road["class"] + "_spec"] = street_km.get(road["class"] + "_spec", 0) + polyline_length(road["points"]) / 1000
        return {
            "revision": self.spec.get("revision", "W1"),
            "terrain": terrain,
            "roads": {r["id"]: round(polyline_length(r["points"]) / 1000, 2) for r in self.roads},
            "roundabouts": [r["id"] for r in self.roundabouts],
            "railKm": {r["id"]: round(polyline_length(r["geom"]) / 1000, 2) for r in self.rails},
            "streetKmByClass": {k: round(v, 1) for k, v in sorted(street_km.items())},
            "driveways": len(self.driveways),
            "access": self.access,
            "buildingsByZone": dict(sorted(counts.items())),
            "coverage": dict(sorted(coverage.items())),
            "skylineFloors": dict(sorted(skyline.items())),
            "industrialComposition": dict(sorted(ind.items())),
            "trees": len(self.trees),
            "unusedMacroCells": unused,
            "oldTown": self.oldtown.metrics,
            "scale": scale,
        }
