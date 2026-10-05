"""Builds the W3.2.x evidence capture routes (teleport + capture steps for the Development Player autopilot).

Inputs : Logs/evidence-candidates.json (extract_w32x_evidence.py), FacilityOps/Assets/StreamingAssets/world-walk-route.json (new route)
Outputs: FacilityOps/Assets/StreamingAssets/world-evidence-route.json   (A-C evidence + D "after" candidates, new build)
         Logs/evidence-route-before.json                                (D "before" candidates, same coordinates, for the old build)
         Logs/evidence-plan.json                                        (what was picked and why)
Unity axes: x east, y up, z north  (Blender x, y, z -> Unity x, z, y)."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
cand = json.loads((ROOT / "Logs" / "evidence-candidates.json").read_text(encoding="utf-8"))
route = json.loads((ROOT / "FacilityOps/Assets/StreamingAssets/world-walk-route.json").read_text(encoding="utf-8"))
lay = cand["layout"]

# ------------------------------------------------------------------ route polyline (x, y, z, leg, fraction)
INTERIOR_LEGS = ("portão -> portaria", "portaria -> porta da escada", "porta da escada -> 1º degrau", "lance 1", "patamar de giro", "pisos seguintes -> 4º andar", "4º andar -> corredor", "corredor -> quadro", "quadro -> 4º andar -> térreo -> rua")
RP = []
for st in route["steps"]:
    if st["kind"] != "walk" or st["name"] in INTERIOR_LEGS:
        continue
    cs = st["corners"]
    total = sum(math.dist((a["x"], a["z"]), (b["x"], b["z"])) for a, b in zip(cs, cs[1:])) or 1.0
    run = 0.0
    for a, b in zip(cs, cs[1:]):
        L = math.dist((a["x"], a["z"]), (b["x"], b["z"]))
        n = max(1, int(L // 2))
        for k in range(n):
            t = k / n
            RP.append((a["x"] + (b["x"] - a["x"]) * t, a["y"] + (b["y"] - a["y"]) * t, a["z"] + (b["z"] - a["z"]) * t, st["name"], (run + L * t) / total))
        run += L
NEARS = {}


def near(x, z):
    """Closest route sample to Unity (x, z): (distance, sample)."""
    key = (round(x), round(z))
    if key not in NEARS:
        best = min(RP, key=lambda p: (p[0] - x) ** 2 + (p[2] - z) ** 2)
        NEARS[key] = (math.hypot(best[0] - x, best[2] - z), best)
    return NEARS[key]


def route_points_between(x, z, dmin, dmax, ymin=-1e9, ymax=1e9, ref=None):
    """Route samples whose distance to (x, z) is within [dmin, dmax] and (optionally) whose height above `ref` is within [ymin, ymax]."""
    out = []
    for p in RP:
        d = math.hypot(p[0] - x, p[2] - z)
        if dmin <= d <= dmax and (ref is None or ymin <= ref - p[1] <= ymax):
            out.append((d, p))
    return out


def yaw_to(px, pz, tx, tz):
    return round(math.degrees(math.atan2(tx - px, tz - pz)), 1)


def V(x, y, z):
    return {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}


def shot(name, label, cam, aim, plan, note):
    """cam = (x, y, z) Unity position of the eyes' feet; aim = (x, y, z)."""
    plan[name] = {"label": label, "camera": [round(v, 1) for v in cam], "aim": [round(v, 1) for v in aim], "note": note}
    return [
        {"kind": "teleport", "name": "tp-" + name, "corners": [V(cam[0], cam[1] + .6, cam[2])], "yaw": yaw_to(cam[0], cam[2], aim[0], aim[2])},
        {"kind": "capture", "name": name, "aim": V(*aim)},
    ]


used_keys = set()
plan, steps, steps_d_after, steps_d_before, plan_d = {}, [], [], [], {}

# ------------------------------------------------------------------ A1 curved residential street
curves = [c for c in lay["curves"] if c["cls"] == "local" and c["amp"] >= 3.0 and c["length"] >= 70 and all(z is not None for z in c["z"])]


def cum(pts):
    out = [0.0]
    for a, b in zip(pts, pts[1:]):
        out.append(out[-1] + math.dist(a, b))
    return out


def chain_dist(c):
    mid = c["points"][len(c["points"]) // 2]
    return near(mid[0], mid[1])[0]


curves.sort(key=chain_dist)
c = curves[0]
pts, zs = c["points"], c["z"]
cs = cum(pts)
mid = len(pts) // 2
ci = max(i for i in range(len(pts)) if cs[i] <= max(0.0, cs[mid] - 16.0))
steps += shot("A1-rua-curva-residencial", "Rua residencial curva", (pts[ci][0], zs[ci], pts[ci][1]), (pts[mid][0], zs[mid] + 1.5, pts[mid][1]), plan,
              f"local chain {c['length']} m, bow {c['amp']} m, {chain_dist(c):.0f} m from the route")

# ------------------------------------------------------------------ A2 / C15 rounded corners
corners = [k for k in lay["corners"] if k["z"] is not None and k["turn_deg"] >= 55]
corners.sort(key=lambda k: near(k["at"][0], k["at"][1])[0])
big = [k for k in corners if k["turn_deg"] >= 80]
k1 = big[0]
back = 14.0
steps += shot("A2-curva-com-intersecao", "Curva com interseção arredondada",
              (k1["at"][0] + k1["d1"][0] * back, k1["z"], k1["at"][1] + k1["d1"][1] * back), (k1["at"][0], k1["z"] + 1.2, k1["at"][1]), plan,
              f"corner turn {k1['turn_deg']} deg, radius {k1['radius']} m")
k2 = next(k for k in corners if k is not k1 and math.dist(k["at"], k1["at"]) > 30)
steps += shot("C15-conexao-de-rua-corrigida", "Conexão de rua corrigida (canto arredondado contínuo)",
              (k2["at"][0] + k2["d2"][0] * 12, k2["z"], k2["at"][1] + k2["d2"][1] * 12), (k2["at"][0], k2["z"] + 1.2, k2["at"][1]), plan,
              f"corner turn {k2['turn_deg']} deg, radius {k2['radius']} m")

# ------------------------------------------------------------------ A3 street following the relief
best = None
for c in lay["curves"]:
    zz = c["z"]
    if any(z is None for z in zz):
        continue
    pp = c["points"]
    cc = cum(pp)
    for i in range(len(pp)):
        for j in range(i + 1, len(pp)):
            run = cc[j] - cc[i]
            if run < 22 or run > 60:
                continue
            g = abs(zz[j] - zz[i]) / run
            d = near(*pp[i])[0]
            if d < 160 and (best is None or g > best[0]):
                best = (g, c, i, j)
g, c, i, j = best
lo, hi = (i, j) if c["z"][i] < c["z"][j] else (j, i)
steps += shot("A3-rua-acompanhando-relevo", "Rua acompanhando o relevo",
              (c["points"][lo][0], c["z"][lo], c["points"][lo][1]), (c["points"][hi][0], c["z"][hi] + 1.5, c["points"][hi][1]), plan,
              f"grade {g * 100:.1f}% over {abs(cum(c['points'])[j] - cum(c['points'])[i]):.0f} m")

# ------------------------------------------------------------------ A4 / A5 / B7 route-based street views
leg = [p for p in RP if p[3] == "Lar -> rua" or p[3] == "rua -> Oficina"]
p0 = leg[int(len(leg) * .55)]
p1 = leg[min(len(leg) - 1, int(len(leg) * .55) + 14)]
steps += shot("A4-trecho-lar-oficina", "Trecho entre Lar e Oficina", (p0[0], p0[1], p0[2]), (p1[0], p1[1] + 1.5, p1[2]), plan, "route Lar -> Oficina, 55%")
leg = [p for p in RP if p[3] == "rua -> Horizonte"]
p0 = leg[max(0, len(leg) - 24)]
steps += shot("A5-trecho-proximo-horizonte", "Trecho próximo ao Horizonte", (p0[0], p0[1], p0[2]), (-2350.0, 31.0, -1810.0), plan, "route rua -> Horizonte, last 45 m")
leg = [p for p in RP if p[3] == "retorno: Horizonte -> Oficina"]
p0 = leg[int(len(leg) * .3)]
p1 = leg[min(len(leg) - 1, int(len(leg) * .3) + 12)]
steps += shot("B7-rua-com-calcada-legivel", "Rua com calçada legível", (p0[0], p0[1], p0[2]), (p1[0], p1[1] + 1.2, p1[2]), plan, "route return leg 30%")

# ------------------------------------------------------------------ B6 / B9 voids
voids = [v for v in lay["voids"] if v["z"] is not None and not v["green"] and v["family"] == "vacant" and v["w"] >= 10]
voids.sort(key=lambda v: abs(near(v["x"], v["y"])[0] - 22))
v6 = voids[0]
d, p = near(v6["x"], v6["y"])
steps += shot("B6-espaco-entre-predios-acabamento", "Espaço entre prédios (antes cinza) com acabamento", (p[0], p[1], p[2]), (v6["x"], v6["z"] + .8, v6["y"]), plan,
              f"vacant lot {v6['w']}x{v6['d']} m, {d:.0f} m from the route")
greens = [v for v in lay["voids"] if v["z"] is not None and v["green"]]
greens = [v for v in greens if 12 <= near(v["x"], v["y"])[0] <= 45]
greens.sort(key=lambda v: near(v["x"], v["y"])[0])
if greens:
    v9 = greens[0]
    d, p = near(v9["x"], v9["y"])
    steps += shot("B9-grama-canteiro", "Área com grama/canteiro coerente", (p[0], p[1], p[2]), (v9["x"], v9["z"] + .8, v9["y"]), plan, f"pocket green, {d:.0f} m from the route")
else:
    v9 = next(v for v in voids[1:] if v is not v6 and 12 <= near(v["x"], v["y"])[0] <= 45)
    d, p = near(v9["x"], v9["y"])
    steps += shot("B9-grama-canteiro", "Área com grama coerente (terreno vago)", (p[0], p[1], p[2]), (v9["x"], v9["z"] + .8, v9["y"]), plan, "vacant lot (no pocket green near the route)")

# ------------------------------------------------------------------ B8 / C14 entrances
ents = cand["entrances"]
cands = []
for e in ents:
    for d, p in route_points_between(e["x"], e["y"], 7.0, 15.0, -.8, 1.2, ref=e["z"]):
        cands.append((d, e, p))
cands.sort(key=lambda t: abs(t[0] - 10.0))
used = set()
for name, label, lo_, hi_ in (("B8-transicao-rua-calcada-lote", "Transição rua → calçada → lote", 9.0, 15.0), ("C14-fachada-com-porta-legivel", "Fachada com porta/entrada legível", 6.5, 10.0)):
    pick = next((t for t in cands if lo_ <= t[0] <= hi_ and (round(t[1]["x"]), round(t[1]["y"])) not in used), None)
    if pick is None:
        pick = next(t for t in cands if (round(t[1]["x"]), round(t[1]["y"])) not in used)
    d, e, p = pick
    used.add((round(e["x"]), round(e["y"])))
    steps += shot(name, label, (p[0], p[1], p[2]), (e["x"], e["z"] + 1.0, e["y"]), plan, f"entrance (canopy+threshold) {d:.0f} m from a route point")

# ------------------------------------------------------------------ B10 paved forecourt
steps += shot("B10-concreto-piso-coerente", "Piso intertravado/concreto do pátio do Horizonte", (-2350.0, 27.6, -1840.0), (-2350.0, 27.3, -1818.0), plan, "Horizonte forecourt paving seen from the street")

# ------------------------------------------------------------------ C11 / C12 cars on relief
cars = [c for c in cand["cars"]]
cc_ = []
for c in cars:
    for d, p in route_points_between(c["x"], c["y"], 4.0, 11.0, -1.0, 1.5, ref=c["z"]):
        cc_.append((d, c, p))
by_pitch = sorted(cc_, key=lambda t: -abs(t[1]["pitch_deg"]))
d, c, p = by_pitch[0]
steps += shot("C11-carro-apoiado-rua-com-relevo", "Carro corretamente apoiado em rua com relevo", (p[0], p[1], p[2]), (c["x"], c["z"] + .7, c["y"]), plan,
              f"car pitch {c['pitch_deg']} deg roll {c['roll_deg']} deg, {d:.0f} m from the route")
rest = [t for t in cc_ if math.dist((t[1]["x"], t[1]["y"]), (c["x"], c["y"])) > 25]
by_roll = sorted(rest, key=lambda t: -(abs(t[1]["roll_deg"]) * 2 + abs(t[1]["pitch_deg"])))
d, c2, p = by_roll[0]
steps += shot("C12-outro-carro-em-area-inclinada", "Outro carro em área inclinada", (p[0], p[1], p[2]), (c2["x"], c2["z"] + .7, c2["y"]), plan,
              f"car pitch {c2['pitch_deg']} deg roll {c2['roll_deg']} deg, {d:.0f} m from the route")

# ------------------------------------------------------------------ C13 roof close-up
rc = []
for r in cand["roofs"]:
    for d, p in route_points_between(r["x"], r["y"], 10.0, 24.0, 2.0, 9.0, ref=r["z"]):
        rc.append((d, r, p))
rc.sort(key=lambda t: (0 if "colonial" in t[1]["kind"] else 1, t[0]))
d, r, p = rc[0]
steps += shot("C13-telhado-cobertura-corrigido", "Telhado/cobertura corrigido em vista próxima", (p[0], p[1], p[2]), (r["x"], r["z"] + .4, r["y"]), plan,
              f"{r['kind']} roof piece, {d:.0f} m from the route")

# ------------------------------------------------------------------ D: same-coordinate candidates (junction ends of bowed chains + hero fronts)
dplan = {}
chains = sorted([c for c in lay["curves"] if c["cls"] == "local" and c["amp"] >= 3.5 and all(z is not None for z in c["z"])], key=chain_dist)
picked = []
for c in chains:
    if all(math.dist(c["points"][0], q["points"][0]) > 45 for q in picked):
        picked.append(c)
    if len(picked) == 6:
        break
for k, c in enumerate(picked):
    pp, zz = c["points"], c["z"]
    mid = ((pp[0][0] + pp[-1][0]) / 2, (pp[0][1] + pp[-1][1]) / 2)
    nm = f"D{k + 1:02d}-curva-extremidade"
    for dest in (steps_d_after, steps_d_before):
        dest += shot(nm, "Início de rua que foi curvada", (pp[0][0], zz[0], pp[0][1]), (mid[0], zz[0] + 1.5, mid[1]), dplan, f"chain {c['length']} m, bow {c['amp']} m; same coordinates in both builds")
hero_spots = [("D07-lar-frente", (-2860.0, 17.65, -2266.0), (-2860.0, 20.5, -2285.0)),
              ("D08-oficina-frente", (-2692.0, 20.9, -2146.0), (-2692.0, 22.0, -2128.0)),
              ("D09-horizonte-rua", (-2350.0, 27.05, -1831.0), (-2350.0, 33.0, -1805.0)),
              ("D10-mercearia-frente", (-2598.0, 24.7, -1485.0), (-2598.0, 26.5, -1470.0))]
for nm, cam, aim in hero_spots:
    for dest in (steps_d_after, steps_d_before):
        dest += shot(nm, "Frente de herói (mesmas coordenadas nos dois builds)", cam, aim, dplan, "stable hero front")


def write_route(path, steps_list, note):
    path.write_text(json.dumps({"version": 1, "note": note, "steps": steps_list}, indent=1), encoding="utf-8")


write_route(ROOT / "FacilityOps/Assets/StreamingAssets/world-evidence-route.json", steps + steps_d_after, "W3.2.x evidence: A-C (new build) + D after candidates")
write_route(ROOT / "Logs" / "evidence-route-before.json", steps_d_before, "W3.2.x D before candidates (old build, same coordinates)")
(ROOT / "Logs" / "evidence-plan.json").write_text(json.dumps({"abc": plan, "d": dplan}, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v["note"] for k, v in {**plan, **dplan}.items()}, indent=1, ensure_ascii=False))
