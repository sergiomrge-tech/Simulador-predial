#!/usr/bin/env python3
"""Road-network distances on the W1 masterplan layout (no Blender).

Builds a graph from spec roads, local streets and driveways produced by masterplan_layout.Layout,
then runs Dijkstra from the player's starting points to every campaign and life location.

Usage: python Tools/Map/masterplan_routes.py [PROJECT_ROOT]
Output: Docs/masterplan-routes-v1.json
"""
import heapq
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from masterplan_layout import Layout, ROAD_WIDTH, load_registry, load_spec, point_seg_dist, segs_intersect  # noqa: E402

ORIGINS = ["garage", "home.starter"]
# Real-world equivalent speeds (km/h). Game time scale is not defined yet; these only compare modes.
SPEEDS = {"walk": 5.0, "v0_initial": 15.0, "car_urban": 30.0}


def seg_intersection(a, b, c, d):
    x1, y1 = a; x2, y2 = b; x3, y3 = c; x4, y4 = d
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def build(layout):
    segs = []  # [a, b, width, attachments]
    for road in layout.roads:
        for a, b in zip(road["points"], road["points"][1:]):
            segs.append([tuple(a), tuple(b), road["width"], []])
    n_road = len(segs)
    for edges in layout.local_edges.values():
        for a, b in edges:
            segs.append([a, b, ROAD_WIDTH["local"], []])

    def key(p):
        return (round(p[0], 1), round(p[1], 1))

    def attach(i, p):
        segs[i][3].append(p)
        return key(p)

    # Road x road intersections.
    for i in range(n_road):
        for j in range(i + 1, n_road):
            a, b, _, _ = segs[i]
            c, d, _, _ = segs[j]
            if segs_intersect(a, b, c, d):
                p = seg_intersection(a, b, c, d)
                attach(i, p); attach(j, p)
    # Local nodes join roads where they reach them (same rule as layout pruning).
    extra = []
    for k in range(n_road, len(segs)):
        a, b, w, _ = segs[k]
        for i in range(n_road):
            s0, s1, rw, _ = segs[i]
            reach = rw / 2 + w / 2 + 25
            for p in (a, b):
                dist, q = point_seg_dist(p, s0, s1)
                if dist < reach:
                    extra.append((key(p), attach(i, q), dist))
            if segs_intersect(a, b, s0, s1):
                q = seg_intersection(a, b, s0, s1)
                attach(i, q); attach(k, q)
    graph = {}

    def link(u, v, w):
        graph.setdefault(u, []).append((v, w))
        graph.setdefault(v, []).append((u, w))

    for a, b, _, att in segs:
        pts = [a, b] + att
        dx, dz = b[0] - a[0], b[1] - a[1]
        pts.sort(key=lambda p: (p[0] - a[0]) * dx + (p[1] - a[1]) * dz)
        for p, q in zip(pts, pts[1:]):
            link(key(p), key(q), math.hypot(q[0] - p[0], q[1] - p[1]))
    for u, v, w in extra:
        link(u, v, w)
    # Locations: driveway target on the network, or nearest network point.
    loc_nodes = {}
    drive = {dw["target"]: dw for dw in layout.driveways}
    all_locs = {l["id"]: (l["x"], l["z"]) for l in layout.campaign + layout.life}
    for lid, centre in all_locs.items():
        if lid in drive:
            on_seg, on_rect = drive[lid]["b"], drive[lid]["a"]
        else:
            on_rect = centre
            on_seg = None
        best = None
        target = on_seg or centre
        for i, (s0, s1, _, _) in enumerate(segs):
            dist, q = point_seg_dist(target, s0, s1)
            if best is None or dist < best[0]:
                best = (dist, i, q)
        node = attach_late(segs, best[1], best[2], graph, key)
        loc = ("loc", lid)
        link(loc, node, best[0] + math.hypot(on_rect[0] - target[0], on_rect[1] - target[1]))
        loc_nodes[lid] = loc
    return graph, loc_nodes


def attach_late(segs, i, q, graph, key):
    """Insert a point into an already-linked segment by connecting it to the segment's neighbouring nodes."""
    a, b, _, att = segs[i]
    pts = [a, b] + att
    dx, dz = b[0] - a[0], b[1] - a[1]
    pts.sort(key=lambda p: (p[0] - a[0]) * dx + (p[1] - a[1]) * dz)
    tq = (q[0] - a[0]) * dx + (q[1] - a[1]) * dz
    prev = max((p for p in pts if (p[0] - a[0]) * dx + (p[1] - a[1]) * dz <= tq),
               key=lambda p: (p[0] - a[0]) * dx + (p[1] - a[1]) * dz, default=a)
    nxt = min((p for p in pts if (p[0] - a[0]) * dx + (p[1] - a[1]) * dz >= tq),
              key=lambda p: (p[0] - a[0]) * dx + (p[1] - a[1]) * dz, default=b)
    k = ("pt", key(q))
    for p in (prev, nxt):
        w = math.hypot(p[0] - q[0], p[1] - q[1])
        graph.setdefault(k, []).append((key(p), w))
        graph.setdefault(key(p), []).append((k, w))
    return k


def dijkstra(graph, src):
    dist = {src: 0.0}
    pq = [(0.0, 0, src)]
    tie = 0
    while pq:
        d, _, u = heapq.heappop(pq)
        if d > dist.get(u, math.inf):
            continue
        for v, w in graph.get(u, ()):
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                tie += 1
                heapq.heappush(pq, (nd, tie, v))
    return dist


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    layout = Layout(load_spec(root), load_registry(root))
    graph, loc_nodes = build(layout)
    locs = {l["id"]: l for l in layout.campaign + layout.life}
    out = {"speedsKmh": SPEEDS, "note": "real-world equivalent minutes; game time scale not defined yet", "origins": {}}
    unreachable = []
    for origin in ORIGINS:
        dist = dijkstra(graph, loc_nodes[origin])
        rows = {}
        o = locs[origin]
        for lid, node in loc_nodes.items():
            if lid == origin:
                continue
            d = dist.get(node)
            if d is None:
                unreachable.append(f"{origin}->{lid}")
                continue
            straight = math.hypot(locs[lid]["x"] - o["x"], locs[lid]["z"] - o["z"])
            rows[lid] = {"district": locs[lid]["district"], "networkM": round(d), "straightM": round(straight),
                         "detour": round(d / straight, 2) if straight else None,
                         "minutes": {m: round(d / 1000 / v * 60, 1) for m, v in SPEEDS.items()}}
        out["origins"][origin] = dict(sorted(rows.items(), key=lambda kv: kv[1]["networkM"]))
    out["unreachable"] = unreachable
    path = root / "Docs" / "masterplan-routes-v1.json"
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    g = out["origins"]["garage"]
    for lid in [l["id"] for l in layout.campaign]:
        r = g.get(lid)
        if r:
            print(f"{lid:15} {r['district']:10} {r['networkM']:6} m  detour {r['detour']}  walk {r['minutes']['walk']:5} min  car {r['minutes']['car_urban']:4} min")
    print("unreachable:", unreachable)


if __name__ == "__main__":
    main()
