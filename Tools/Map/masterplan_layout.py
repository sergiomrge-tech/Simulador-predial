"""Deterministic Santa Aurora W1 masterplan layout (pure Python, no Blender).

Shared by Tools/Map/validate_masterplan.py and Tools/Blender/create_santa_aurora_masterplan.py
so the validated layout is exactly the generated layout.

Coordinates are spec metres: x = east, z = north. Blender maps spec z -> Blender Y.
Everything produced here is W1 MASSING (S0), never final art.
"""
import json
import math
import random
from pathlib import Path

ROAD_WIDTH = {"arterial": 30.0, "collector": 18.0, "local": 12.0, "driveway": 8.0}
SETBACK = 6.0
ACCESS_MAX_GAP = 120.0
# Ownership order resolves nominal district bounds that overlap at the seams.
DISTRICT_OWNERSHIP = ["civic", "expansion", "old", "industrial", "corporate", "technology"]

# Background shell composition per district (World Bible section 7 / 8).
DISTRICT_FABRIC = {
    "old":        {"grid": 180, "lot": (26, 26), "gap": 6,  "floors": (2, 6),  "floorH": 3.2, "target": 170},
    "expansion":  {"grid": 260, "lot": (40, 40), "gap": 14, "floors": (4, 14), "floorH": 3.0, "target": 110},
    "civic":      {"grid": 220, "lot": (45, 45), "gap": 15, "floors": (3, 10), "floorH": 3.6, "target": 45},
    "corporate":  {"grid": 240, "lot": (48, 48), "gap": 16, "floors": (8, 35), "floorH": 3.8, "target": 65},
    "industrial": {"grid": 380, "lot": (90, 70), "gap": 22, "floors": (1, 3),  "floorH": 6.0, "target": 75},
    "technology": {"grid": 320, "lot": (55, 55), "gap": 18, "floors": (8, 28), "floorH": 3.8, "target": 55},
}

# Urban block fabric (perimeter massing per street block) so districts read at city scale.
# ring = building depth along block edges, sides = how many block edges get built, h = height range (m),
# vacancy = share of blocks left open (yards, parking, vacant lots). "shed" fills the block with one low volume.
BLOCK_FABRIC = {
    "old":        {"mode": "ring", "ring": 22, "sides": (3, 4), "h": (6.5, 16), "vacancy": .08},
    "expansion":  {"mode": "ring", "ring": 18, "sides": (2, 3), "h": (9, 24),   "vacancy": .22},
    "civic":      {"mode": "ring", "ring": 20, "sides": (2, 3), "h": (10, 20),  "vacancy": .25},
    "corporate":  {"mode": "ring", "ring": 24, "sides": (2, 4), "h": (14, 32),  "vacancy": .18},
    "industrial": {"mode": "shed", "cover": (.45, .72), "h": (8, 14), "vacancy": .30},
    "technology": {"mode": "ring", "ring": 26, "sides": (1, 3), "h": (10, 22),  "vacancy": .30},
}

# Composite massing inside campaign footprints: (dx, dz, w, d, h, role).
# Offsets are relative to the footprint centre; heights follow structure_registry_v1 floors.
CAMPAIGN_MASSING = {
    "garage":        [(0, 4, 30, 30, 6.5, "workshop_shed")],
    "horizonte":     [(0, 4, 38, 44, 37, "residential_slab"), (0, 6, 12, 12, 42, "roof_plant")],
    "apartments":    [(0, 0, 44, 56, 16, "residential_block")],
    "grocery":       [(0, 3, 26, 28, 7.5, "shop")],
    "restaurant":    [(0, 3, 32, 34, 7.5, "restaurant")],
    "workshop":      [(0, 8, 42, 36, 8, "workshop_boxes")],
    "smalloffice":   [(0, 0, 34, 40, 11, "office")],
    "imperial":      [(0, -36, 70, 20, 13, "foyer"), (0, -2, 72, 48, 19, "auditorium"), (0, 34, 50, 24, 29, "fly_tower")],
    "school":        [(-30, 30, 36, 60, 9, "classroom_wing"), (20, 45, 56, 30, 9, "classroom_wing"), (25, -35, 46, 40, 8, "gym_kitchen")],
    "recurringcondo":[(0, 0, 130, 160, 4, "podium_garage"), (-34, -40, 30, 36, 50, "tower_a"), (34, 40, 30, 36, 50, "tower_b"), (0, -82, 16, 10, 5, "portaria")],
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
                      (0, 0, 190, 2, 3, "perimeter_s"), (0, 0, 2, 230, 3, "perimeter_w")],
    "smarttower":    [(0, 0, 104, 124, 10, "podium"), (0, 0, 46, 52, 91, "smart_tower")],
    "central":       [(-100, 120, 100, 70, 24, "administrative_centre"), (40, 140, 70, 60, 20, "urban_monitoring"),
                      (130, 120, 70, 70, 14, "municipal_datacentre"), (140, 30, 14, 14, 62, "telecom_mast"),
                      (-120, 10, 70, 60, 14, "emergency_centre"), (-120, -100, 60, 70, 10, "electrical_distribution"),
                      (-30, -150, 70, 40, 8, "generators"), (60, -150, 50, 40, 9, "pumps_drainage"),
                      (130, -100, 60, 70, 11, "hvac_plant"), (120, -20, 40, 40, 16, "automation_controller"),
                      (0, 0, 220, 8, 2, "service_tunnel_ew"), (0, 0, 8, 300, 2, "service_tunnel_ns")],
}
# Datacenter perimeter walls are placed on the footprint edge; others use offsets above.
PERIMETER_ROLES = {"perimeter_s", "perimeter_w"}

LIFE_HEIGHT = {"home.starter": 13.0, "home.apartment.01": 30.0, "home.apartment.02": 24.0, "fuel.old": 6.0, "fuel.north": 6.0,
               "leisure.park": 1.0, "leisure.fishing": 1.0}


def load_spec(root):
    path = Path(root) / "ArtSource" / "Blender" / "World" / "masterplan_spec_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_registry(root):
    path = Path(root) / "ArtSource" / "Blender" / "World" / "structure_registry_v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- geometry helpers

def rect(cx, cz, w, d, pad=0.0):
    return (cx - w / 2 - pad, cz - d / 2 - pad, cx + w / 2 + pad, cz + d / 2 + pad)


def rects_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def point_in_rect(p, r):
    return r[0] <= p[0] <= r[2] and r[1] <= p[1] <= r[3]


def point_seg_dist(p, a, b):
    ax, az = a; bx, bz = b; px, pz = p
    dx, dz = bx - ax, bz - az
    L = dx * dx + dz * dz
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / L))
    q = (ax + t * dx, az + t * dz)
    return math.hypot(q[0] - px, q[1] - pz), q


def point_rect_dist(p, r):
    dx = max(r[0] - p[0], 0, p[0] - r[2])
    dz = max(r[1] - p[1], 0, p[1] - r[3])
    q = (min(max(p[0], r[0]), r[2]), min(max(p[1], r[1]), r[3]))
    return math.hypot(dx, dz), q


def _ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def segs_intersect(a, b, c, d):
    d1, d2, d3, d4 = _ccw(c, d, a), _ccw(c, d, b), _ccw(a, b, c), _ccw(a, b, d)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))


def seg_rect_dist(a, b, r):
    """Exact distance between a segment and an axis-aligned rectangle, plus closest pair (on_seg, on_rect)."""
    if point_in_rect(a, r):
        return 0.0, a, a
    corners = [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]
    for i in range(4):
        if segs_intersect(a, b, corners[i], corners[(i + 1) % 4]):
            return 0.0, a, a
    best = None
    for p in (a, b):
        dist, q = point_rect_dist(p, r)
        if best is None or dist < best[0]:
            best = (dist, p, q)
    for c in corners:
        dist, q = point_seg_dist(c, a, b)
        if dist < best[0]:
            best = (dist, q, c)
    return best


def polyline_segments(points):
    return [(tuple(points[i]), tuple(points[i + 1])) for i in range(len(points) - 1)]


def polyline_length(points):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in polyline_segments(points))


# ---------------------------------------------------------------- layout

class Layout:
    def __init__(self, spec, registry=None, seed=20261003):
        self.spec = spec
        self.registry = registry or {"locations": []}
        self.rng = random.Random(seed)
        self.errors = []
        self.warnings = []
        w = spec["world"]
        self.world = (w["minX"], w["minZ"], w["maxX"], w["maxZ"])
        self.districts = {d["id"]: d for d in spec["districts"]}
        self.campaign = spec["campaignLocations"]
        self.life = spec["lifeLocations"]
        self.open_spaces = spec.get("openSpaces", [])
        self.canal = spec.get("canal")
        self.roads = []          # dicts: id, name, class, width, points
        self.local_edges = {}    # district -> list[(a, b)]
        self.driveways = []      # dicts: target, a, b, gap
        self.shells = []         # dicts: id, district, x, z, w, d, h
        self.campaign_rects = {l["id"]: rect(l["x"], l["z"], l["width"], l["depth"]) for l in self.campaign}
        self.life_rects = {l["id"]: rect(l["x"], l["z"], 20, 20) for l in self.life}
        self.open_rects = {o["id"]: rect(o["x"], o["z"], o["width"], o["depth"]) for o in self.open_spaces}
        self._build_roads()
        self._check_spec_roads()
        self._build_local_grid()
        self._prune_disconnected()
        self._build_driveways()
        self._build_shells()
        self._build_block_fabric()

    # --- ownership
    def owner(self, p):
        for did in DISTRICT_OWNERSHIP:
            d = self.districts.get(did)
            if d and point_in_rect(p, d["bounds"]):
                return did
        return None

    # --- obstacles
    def hard_rects(self, pad):
        out = [rect(l["x"], l["z"], l["width"], l["depth"], pad) for l in self.campaign]
        out += [rect(l["x"], l["z"], 20, 20, pad) for l in self.life]
        out += [rect(o["x"], o["z"], o["width"], o["depth"], pad) for o in self.open_spaces]
        return out

    def canal_segments(self):
        return polyline_segments(self.canal["points"]) if self.canal else []

    # --- spec roads
    def _build_roads(self):
        for r in self.spec["roads"]:
            pts = r.get("points") or [r["from"], r["to"]]
            self.roads.append({"id": r["id"], "name": r["name"], "class": r["class"],
                               "width": ROAD_WIDTH[r["class"]], "points": [tuple(p) for p in pts]})

    def _check_spec_roads(self):
        for road in self.roads:
            half = road["width"] / 2
            for a, b in polyline_segments(road["points"]):
                for loc in self.campaign:
                    dist, _, _ = seg_rect_dist(a, b, self.campaign_rects[loc["id"]])
                    if dist < half + SETBACK:
                        self.errors.append(f"road {road['id']} crosses/encroaches campaign footprint {loc['id']} (clear {dist - half:.1f} m)")
                for loc in self.life:
                    dist, _, _ = seg_rect_dist(a, b, self.life_rects[loc["id"]])
                    if dist < half + SETBACK:
                        self.errors.append(f"road {road['id']} encroaches life marker {loc['id']} (clear {dist - half:.1f} m)")
                for oid, orc in self.open_rects.items():
                    dist, _, _ = seg_rect_dist(a, b, orc)
                    if dist < half:
                        self.errors.append(f"road {road['id']} crosses open space {oid}")
        if self.canal:
            ch = self.canal["width"] / 2
            for a, b in self.canal_segments():
                for loc in self.campaign:
                    dist, _, _ = seg_rect_dist(a, b, self.campaign_rects[loc["id"]])
                    if dist < ch + SETBACK:
                        self.errors.append(f"canal crosses campaign footprint {loc['id']}")
                for loc in self.life:
                    dist, _, _ = seg_rect_dist(a, b, self.life_rects[loc["id"]])
                    if dist < ch + SETBACK:
                        self.errors.append(f"canal crosses life marker {loc['id']}")

    # --- local grid
    def _edge_blocked(self, a, b, obstacles):
        for r in obstacles:
            if seg_rect_dist(a, b, r)[0] <= 0:
                return True
        # Do not duplicate spec roads: skip local edges running inside an arterial/collector corridor.
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        for road in self.roads:
            for s0, s1 in polyline_segments(road["points"]):
                if point_seg_dist(mid, s0, s1)[0] < road["width"] / 2 + 20:
                    return True
        if self.canal:
            ch = self.canal["width"] / 2 + 10
            for s0, s1 in self.canal_segments():
                if segs_intersect(a, b, s0, s1) or point_seg_dist(mid, s0, s1)[0] < ch:
                    return True
        return False

    def _build_local_grid(self):
        lw = ROAD_WIDTH["local"] / 2
        obstacles = self.hard_rects(lw + SETBACK)
        for did, fab in DISTRICT_FABRIC.items():
            d = self.districts[did]
            x0, z0, x1, z1 = d["bounds"]
            g = fab["grid"]
            xs = [x0 + i * g for i in range(int((x1 - x0) // g) + 1)]
            zs = [z0 + i * g for i in range(int((z1 - z0) // g) + 1)]
            # Split block edges into short pieces so a large lot only removes the street stretch it occupies.
            pieces = max(1, math.ceil(g / 60))
            step = g / pieces
            edges = []
            for x in xs:
                for i in range(len(zs) - 1):
                    for k in range(pieces):
                        edges.append(((x, zs[i] + k * step), (x, zs[i] + (k + 1) * step)))
            for z in zs:
                for i in range(len(xs) - 1):
                    for k in range(pieces):
                        edges.append(((xs[i] + k * step, z), (xs[i] + (k + 1) * step, z)))
            kept = []
            for a, b in edges:
                mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                if self.owner(mid) != did:
                    continue
                if self._edge_blocked(a, b, obstacles):
                    continue
                kept.append((a, b))
            self.local_edges[did] = kept

    def _road_segments(self):
        for road in self.roads:
            for a, b in polyline_segments(road["points"]):
                yield road, a, b

    def _prune_disconnected(self):
        """Keep only local edges that reach the spec road network (directly or through other local edges)."""
        parent = {}

        def find(k):
            while parent.setdefault(k, k) != k:
                parent[k] = parent[parent[k]]
                k = parent[k]
            return k

        def union(a, b):
            parent[find(a)] = find(b)

        # Spec roads: connected when their centre lines intersect or nearly touch.
        segs = list(self._road_segments())
        for road, a, b in segs:
            union(("road", road["id"]), ("road", road["id"]))
        for i, (r1, a, b) in enumerate(segs):
            for r2, c, d in segs[i + 1:]:
                if r1["id"] == r2["id"]:
                    continue
                touch = segs_intersect(a, b, c, d) or min(point_seg_dist(a, c, d)[0], point_seg_dist(b, c, d)[0],
                                                          point_seg_dist(c, a, b)[0], point_seg_dist(d, a, b)[0]) < (r1["width"] + r2["width"]) / 2
                if touch:
                    union(("road", r1["id"]), ("road", r2["id"]))
        road_roots = {find(("road", r["id"])) for r in self.roads}
        if len(road_roots) > 1:
            self.errors.append(f"spec road network is split into {len(road_roots)} components")
        for did, edges in self.local_edges.items():
            for a, b in edges:
                union(("n", a), ("n", b))
                for road, s0, s1 in segs:
                    reach = road["width"] / 2 + ROAD_WIDTH["local"] / 2 + 25
                    if (segs_intersect(a, b, s0, s1) or point_seg_dist(a, s0, s1)[0] < reach
                            or point_seg_dist(b, s0, s1)[0] < reach):
                        union(("n", a), ("road", road["id"]))
        main = find(("road", self.roads[0]["id"]))
        dropped = 0
        for did in self.local_edges:
            keep = [e for e in self.local_edges[did] if find(("n", e[0])) == main]
            dropped += len(self.local_edges[did]) - len(keep)
            self.local_edges[did] = keep
        self.dropped_local_edges = dropped

    # --- access
    def network_segments(self):
        for road in self.roads:
            for a, b in polyline_segments(road["points"]):
                yield road["class"], road["width"], road["id"], a, b
        for did, edges in self.local_edges.items():
            for a, b in edges:
                yield "local", ROAD_WIDTH["local"], f"local.{did}", a, b

    def _build_driveways(self):
        segs = list(self.network_segments())
        targets = [(l["id"], "campaign", self.campaign_rects[l["id"]]) for l in self.campaign]
        anchored = {o["anchor"]: self.open_rects[o["id"]] for o in self.open_spaces if o.get("anchor")}
        targets += [(l["id"], "life", anchored.get(l["id"], self.life_rects[l["id"]])) for l in self.life]
        all_rects = dict(self.campaign_rects)
        all_rects.update(self.life_rects)
        self.access = {}
        for tid, kind, r in targets:
            best = None
            for cls, width, rid, a, b in segs:
                dist, on_seg, on_rect = seg_rect_dist(a, b, r)
                gap = max(0.0, dist - width / 2)
                if best is None or gap < best[0]:
                    best = (gap, rid, cls, on_seg, on_rect, width)
            gap, rid, cls, on_seg, on_rect, width = best
            self.access[tid] = {"kind": kind, "road": rid, "roadClass": cls, "gap": round(gap, 1)}
            if gap > ACCESS_MAX_GAP:
                self.errors.append(f"no plausible road access for {tid}: nearest {rid} at {gap:.0f} m")
                continue
            if gap > 1.0:
                dw = {"target": tid, "road": rid, "a": on_rect, "b": on_seg, "gap": round(gap, 1)}
                for oid, orc in all_rects.items():
                    if oid != tid and not point_in_rect(((orc[0] + orc[2]) / 2, (orc[1] + orc[3]) / 2), r) and seg_rect_dist(on_rect, on_seg, orc)[0] <= 0:
                        self.errors.append(f"driveway for {tid} crosses {oid}")
                self.driveways.append(dw)

    # --- background shells
    def _build_shells(self):
        hard = self.hard_rects(15)
        counts = {}
        for did, fab in DISTRICT_FABRIC.items():
            d = self.districts[did]
            x0, z0, x1, z1 = d["bounds"]
            g = fab["grid"]
            lw, ld = fab["lot"]
            gap = fab["gap"]
            inset = ROAD_WIDTH["local"] / 2 + 6
            cand = []
            bx = x0
            while bx + g <= x1 + 1e-6:
                bz = z0
                while bz + g <= z1 + 1e-6:
                    usable = g - 2 * inset
                    nx = max(1, int((usable + gap) // (lw + gap)))
                    nz = max(1, int((usable + gap) // (ld + gap)))
                    sx = (usable - (nx * lw + (nx - 1) * gap)) / 2
                    sz = (usable - (nz * ld + (nz - 1) * gap)) / 2
                    for i in range(nx):
                        for j in range(nz):
                            cx = bx + inset + sx + i * (lw + gap) + lw / 2
                            cz = bz + inset + sz + j * (ld + gap) + ld / 2
                            cand.append((cx, cz))
                    bz += g
                bx += g
            ok = []
            for cx, cz in cand:
                if self.owner((cx, cz)) != did:
                    continue
                r = rect(cx, cz, lw, ld)
                if any(rects_overlap(r, h) for h in hard):
                    continue
                if self._rect_hits_corridor(r):
                    continue
                ok.append((cx, cz))
            self.rng.shuffle(ok)
            chosen = ok[:fab["target"]]
            cx0, cz0 = d["center"]
            radius = max(x1 - x0, z1 - z0) / 2
            for n, (cx, cz) in enumerate(sorted(chosen)):
                w = lw * self.rng.uniform(.62, 1.0)
                dd = ld * self.rng.uniform(.62, 1.0)
                lo, hi = fab["floors"]
                closeness = 1 - min(1.0, math.hypot(cx - cx0, cz - cz0) / radius)
                u = self.rng.random() ** 1.6
                if did in ("corporate", "technology", "expansion"):
                    u = min(1.0, u * (0.55 + 0.9 * closeness))
                floors = lo + round((hi - lo) * u)
                self.shells.append({"id": f"SHELL_{did}_{n:03d}", "district": did, "x": round(cx, 1), "z": round(cz, 1),
                                    "w": round(w, 1), "d": round(dd, 1), "h": round(floors * fab["floorH"], 1), "floors": floors})
            counts[did] = len(chosen)
            if len(chosen) < fab["target"] * 0.6:
                self.warnings.append(f"district {did}: only {len(chosen)} background shells (target {fab['target']})")
        # Industrial vertical accents: chimneys/silos give the low district a readable skyline.
        accents = [s for s in self.shells if s["district"] == "industrial"]
        self.rng.shuffle(accents)
        for s in accents[:10]:
            self.shells.append({"id": s["id"] + "_stack", "district": "industrial", "x": s["x"] + s["w"] / 2 - 5,
                                "z": s["z"] + s["d"] / 2 - 5, "w": 5.0, "d": 5.0, "h": round(self.rng.uniform(32, 55), 1),
                                "floors": 0, "accent": True})
        self.shell_counts = counts

    def _build_block_fabric(self):
        """Perimeter massing per street block; pieces touching lots, markers, open space or corridors are dropped."""
        hard = self.hard_rects(12)
        self.fabric = []
        inset = ROAD_WIDTH["local"] / 2 + 4
        for did, bf in BLOCK_FABRIC.items():
            d = self.districts[did]
            x0, z0, x1, z1 = d["bounds"]
            g = DISTRICT_FABRIC[did]["grid"]
            bx = x0
            while bx + g <= x1 + 1e-6:
                bz = z0
                while bz + g <= z1 + 1e-6:
                    centre = (bx + g / 2, bz + g / 2)
                    if self.owner(centre) == did and self.rng.random() >= bf["vacancy"]:
                        bx0, bz0, bx1, bz1 = bx + inset, bz + inset, bx + g - inset, bz + g - inset
                        pieces = []
                        if bf["mode"] == "shed":
                            w = (bx1 - bx0) * self.rng.uniform(*bf["cover"])
                            dd = (bz1 - bz0) * self.rng.uniform(.5, .9)
                            pieces.append((rect(centre[0], centre[1], w, dd), self.rng.uniform(*bf["h"])))
                        else:
                            ring = bf["ring"]
                            edges = [(bx0, bz0, bx1, bz0 + ring), (bx0, bz1 - ring, bx1, bz1),
                                     (bx0, bz0 + ring, bx0 + ring, bz1 - ring), (bx1 - ring, bz0 + ring, bx1, bz1 - ring)]
                            self.rng.shuffle(edges)
                            for e in edges[:self.rng.randint(*bf["sides"])]:
                                # Break each built edge into 2-3 buildings of different heights.
                                n = self.rng.randint(2, 3)
                                horizontal = (e[2] - e[0]) > (e[3] - e[1])
                                span = (e[2] - e[0]) if horizontal else (e[3] - e[1])
                                for k in range(n):
                                    a, b = k * span / n, (k + 1) * span / n - 3
                                    pr = (e[0] + a, e[1], e[0] + b, e[3]) if horizontal else (e[0], e[1] + a, e[2], e[1] + b)
                                    pieces.append((pr, self.rng.uniform(*bf["h"])))
                        for pr, h in pieces:
                            if any(rects_overlap(pr, hr) for hr in hard) or self._rect_hits_corridor(pr):
                                continue
                            self.fabric.append({"district": did, "rect": pr, "h": round(h, 1)})
                    bz += g
                bx += g

    def _rect_hits_corridor(self, r):
        for road in self.roads:
            half = road["width"] / 2 + 8
            for a, b in polyline_segments(road["points"]):
                if seg_rect_dist(a, b, r)[0] < half:
                    return True
        if self.canal:
            ch = self.canal["width"] / 2 + 25
            for a, b in self.canal_segments():
                if seg_rect_dist(a, b, r)[0] < ch:
                    return True
        for dw in self.driveways:
            if seg_rect_dist(dw["a"], dw["b"], r)[0] < ROAD_WIDTH["driveway"] / 2 + 4:
                return True
        return False

    # --- campaign massing
    def campaign_volumes(self, loc):
        parts = CAMPAIGN_MASSING.get(loc["id"])
        x, z, W, D = loc["x"], loc["z"], loc["width"], loc["depth"]
        if not parts:
            return [{"role": "envelope", "x": x, "z": z, "w": W - 4, "d": D - 4, "h": 12.0}]
        out = []
        for dx, dz, w, d, h, role in parts:
            if role == "perimeter_s":
                dx, dz = 0, -D / 2 + 1
            elif role == "perimeter_w":
                dx, dz = -W / 2 + 1, 0
            out.append({"role": role, "x": x + dx, "z": z + dz, "w": w, "d": d, "h": float(h)})
        return out

    def check_massing(self):
        for loc in self.campaign:
            r = self.campaign_rects[loc["id"]]
            for v in self.campaign_volumes(loc):
                vr = rect(v["x"], v["z"], v["w"], v["d"])
                if vr[0] < r[0] - .01 or vr[1] < r[1] - .01 or vr[2] > r[2] + .01 or vr[3] > r[3] + .01:
                    self.errors.append(f"massing {loc['id']}/{v['role']} exceeds footprint")

    # --- reports
    def checks(self):
        self.check_massing()
        # Campaign vs life overlaps (life markers are 20x20 placeholders).
        for lid, lr in self.life_rects.items():
            for cid, cr in self.campaign_rects.items():
                if rects_overlap(lr, cr):
                    self.errors.append(f"life marker {lid} overlaps campaign footprint {cid}")
        for i, a in enumerate(self.campaign):
            for b in self.campaign[i + 1:]:
                if rects_overlap(self.campaign_rects[a["id"]], self.campaign_rects[b["id"]]):
                    self.errors.append(f"campaign footprints overlap: {a['id']} / {b['id']}")
        ids = {l["id"]: l for l in self.campaign + self.life}

        def dist(a, b):
            return round(math.hypot(ids[a]["x"] - ids[b]["x"], ids[a]["z"] - ids[b]["z"]))

        pairs = [("home.starter", "garage"), ("garage", "horizonte"), ("garage", "imperial"), ("garage", "recurringcondo"),
                 ("garage", "factory"), ("garage", "mall"), ("garage", "datacenter"), ("garage", "central"),
                 ("home.starter", "supplier.tools"), ("garage", "vehicles.used")]
        distances = {f"{a}->{b}": dist(a, b) for a, b in pairs}
        if distances["home.starter->garage"] < 60:
            self.errors.append("home.starter is too close to garage (same lot)")
        if distances["garage->central"] < 2500:
            self.warnings.append("garage->central under 2.5 km; transport progression may feel weak")
        area = {}
        for did, d in self.districts.items():
            x0, z0, x1, z1 = d["bounds"]
            area[did] = round((x1 - x0) * (z1 - z0) / 1e6, 2)
            if area[did] < 3.0:
                self.warnings.append(f"district {did} smaller than 3 km2")
        # Expansion reserve: share of macro cells not owned by any district.
        free = 0
        x0w, z0w, x1w, z1w = self.world
        for ix in range(int((x1w - x0w) // 250)):
            for iz in range(int((z1w - z0w) // 250)):
                if self.owner((x0w + ix * 250 + 125, z0w + iz * 250 + 125)) is None:
                    free += 1
        total_sub = ((x1w - x0w) // 250) * ((z1w - z0w) // 250)
        return {
            "roadLengthsKm": {r["id"]: round(polyline_length(r["points"]) / 1000, 2) for r in self.roads},
            "localStreetEdges": {k: len(v) for k, v in self.local_edges.items()},
            "localStreetKm": round(sum(math.hypot(b[0] - a[0], b[1] - a[1]) for v in self.local_edges.values() for a, b in v) / 1000, 1),
            "droppedDisconnectedLocalEdges": self.dropped_local_edges,
            "driveways": len(self.driveways),
            "access": self.access,
            "backgroundShells": self.shell_counts,
            "blockFabricVolumes": {did: sum(1 for f in self.fabric if f["district"] == did) for did in self.districts},
            "industrialAccents": sum(1 for s in self.shells if s.get("accent")),
            "keyDistancesMeters": distances,
            "districtAreaKm2": area,
            "unassignedSubcellShare": round(free / total_sub, 3),
            "maxHeights": {did: max((s["h"] for s in self.shells if s["district"] == did), default=0) for did in self.districts},
        }
