"""Urban fabric generation shared by the Old Town and the whole masterplan (pure Python).

- Building family catalogue (Old Town production families + generic district massing families).
- Organic street grid generator (variable block sizes, rotation, domain warp, seam stitching).
- Street graph utilities (split at crossings, removals, alleys, connectivity pruning).
- Frontage lot packing: buildings line the streets, attached where the family is attached,
  back-to-back conflicts leave courtyards and "fundos" naturally.
- Industrial lot composer (sheds, docks, yards, tanks, silos, substations, chimneys).
"""
import math

from sa_geom import (OBB, Noise2, SpatialHash, dist, lerp, norm, obb_overlap, perp, point_seg, seg_intersection,
                     segment_obb, sub)

# Street cross-sections: total corridor width and sidewalk width per side (metres).
STREET = {
    "arterial": {"total": 30.0, "sidewalk": 3.0},
    "collector": {"total": 18.0, "sidewalk": 3.0},
    "main": {"total": 16.0, "sidewalk": 3.0},
    "local": {"total": 12.0, "sidewalk": 2.5},
    "industrial": {"total": 16.0, "sidewalk": 2.0},
    "alley": {"total": 5.0, "sidewalk": 0.0},
    "passage": {"total": 3.0, "sidewalk": 0.0},
    "service": {"total": 7.0, "sidewalk": 0.0},
}


def carriageway(cls):
    s = STREET[cls]
    return s["total"] - 2 * s["sidewalk"]


# ---------------------------------------------------------------- families

def _v(fid, fam, w, d, floors, fh, roof, setback=0.0, attached=True, ground_h=None, tags=()):
    h = (ground_h or fh) + fh * (floors - 1)
    return {"id": fid, "family": fam, "w": float(w), "d": float(d), "floors": floors, "fh": fh,
            "ground_h": ground_h or fh, "roof": roof, "setback": setback, "attached": attached,
            "height": round(h, 2), "tags": list(tags)}


# Old Town production families (each variant becomes a detailed reusable mesh in Blender).
OLDTOWN_VARIANTS = [
    _v("sob_a", "sobrado_estreito", 5.0, 12.0, 2, 3.0, "gable_side"),
    _v("sob_b", "sobrado_estreito", 6.0, 14.0, 2, 3.0, "gable_side"),
    _v("sob_c", "sobrado_estreito", 7.0, 15.0, 2, 3.0, "gable_front"),
    _v("sob_d", "sobrado_estreito", 6.0, 12.0, 3, 3.0, "flat_parapet"),
    _v("sob_e", "sobrado_estreito", 5.5, 16.0, 2, 3.0, "gable_side"),
    _v("cas_a", "casa_terrea", 8.0, 10.0, 1, 3.0, "hip", setback=4.0, attached=False),
    _v("cas_b", "casa_terrea", 9.0, 12.0, 1, 3.0, "gable_side", setback=3.0, attached=False),
    _v("cas_c", "casa_terrea", 10.0, 11.0, 1, 3.0, "hip", setback=5.0, attached=False),
    _v("cas_d", "casa_terrea", 12.0, 13.0, 1, 3.0, "gable_front", setback=4.0, attached=False),
    _v("cas_e", "casa_terrea", 8.5, 14.0, 1, 3.0, "gable_side", setback=2.0, attached=False),
    _v("cr_a", "comercio_residencia", 7.0, 15.0, 2, 3.0, "flat_parapet", ground_h=4.0, tags=("shop",)),
    _v("cr_b", "comercio_residencia", 8.0, 16.0, 2, 3.0, "gable_side", ground_h=4.0, tags=("shop",)),
    _v("cr_c", "comercio_residencia", 9.0, 18.0, 3, 3.0, "flat_parapet", ground_h=4.2, tags=("shop",)),
    _v("cr_d", "comercio_residencia", 10.0, 20.0, 2, 3.0, "flat_parapet", ground_h=4.2, tags=("shop",)),
    _v("cr_e", "comercio_residencia", 8.0, 14.0, 3, 3.0, "gable_side", ground_h=4.0, tags=("shop",)),
    _v("p3_a", "predio_3pav", 10.0, 15.0, 3, 3.0, "flat_parapet"),
    _v("p3_b", "predio_3pav", 12.0, 18.0, 3, 3.0, "flat_parapet"),
    _v("p3_c", "predio_3pav", 14.0, 20.0, 3, 3.0, "hip"),
    _v("p3_d", "predio_3pav", 11.0, 16.0, 3, 3.0, "flat_parapet", ground_h=4.0, tags=("shop",)),
    _v("p46_a", "predio_4a6", 12.0, 18.0, 4, 2.9, "flat_parapet"),
    _v("p46_b", "predio_4a6", 14.0, 20.0, 5, 2.9, "flat_parapet", ground_h=4.0, tags=("shop",)),
    _v("p46_c", "predio_4a6", 16.0, 22.0, 6, 2.9, "flat_parapet"),
    _v("p46_d", "predio_4a6", 18.0, 24.0, 5, 2.9, "flat_parapet", ground_h=4.2, tags=("shop",)),
    _v("p46_e", "predio_4a6", 13.0, 18.0, 4, 2.9, "hip"),
    _v("ofi_a", "oficina", 10.0, 22.0, 1, 5.5, "shed_metal", tags=("big_door",)),
    _v("ofi_b", "oficina", 12.0, 26.0, 1, 5.5, "gable_metal", tags=("big_door",)),
    _v("ofi_c", "oficina", 14.0, 28.0, 1, 6.0, "sawtooth", tags=("big_door",)),
    _v("ofi_d", "oficina", 16.0, 30.0, 1, 6.0, "gable_metal", setback=3.0, tags=("big_door", "yard")),
    _v("arm_a", "armazem", 16.0, 28.0, 1, 7.5, "gable_brick", tags=("big_door", "rail")),
    _v("arm_b", "armazem", 20.0, 32.0, 1, 8.0, "gable_brick", tags=("big_door", "rail")),
    _v("arm_c", "armazem", 24.0, 36.0, 1, 8.5, "barrel", tags=("big_door", "rail")),
    _v("arm_d", "armazem", 30.0, 40.0, 1, 9.0, "gable_brick", tags=("big_door", "rail")),
    _v("dep_a", "deposito", 12.0, 16.0, 1, 5.0, "flat_parapet", tags=("big_door",)),
    _v("dep_b", "deposito", 14.0, 20.0, 1, 5.5, "shed_metal", tags=("big_door",)),
    _v("dep_c", "deposito", 18.0, 24.0, 1, 6.0, "gable_metal", tags=("big_door",)),
    _v("dep_d", "deposito", 20.0, 22.0, 1, 5.5, "flat_parapet", tags=("big_door",)),
    _v("pc_a", "pequeno_comercial", 12.0, 16.0, 2, 3.4, "flat_parapet", ground_h=4.0, tags=("shop",)),
    _v("pc_b", "pequeno_comercial", 14.0, 18.0, 3, 3.3, "flat_parapet", ground_h=4.0, tags=("shop",)),
    _v("pc_c", "pequeno_comercial", 16.0, 18.0, 2, 3.4, "flat_parapet", ground_h=4.2, tags=("shop",)),
    _v("pc_d", "pequeno_comercial", 18.0, 20.0, 3, 3.3, "flat_parapet", ground_h=4.2, tags=("shop",)),
    _v("ab_a", "abandonada_reformada", 8.0, 15.0, 2, 3.0, "roofless", tags=("abandoned", "shop")),
    _v("ab_b", "abandonada_reformada", 12.0, 18.0, 3, 3.0, "flat_parapet", tags=("abandoned",)),
    _v("ab_c", "abandonada_reformada", 6.0, 14.0, 2, 3.0, "roofless", tags=("abandoned",)),
    _v("ab_d", "abandonada_reformada", 16.0, 24.0, 1, 6.5, "gable_metal_broken", tags=("abandoned", "big_door")),
    _v("ab_e", "abandonada_reformada", 10.0, 16.0, 3, 3.0, "flat_parapet", tags=("renovation", "scaffold")),
]
OLDTOWN_BY_ID = {v["id"]: v for v in OLDTOWN_VARIANTS}
OLDTOWN_FAMILIES = sorted({v["family"] for v in OLDTOWN_VARIANTS})

# Old Town neighbourhood characters: family weights.
CHARACTER = {
    "core_rail":   {"comercio_residencia": 28, "sobrado_estreito": 24, "predio_3pav": 14, "armazem": 14, "deposito": 6, "oficina": 6, "abandonada_reformada": 8},
    "core_mixed":  {"comercio_residencia": 26, "sobrado_estreito": 20, "predio_3pav": 18, "predio_4a6": 14, "pequeno_comercial": 10, "casa_terrea": 6, "abandonada_reformada": 6},
    "core_stately": {"predio_3pav": 24, "predio_4a6": 24, "comercio_residencia": 20, "pequeno_comercial": 16, "sobrado_estreito": 10, "abandonada_reformada": 6},
    "workshops":   {"oficina": 30, "deposito": 18, "casa_terrea": 20, "sobrado_estreito": 10, "armazem": 10, "abandonada_reformada": 12},
    "residential_low": {"casa_terrea": 48, "sobrado_estreito": 26, "comercio_residencia": 10, "predio_3pav": 10, "abandonada_reformada": 6},
    "mixed_low":   {"casa_terrea": 34, "sobrado_estreito": 20, "comercio_residencia": 16, "oficina": 10, "predio_3pav": 10, "deposito": 4, "abandonada_reformada": 6},
    "depots":      {"armazem": 30, "deposito": 34, "oficina": 20, "casa_terrea": 6, "abandonada_reformada": 10},
    "transition_mixed": {"casa_terrea": 24, "predio_3pav": 16, "predio_4a6": 14, "comercio_residencia": 16, "oficina": 10, "pequeno_comercial": 12, "deposito": 4, "sobrado_estreito": 4},
}
MAIN_STREET_BIAS = {"comercio_residencia": 2.2, "pequeno_comercial": 1.8, "predio_4a6": 1.6, "predio_3pav": 1.3, "casa_terrea": .45, "oficina": .6, "deposito": .4}


def _g(fid, fam, w, d, floors, fh, podium=None, setback=4.0, attached=False, tags=()):
    return {"id": fid, "family": fam, "w": w, "d": d, "floors": floors, "fh": fh, "podium": podium,
            "setback": setback, "attached": attached, "tags": list(tags)}


# Generic district massing families: w/d/floors are (min, max) ranges sampled per lot.
GENERIC = {
    "house_low": _g("house_low", "house_low", (10, 14), (12, 16), (1, 2), 3.0, setback=4.0),
    "row_mixed": _g("row_mixed", "row_mixed", (8, 14), (14, 20), (2, 4), 3.1, setback=0.0, attached=True),
    "shop_row": _g("shop_row", "shop_row", (12, 22), (15, 22), (1, 2), 4.0, setback=0.0, attached=True),
    "mid_res": _g("mid_res", "mid_res", (20, 32), (14, 18), (4, 8), 3.0, setback=5.0),
    "condo_slab": _g("condo_slab", "condo_slab", (30, 46), (14, 18), (8, 16), 3.0, podium=(1, 4.0), setback=8.0),
    "tower_res": _g("tower_res", "tower_res", (22, 28), (22, 28), (10, 16), 3.0, podium=(1, 4.0), setback=8.0),
    "office_mid": _g("office_mid", "office_mid", (26, 40), (20, 30), (6, 12), 3.6, setback=6.0),
    "office_tower": _g("office_tower", "office_tower", (30, 40), (30, 40), (10, 33), 3.8, podium=(2, 5.0), setback=8.0),
    "institutional": _g("institutional", "institutional", (32, 60), (25, 40), (3, 6), 4.0, setback=8.0),
    "campus_lab": _g("campus_lab", "campus_lab", (40, 70), (30, 50), (2, 5), 4.2, setback=12.0),
    "campus_tower": _g("campus_tower", "campus_tower", (28, 36), (28, 36), (8, 28), 3.8, podium=(1, 5.0), setback=12.0),
    "depot": _g("depot", "depot", (20, 40), (25, 45), (1, 1), 7.5, setback=6.0, tags=("big_door",)),
    "service_shed": _g("service_shed", "service_shed", (15, 30), (15, 30), (1, 1), 5.5, setback=4.0),
    "parking_lot": _g("parking_lot", "parking_lot", (30, 50), (30, 42), (0, 0), 0.0, setback=2.0, tags=("open", "parking")),
    "green": _g("green", "green", (40, 80), (30, 60), (0, 0), 0.0, setback=4.0, tags=("open", "green")),
    "vacant": _g("vacant", "vacant", (20, 40), (20, 40), (0, 0), 0.0, setback=2.0, tags=("open", "vacant")),
    "sports": _g("sports", "sports", (110, 110), (72, 72), (0, 0), 0.0, setback=6.0, tags=("open", "sports")),
    "industrial_lot": _g("industrial_lot", "industrial_lot", (70, 150), (80, 150), (1, 1), 10.0, setback=6.0, tags=("composite", "tight")),
    "small_factory": _g("small_factory", "small_factory", (30, 55), (35, 60), (1, 1), 8.0, setback=4.0, tags=("composite", "tight")),
}

PROFILES = {
    # spacing (min,max), orientation deg, warp amplitude m, warp wavelength m, families weights, street class, vacancy
    "services_depots": {"spacing": (120, 190), "orient": 6, "warp": 10, "wl": 500, "street": "local",
                        "fam": {"depot": 22, "service_shed": 22, "house_low": 18, "row_mixed": 8, "vacant": 10, "parking_lot": 6, "small_factory": 8, "green": 6}},
    "institutional": {"spacing": (130, 200), "orient": 0, "warp": 6, "wl": 700, "street": "local",
                      "fam": {"institutional": 34, "office_mid": 14, "shop_row": 16, "mid_res": 10, "green": 14, "parking_lot": 8, "row_mixed": 4}},
    "offices_mid": {"spacing": (120, 180), "orient": -4, "warp": 5, "wl": 700, "street": "local",
                    "fam": {"office_mid": 40, "parking_lot": 16, "shop_row": 14, "mid_res": 12, "institutional": 8, "green": 6, "office_tower": 4}},
    "campus": {"spacing": (180, 260), "orient": 8, "warp": 14, "wl": 900, "street": "local",
               "fam": {"campus_lab": 30, "campus_tower": 14, "parking_lot": 18, "green": 28, "office_mid": 10}},
    "canal_valley": {"spacing": (170, 260), "orient": -10, "warp": 12, "wl": 700, "street": "local",
                     "fam": {"green": 30, "sports": 10, "depot": 16, "service_shed": 14, "house_low": 14, "vacant": 10, "parking_lot": 6}},
    "residential_mid": {"spacing": (140, 220), "orient": 3, "warp": 8, "wl": 800, "street": "local",
                        "fam": {"condo_slab": 22, "mid_res": 24, "tower_res": 10, "shop_row": 14, "house_low": 12, "parking_lot": 8, "green": 10}},
    "transition_mixed": {"spacing": (110, 170), "orient": 2, "warp": 12, "wl": 500, "street": "local",
                         "fam": {"house_low": 26, "row_mixed": 22, "shop_row": 14, "mid_res": 12, "service_shed": 10, "depot": 6, "vacant": 6, "parking_lot": 4}},
    "expansion": {"spacing": (150, 240), "orient": 0, "warp": 6, "wl": 900, "street": "local",
                  "fam": {"condo_slab": 24, "mid_res": 26, "tower_res": 10, "house_low": 12, "shop_row": 12, "parking_lot": 6, "green": 10}},
    "civic": {"spacing": (130, 200), "orient": 0, "warp": 4, "wl": 900, "street": "local",
              "fam": {"institutional": 36, "office_mid": 18, "shop_row": 12, "green": 18, "parking_lot": 10, "mid_res": 6}},
    "corporate": {"spacing": (120, 190), "orient": -3, "warp": 4, "wl": 900, "street": "local",
                  "fam": {"office_tower": 62, "office_mid": 12, "parking_lot": 12, "green": 8, "tower_res": 6}},
    "industrial": {"spacing": (170, 260), "orient": 3, "warp": 8, "wl": 1200, "street": "industrial",
                   "fam": {"industrial_lot": 44, "small_factory": 30, "depot": 16, "service_shed": 8, "parking_lot": 2}},
    "technology": {"spacing": (180, 280), "orient": 10, "warp": 12, "wl": 1000, "street": "local",
                   "fam": {"campus_tower": 26, "campus_lab": 30, "green": 24, "parking_lot": 14, "office_mid": 6}},
}

# Height targets per district (floors) — used by validation of the skyline.
SKYLINE_TARGETS = {"old": (2, 6), "expansion": (4, 16), "civic": (3, 10), "corporate": (12, 35), "technology": (8, 28), "industrial": (1, 3)}


def pick(rng, weights):
    total = sum(weights.values())
    r = rng.uniform(0, total)
    acc = 0.0
    for k, w in weights.items():
        acc += w
        if r <= acc:
            return k
    return k


# ---------------------------------------------------------------- street graph

class StreetGraph:
    """Undirected street graph. Nodes are 2D points; edges carry class, name and a polyline of two points."""

    def __init__(self):
        self.nodes = {}       # nid -> (x, z)
        self.edges = {}       # eid -> dict(a, b, cls, name, zone)
        self._nid = 0
        self._eid = 0
        self._index = {}

    def node(self, p, snap=0.5):
        key = (round(p[0] / snap), round(p[1] / snap))
        nid = self._index.get(key)
        if nid is None:
            nid = self._nid
            self._nid += 1
            self.nodes[nid] = (float(p[0]), float(p[1]))
            self._index[key] = nid
        return nid

    def add_edge(self, a, b, cls, name="", zone="", **extra):
        if a == b:
            return None
        eid = self._eid
        self._eid += 1
        self.edges[eid] = {"a": a, "b": b, "cls": cls, "name": name, "zone": zone, **extra}
        return eid

    def add_polyline(self, pts, cls, name="", zone="", **extra):
        ids = [self.node(p) for p in pts]
        out = []
        for a, b in zip(ids, ids[1:]):
            e = self.add_edge(a, b, cls, name, zone, **extra)
            if e is not None:
                out.append(e)
        return out

    def seg(self, eid):
        e = self.edges[eid]
        return self.nodes[e["a"]], self.nodes[e["b"]]

    def degree(self):
        deg = {n: 0 for n in self.nodes}
        for e in self.edges.values():
            deg[e["a"]] += 1
            deg[e["b"]] += 1
        return deg

    def incident(self):
        inc = {n: [] for n in self.nodes}
        for eid, e in self.edges.items():
            inc[e["a"]].append(eid)
            inc[e["b"]].append(eid)
        return inc

    def remove(self, eids):
        for eid in eids:
            self.edges.pop(eid, None)

    def edge_hash(self, cell=120.0):
        h = SpatialHash(cell)
        for eid in self.edges:
            a, b = self.seg(eid)
            h.insert((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), eid)
        return h

    def split_crossings(self, priority_classes):
        """Split every edge crossing an edge of a priority class at the crossing point (creates real junctions)."""
        pri = [eid for eid, e in self.edges.items() if e["cls"] in priority_classes]
        h = self.edge_hash()
        cuts = {}
        for pe in pri:
            a, b = self.seg(pe)
            aabb = (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))
            for oe in h.query(aabb):
                if oe == pe or oe not in self.edges:
                    continue
                c, d = self.seg(oe)
                hit = seg_intersection(a, b, c, d)
                if not hit:
                    continue
                p, t, u = hit
                if min(t, 1 - t) * dist(a, b) < 1.0 or min(u, 1 - u) * dist(c, d) < 1.0:
                    continue
                cuts.setdefault(pe, []).append((t, p))
                cuts.setdefault(oe, []).append((u, p))
        for eid, lst in cuts.items():
            if eid not in self.edges:
                continue
            e = self.edges.pop(eid)
            lst.sort()
            chain = [e["a"]] + [self.node(p) for _, p in lst] + [e["b"]]
            for n0, n1 in zip(chain, chain[1:]):
                extra = {k: v for k, v in e.items() if k not in ("a", "b", "cls", "name", "zone")}
                self.add_edge(n0, n1, e["cls"], e["name"], e["zone"], **extra)

    def prune_to(self, keep_classes):
        """Keep only components that contain at least one edge of keep_classes."""
        parent = {}

        def find(k):
            while parent.setdefault(k, k) != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k

        for e in self.edges.values():
            parent[find(e["a"])] = find(e["b"])
        good = {find(e["a"]) for e in self.edges.values() if e["cls"] in keep_classes}
        drop = [eid for eid, e in self.edges.items() if find(e["a"]) not in good]
        self.remove(drop)
        used = {e["a"] for e in self.edges.values()} | {e["b"] for e in self.edges.values()}
        for n in list(self.nodes):
            if n not in used:
                del self.nodes[n]
        self._index = {k: v for k, v in self._index.items() if v in self.nodes}
        return len(drop)


def organic_grid(graph, region, origin, orient_deg, spacing, warp_amp, warp_wl, rng, cls="local", zone="", extent=None):
    """Variable-spacing rotated grid with domain warping, clipped to region(p) -> bool.

    extent: (half_u, half_v) of the generated grid around origin.
    Returns the list of created edge ids.
    """
    th = math.radians(orient_deg)
    u = (math.cos(th), math.sin(th))
    v = (-math.sin(th), math.cos(th))
    hu, hv = extent

    def ticks(half):
        out = [0.0]
        t = 0.0
        while t < half:
            t += rng.uniform(*spacing)
            out.append(t)
        t = 0.0
        while t > -half:
            t -= rng.uniform(*spacing)
            out.append(t)
        return sorted(out)

    us, vs = ticks(hu), ticks(hv)
    nx, nz = Noise2(rng, warp_wl, 2), Noise2(rng, warp_wl, 2)
    pts = {}
    for i, a in enumerate(us):
        for j, b in enumerate(vs):
            p = (origin[0] + u[0] * a + v[0] * b, origin[1] + u[1] * a + v[1] * b)
            p = (p[0] + warp_amp * nx(*p), p[1] + warp_amp * nz(*p))
            pts[(i, j)] = p
    # Sub-divide each grid edge into short pieces (keeps curvature of the warp and lets obstacles cut locally).
    created = []
    for (i, j), p in pts.items():
        for di, dj in ((1, 0), (0, 1)):
            q = pts.get((i + di, j + dj))
            if q is None:
                continue
            L = dist(p, q)
            n = max(1, int(L // 45))
            chain = []
            for k in range(n + 1):
                t = k / n
                base_u = us[i] + (us[i + di] - us[i]) * t if di else us[i]
                base_v = vs[j] + (vs[j + dj] - vs[j]) * t if dj else vs[j]
                bp = (origin[0] + u[0] * base_u + v[0] * base_v, origin[1] + u[1] * base_u + v[1] * base_v)
                chain.append((bp[0] + warp_amp * nx(*bp), bp[1] + warp_amp * nz(*bp)))
            if not all(region(c) for c in chain):
                continue
            created += graph.add_polyline(chain, cls, zone=zone, grid=(i, j, di, dj))
    return created


def remove_near_parallel(graph, guide_eids, reach, max_angle_deg, classes):
    """Remove edges of the given classes that run almost parallel and close to guide edges (avoids doubled streets)."""
    cos_lim = math.cos(math.radians(max_angle_deg))
    h = graph.edge_hash()
    drop = set()
    for ge in guide_eids:
        if ge not in graph.edges:
            continue
        a, b = graph.seg(ge)
        gd = norm(sub(b, a))
        aabb = (min(a[0], b[0]) - reach, min(a[1], b[1]) - reach, max(a[0], b[0]) + reach, max(a[1], b[1]) + reach)
        for oe in h.query(aabb):
            if oe in drop or oe == ge or oe not in graph.edges or graph.edges[oe]["cls"] not in classes:
                continue
            c, d = graph.seg(oe)
            mid = lerp(c, d, .5)
            if point_seg(mid, a, b)[0] > reach:
                continue
            od = norm(sub(d, c))
            if abs(gd[0] * od[0] + gd[1] * od[1]) >= cos_lim:
                drop.add(oe)
    graph.remove(drop)
    return len(drop)


def remove_hitting(graph, obbs, classes, pad=0.0):
    h = SpatialHash(100.0)
    for o in obbs:
        h.insert(o.aabb(), o)
    drop = []
    for eid, e in graph.edges.items():
        if e["cls"] not in classes:
            continue
        a, b = graph.seg(eid)
        s = segment_obb(a, b, STREET[e["cls"]]["total"] + 2 * pad)
        for o in h.query(s.aabb()):
            if obb_overlap(s, o):
                drop.append(eid)
                break
    graph.remove(drop)
    return len(drop)


def stitch_dead_ends(graph, max_len, rng, cls="local", zone_of=None, obstacles=()):
    """Connect dangling nodes to a nearby node of another zone/street when it does not cross anything."""
    deg = graph.degree()
    h = graph.edge_hash()
    nh = SpatialHash(max_len)
    for n, p in graph.nodes.items():
        nh.insert((p[0], p[1], p[0], p[1]), n)
    obh = SpatialHash(100.0)
    for o in obstacles:
        obh.insert(o.aabb(), o)
    added = 0
    for n, d in list(deg.items()):
        if d != 1 or n not in graph.nodes:
            continue
        p = graph.nodes[n]
        best = None
        for m in nh.query((p[0] - max_len, p[1] - max_len, p[0] + max_len, p[1] + max_len)):
            if m == n:
                continue
            q = graph.nodes[m]
            L = dist(p, q)
            if L < 8 or L > max_len:
                continue
            if zone_of and zone_of(n) == zone_of(m) and deg.get(m, 0) >= 2:
                continue
            if best is None or L < best[0]:
                best = (L, m)
        if not best:
            continue
        q = graph.nodes[best[1]]
        ok = True
        aabb = (min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1]))
        for oe in h.query(aabb):
            if oe not in graph.edges:
                continue
            e = graph.edges[oe]
            if n in (e["a"], e["b"]) or best[1] in (e["a"], e["b"]):
                continue
            c, dd = graph.seg(oe)
            if seg_intersection(p, q, c, dd):
                ok = False
                break
        if ok:
            s = segment_obb(p, q, STREET[cls]["total"])
            for o in obh.query(s.aabb()):
                if obb_overlap(s, o):
                    ok = False
                    break
        if ok:
            graph.add_edge(n, best[1], cls, zone=(zone_of(n) if zone_of else ""), stitched=True)
            deg[n] += 1
            deg[best[1]] = deg.get(best[1], 0) + 1
            added += 1
    return added


# ---------------------------------------------------------------- frontage lot packing

class LotPacker:
    """Places oriented lots along street edges without overlaps (obstacles + previously placed lots)."""

    def __init__(self, graph, rng, cell=60.0):
        self.graph = graph
        self.rng = rng
        self.hash = SpatialHash(cell)
        self.lots = []
        self.deg = graph.degree()
        self.inc = graph.incident()

    def block(self, obb, tag="obstacle"):
        self.hash.insert(obb.aabb(), (obb, tag))

    def block_streets(self, extra_pad=0.0):
        for eid, e in self.graph.edges.items():
            a, b = self.graph.seg(eid)
            self.block(segment_obb(a, b, STREET[e["cls"]]["total"] + 2 * extra_pad), "street")
        # Junction pads so corner lots keep clear of intersections.
        for n, p in self.graph.nodes.items():
            if self.deg.get(n, 0) >= 3:
                r = max(STREET[self.graph.edges[e]["cls"]]["total"] for e in self.inc[n]) * .5 + 1.5
                self.block(OBB(p, (1.0, 0.0), r, r), "junction")

    def free(self, obb):
        for other, _tag in self.hash.query(obb.aabb()):
            if obb_overlap(obb, other):
                return False
        return True

    def end_clear(self, nid, eid):
        if self.deg.get(nid, 0) <= 1:
            return 2.0
        if self.deg.get(nid, 0) == 2:
            return 0.3  # street continues: no corner here
        widest = max((STREET[self.graph.edges[e]["cls"]]["total"] for e in self.inc[nid] if e != eid), default=8.0)
        return widest * .5 + 2.0

    def chains(self, classes):
        """Maximal street runs through degree-2 nodes of the same class: [(node_ids, edge_ids, cls, name)]."""
        g = self.graph
        seen = set()
        out = []
        for eid, e in g.edges.items():
            if eid in seen or e["cls"] not in classes:
                continue
            seen.add(eid)
            nodes = [e["a"], e["b"]]
            eids = [eid]
            for forward in (True, False):
                while True:
                    end = nodes[-1] if forward else nodes[0]
                    if self.deg.get(end, 0) != 2:
                        break
                    nxt = [x for x in self.inc[end] if x not in seen and g.edges[x]["cls"] == e["cls"]]
                    if not nxt:
                        break
                    x = nxt[0]
                    seen.add(x)
                    ex = g.edges[x]
                    other = ex["b"] if ex["a"] == end else ex["a"]
                    if forward:
                        nodes.append(other)
                        eids.append(x)
                    else:
                        nodes.insert(0, other)
                        eids.insert(0, x)
            out.append((nodes, eids, e["cls"], e.get("name", "")))
        return out

    def pack_chain(self, chain, choose, sides=(1, -1), meta=None):
        """Pack lots along a whole street run. choose(side, point, edge_dict) -> spec or None."""
        nodes, eids, cls, name = chain
        g = self.graph
        pts = [g.nodes[n] for n in nodes]
        cum = [0.0]
        for a, b in zip(pts, pts[1:]):
            cum.append(cum[-1] + dist(a, b))
        L = cum[-1]
        if L < 6:
            return 0

        def at(s):
            s = max(0.0, min(L, s))
            for i in range(len(cum) - 1):
                if cum[i + 1] >= s:
                    seg = cum[i + 1] - cum[i]
                    return lerp(pts[i], pts[i + 1], (s - cum[i]) / seg if seg else 0.0)
            return pts[-1]

        half = STREET[cls]["total"] / 2
        start = self.end_clear(nodes[0], eids[0])
        stop = L - self.end_clear(nodes[-1], eids[-1])
        edge = {"cls": cls, "name": name, "a": nodes[0], "b": nodes[-1]}
        placed = 0
        for side in sides:
            t = start + self.rng.uniform(0, 2.0)
            fails = 0
            while t < stop - 3:
                p0 = at(t)
                spec = choose(side, p0, edge)
                if spec is None:
                    t += 6
                    continue
                w, d = spec["w"], spec["d"]
                if t + w > stop:
                    fails += 1
                    if fails > 3:
                        break
                    continue
                p1 = at(t + w)
                pm = at(t + w / 2)
                u = norm(sub(p1, p0))
                n = perp(u)
                n = (n[0] * side, n[1] * side)
                # Chord midpoint can sit inside a curve: start the lot from the curve point itself.
                base = pm
                off = half + 0.4 + spec.get("setback", 0.0) + d / 2
                c = (base[0] + n[0] * off, base[1] + n[1] * off)
                obb = OBB(c, (-n[1], n[0]), w / 2, d / 2)
                if not self.free(obb.grown(-0.01)):
                    ok = False
                    if spec.get("shrinkable", True):
                        for frac in (.8, .65):
                            d2 = d * frac
                            if d2 < spec.get("min_d", d * .6):
                                break
                            off2 = half + 0.4 + spec.get("setback", 0.0) + d2 / 2
                            obb2 = OBB((base[0] + n[0] * off2, base[1] + n[1] * off2), (-n[1], n[0]), w / 2, d2 / 2)
                            if self.free(obb2.grown(-0.01)):
                                obb, d, ok = obb2, d2, True
                                break
                    if not ok:
                        t += 3.0
                        continue
                lot = dict(spec)
                lot.update({"obb": obb, "d": d, "street": eids[0], "street_cls": cls, "street_name": name,
                            "rot": math.atan2(-n[0], n[1]), "front": (base[0] + n[0] * half, base[1] + n[1] * half)})
                if meta:
                    lot.update(meta)
                self.lots.append(lot)
                self.block(obb, "lot")
                placed += 1
                t += w + spec.get("gap", 0.0)
        return placed

    def pack_edge(self, eid, choose, sides=(1, -1), meta=None):
        """choose(side, along_t, edge) -> spec dict with w, d, setback, gap, plus anything to store; or None to skip."""
        e = self.graph.edges[eid]
        a, b = self.graph.seg(eid)
        L = dist(a, b)
        if L < 6:
            return 0
        u = norm(sub(b, a))
        n0 = perp(u)
        half = STREET[e["cls"]]["total"] / 2
        start = self.end_clear(e["a"], eid)
        stop = L - self.end_clear(e["b"], eid)
        placed = 0
        for side in sides:
            n = (n0[0] * side, n0[1] * side)
            t = start + self.rng.uniform(0, 2.0)
            fails = 0
            while t < stop - 3:
                spec = choose(side, t / L, e)
                if spec is None:
                    t += 6
                    continue
                w, d = spec["w"], spec["d"]
                if t + w > stop:
                    fails += 1
                    if fails > 3:
                        break
                    continue
                along = t + w / 2
                off = half + 0.4 + spec.get("setback", 0.0) + d / 2
                c = (a[0] + u[0] * along + n[0] * off, a[1] + u[1] * along + n[1] * off)
                # Lot axis u_l runs along the street; depth axis points away from the street (n).
                obb = OBB(c, (-n[1], n[0]), w / 2, d / 2)
                # Shrink the depth if a conflict is only at the back (creates shallower lots near corners).
                if not self.free(obb.grown(-0.01)):
                    ok = False
                    for frac in (.8, .65):
                        d2 = d * frac
                        if d2 < spec.get("min_d", d * .6):
                            break
                        off2 = half + 0.4 + spec.get("setback", 0.0) + d2 / 2
                        c2 = (a[0] + u[0] * along + n[0] * off2, a[1] + u[1] * along + n[1] * off2)
                        obb2 = OBB(c2, (-n[1], n[0]), w / 2, d2 / 2)
                        if self.free(obb2.grown(-0.01)) and spec.get("shrinkable", True):
                            obb, d, ok = obb2, d2, True
                            break
                    if not ok:
                        t += 3.0
                        continue
                lot = dict(spec)
                lot.update({"obb": obb, "d": d, "street": eid, "street_cls": e["cls"], "street_name": e.get("name", ""),
                            "rot": math.atan2(-n[0], n[1]), "front": (a[0] + u[0] * along + n[0] * half, a[1] + u[1] * along + n[1] * half)})
                if meta:
                    lot.update(meta)
                self.lots.append(lot)
                self.block(obb, "lot")
                placed += 1
                t += w + spec.get("gap", 0.0)
        return placed


# ---------------------------------------------------------------- industrial composer

def compose_industrial(lot, rng):
    """Turn an industrial lot OBB into several volumes. Returns list of dicts (kind, obb|centre, sizes, h)."""
    obb = lot["obb"]
    W, D = obb.hw * 2, obb.hd * 2
    u, v, c = obb.u, obb.v, obb.c

    def at(du, dv):
        return (c[0] + u[0] * du + v[0] * dv, c[1] + u[1] * du + v[1] * dv)

    parts = []
    yard_d = D * rng.uniform(.22, .34)
    shed_w = W * rng.uniform(.62, .86)
    shed_d = (D - yard_d) * rng.uniform(.78, .95)
    shed_du = rng.uniform(-(W - shed_w) / 2, (W - shed_w) / 2)
    shed_dv = -D / 2 + yard_d + shed_d / 2  # front of lot is at -v (street side)
    shed_h = rng.uniform(8.0, 14.0) if lot["family"] == "industrial_lot" else rng.uniform(6.5, 9.5)
    parts.append({"kind": "shed", "obb": OBB(at(shed_du, shed_dv), u, shed_w / 2, shed_d / 2), "h": shed_h,
                  "roof": rng.choice(["gable_metal", "sawtooth", "flat", "barrel"])})
    # Paved yard in front of the shed.
    parts.append({"kind": "yard", "obb": OBB(at(0, -D / 2 + yard_d / 2), u, W / 2 - 1, yard_d / 2 - 1), "h": 0.15})
    # Docks along the shed front.
    ndock = max(2, int(shed_w // 9)) if lot["family"] == "industrial_lot" else max(1, int(shed_w // 12))
    for k in range(ndock):
        du = shed_du - shed_w / 2 + (k + .5) * shed_w / ndock
        parts.append({"kind": "dock", "obb": OBB(at(du, shed_dv - shed_d / 2 - 1.2), u, 1.9, 1.2), "h": 1.2})
    # Office annex at a front corner.
    side = rng.choice((-1, 1))
    ow, od = rng.uniform(10, 18), rng.uniform(8, 12)
    parts.append({"kind": "office", "obb": OBB(at(side * (W / 2 - ow / 2 - 2), -D / 2 + yard_d * .45), u, ow / 2, od / 2),
                  "h": rng.choice([7.0, 10.5])})
    rest_du = -side * (W / 2 - 14)
    if rng.random() < .45:
        r = rng.uniform(4.0, 8.0)
        for k in range(rng.randint(1, 3)):
            parts.append({"kind": "tank", "centre": at(rest_du - side * k * (2 * r + 3), -D / 2 + yard_d * .5), "r": r,
                          "h": rng.uniform(7, 15)})
    if rng.random() < .22:
        r = rng.uniform(2.6, 3.8)
        for k in range(rng.randint(3, 6)):
            parts.append({"kind": "silo", "centre": at(shed_du + shed_w / 2 + r + 3, shed_dv - shed_d / 2 + r + k * (2 * r + .6)),
                          "r": r, "h": rng.uniform(18, 30)})
    if rng.random() < .2:
        parts.append({"kind": "substation", "obb": OBB(at(-side * (W / 2 - 12), -D / 2 + yard_d * .5), u, 9, 7), "h": 4.0})
    if rng.random() < .14:
        parts.append({"kind": "chimney", "centre": at(shed_du + shed_w * .3, shed_dv + shed_d * .3), "r": 1.6, "h": rng.uniform(30, 52)})
    if rng.random() < .35:
        parts.append({"kind": "truck_parking", "obb": OBB(at(0, -D / 2 + yard_d * .5), u, min(W / 2 - 6, 30), 9), "h": 0.05})
    # Keep everything inside the lot (silos/tanks may overflow on narrow lots -> drop them).
    kept = []
    for p in parts:
        if "obb" in p:
            if all(obb.grown(.5).contains(q) for q in p["obb"].corners()):
                kept.append(p)
        else:
            cc, r = p["centre"], p["r"]
            if all(obb.contains(q) for q in ((cc[0] + r, cc[1]), (cc[0] - r, cc[1]), (cc[0], cc[1] + r), (cc[0], cc[1] - r))):
                kept.append(p)
    return kept
