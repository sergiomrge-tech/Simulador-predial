#!/usr/bin/env python3
"""Road-network distances on the masterplan layout (no Blender).

Builds a graph from spec roads (smoothed, with roundabouts), every zone/Old Town street that vehicles can use,
and the location driveways, then runs Dijkstra from the player's starting points to every campaign and life location.

Usage: python Tools/Map/masterplan_routes.py [PROJECT_ROOT]
Output: Docs/masterplan-routes-v1.json
"""
import heapq
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from masterplan_layout import SPRINT_MS, WALK_MS, Layout, load_registry, load_spec  # noqa: E402
from sa_geom import SpatialHash, point_seg, seg_intersection  # noqa: E402
from urban_fabric import STREET  # noqa: E402

ORIGINS = ["garage", "home.starter"]
# Real-world equivalent speeds (km/h). walk/sprint are the prototype controller speeds (3 and 5 m/s).
SPEEDS = {"walk": WALK_MS * 3.6, "sprint": SPRINT_MS * 3.6, "v0_initial": 15.0, "car_urban": 30.0}


def key(p):
    return (round(p[0], 1), round(p[1], 1))


def build(layout):
    segs = []  # [a, b, width, attachments, is_spec]
    for road in layout.roads:
        for a, b in zip(road["points"], road["points"][1:]):
            segs.append([tuple(a), tuple(b), road["width"], [], True])
    for edges in layout.local_edges.values():
        for a, b, cls in edges:
            if cls == "passage":
                continue
            segs.append([tuple(a), tuple(b), STREET[cls]["total"], [], False])
    h = SpatialHash(150.0)
    for i, (a, b, w, _, _) in enumerate(segs):
        h.insert((min(a[0], b[0]) - w, min(a[1], b[1]) - w, max(a[0], b[0]) + w, max(a[1], b[1]) + w), i)
    graph = {}

    def link(u, v, w):
        graph.setdefault(u, []).append((v, w))
        graph.setdefault(v, []).append((u, w))

    extra = []
    for i, (a, b, w, att, spec_i) in enumerate(segs):
        aabb = (min(a[0], b[0]) - 40, min(a[1], b[1]) - 40, max(a[0], b[0]) + 40, max(a[1], b[1]) + 40)
        for j in h.query(aabb):
            if j <= i:
                continue
            c, d, w2, att2, spec_j = segs[j]
            hit = seg_intersection(a, b, c, d)
            if hit:
                p = hit[0]
                att.append(p)
                att2.append(p)
                continue
            # End points that stop short of another street still join it (T-junctions, roundabout entries).
            reach = (w + w2) / 2 + 6
            for p, owner in ((a, i), (b, i), (c, j), (d, j)):
                other = j if owner == i else i
                oa, ob = segs[other][0], segs[other][1]
                dd, q, _ = point_seg(p, oa, ob)
                if dd < reach and dd > 0.05:
                    segs[other][3].append(q)
                    extra.append((key(p), key(q), dd))
    for a, b, _, att, _ in segs:
        pts = [a, b] + att
        dx, dz = b[0] - a[0], b[1] - a[1]
        pts.sort(key=lambda p: (p[0] - a[0]) * dx + (p[1] - a[1]) * dz)
        for p, q in zip(pts, pts[1:]):
            link(key(p), key(q), math.hypot(q[0] - p[0], q[1] - p[1]))
    for u, v, w in extra:
        link(u, v, w)
    loc_nodes = {}
    drive = {dw["target"]: dw for dw in layout.driveways}
    for loc in layout.campaign + layout.life:
        lid = loc["id"]
        centre = (loc["x"], loc["z"])
        if lid in drive:
            target, on_rect = tuple(drive[lid]["b"]), tuple(drive[lid]["a"])
        else:
            target, on_rect = centre, centre
        best = None
        for reach in (100, 300, 1000):
            for i in h.query((target[0] - reach, target[1] - reach, target[0] + reach, target[1] + reach)):
                dd, q, _ = point_seg(target, segs[i][0], segs[i][1])
                if best is None or dd < best[0]:
                    best = (dd, i, q)
            if best:
                break
        dd, i, q = best
        a, b = segs[i][0], segs[i][1]
        node = ("pt", key(q))
        for p in (a, b):
            link(node, key(p), math.hypot(p[0] - q[0], p[1] - q[1]))
        link(("loc", lid), node, dd + math.hypot(on_rect[0] - target[0], on_rect[1] - target[1]))
        loc_nodes[lid] = ("loc", lid)
    return graph, loc_nodes


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
    layout = Layout(load_spec(root), load_registry(root), root=root)
    graph, loc_nodes = build(layout)
    locs = {l["id"]: l for l in layout.campaign + layout.life}
    out = {"speedsKmh": SPEEDS, "note": "real-world equivalent minutes; game time scale not defined yet; walk/sprint use the prototype controller speeds",
           "origins": {}}
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
