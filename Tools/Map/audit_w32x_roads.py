"""Pure-Python audit of the corridor street network (W3.2.x): connectivity, junction angles, residual kinks, curvature, near-overlaps.
Run: python Tools/Map/audit_w32x_roads.py [--out report.json]"""
import collections, json, math, statistics, sys
from pathlib import Path
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "Tools" / "Map")); sys.path.insert(0, str(root / "Tools" / "Blender"))
import sa_geom
from masterplan_layout import load_spec
from oldtown_layout import OldTown

BOX = (-3000.0, -2500.0, -2250.0, -1250.0)
inside = lambda p, pad=0.0: BOX[0] - pad <= p[0] <= BOX[2] + pad and BOX[1] - pad <= p[1] <= BOX[3] + pad
ot = OldTown(root, load_spec(root))
g = ot.graph
inc, deg = g.incident(), g.degree()
E = [(eid, e) for eid, e in g.edges.items() if e["cls"] in ("arterial", "main", "local", "collector", "service", "alley") and (inside(g.seg(eid)[0]) or inside(g.seg(eid)[1]))]
rep = {"edges": len(E), "by_class": dict(collections.Counter(e["cls"] for _, e in E))}
# connectivity of the drivable corridor network
parent = {}
def find(a):
    while parent.setdefault(a, a) != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
for _, e in E:
    parent[find(e["a"])] = find(e["b"])
comps = collections.Counter(find(n) for _, e in E for n in (e["a"], e["b"]))
big = max(comps.values())
rep["components"] = len(comps)
rep["largest_component_edges_share"] = round(big / (2 * len(E)), 3)
# main street spine: arterial edges must all be in the largest component
rep["isolated_pieces_edges"] = sorted(n for c, n in comps.items() if c != comps.most_common(1)[0][0])[:10]
# dead ends
rep["dead_ends"] = sum(1 for n, d in deg.items() if d == 1 and inside(g.nodes[n]))
# junction angles + deflection at through nodes
angs, defl = [], []
for n, es in inc.items():
    p = g.nodes[n]
    if not inside(p):
        continue
    dirs = []
    for e in es:
        a, b = g.seg(e)
        o = b if sa_geom.dist(a, p) < 1e-6 else a
        dirs.append(math.atan2(o[1] - p[1], o[0] - p[0]))
    dirs.sort()
    if len(es) >= 3:
        for i in range(len(dirs)):
            angs.append(math.degrees((dirs[(i + 1) % len(dirs)] - dirs[i]) % (2 * math.pi)))
    elif len(es) == 2:
        defl.append(180 - abs(math.degrees((dirs[0] - dirs[1] + math.pi) % (2 * math.pi) - math.pi)))
rep["junction_angles"] = {"n": len(angs), "near_90_pct": round(100 * sum(1 for a in angs if 80 <= a <= 100) / max(1, len(angs)), 1),
                          "min_deg": round(min(angs), 1) if angs else None, "acute_lt_35": sum(1 for a in angs if a < 35)}
rep["through_node_deflection_deg"] = {"n": len(defl), "mean": round(statistics.mean(defl), 2), "p95": round(sorted(defl)[int(.95 * len(defl))], 2), "max": round(max(defl), 1),
                                      "over_25": sum(1 for d in defl if d > 25)}
# edge lengths (cars / poles / lots need segments >= 18 m on streets)
L = [sa_geom.dist(*g.seg(eid)) for eid, _ in E]
rep["edge_len_m"] = {"mean": round(statistics.mean(L), 1), "min": round(min(L), 1), "lt_12": sum(1 for x in L if x < 12)}
rep["curve_stats"] = getattr(ot, "curve_stats", None)
rep["layout_checks"] = ot.checks()
out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
text = json.dumps(rep, indent=2, ensure_ascii=False)
if out:
    out.write_text(text, encoding="utf-8")
print(text)
