"""Grand Aurora: the final 5-star resort of Resort Aurora, modelled on the real P5 platô terraces of the Bairro das Palmeiras.

blender --background --factory-startup --python Tools/Blender/create_grand_aurora.py -- --root PROJECT_ROOT [--render] [--night]

Reads the exported site (FacilityOps/Assets/_Game/Resources/Resort/ResortSite.json + ResortSiteHeights.bytes), so the blend lines up with
the Unity map (Blender X/Y/Z = Unity x/z/y). Writes ArtSource/Blender/Resort/SantaAurora_GrandAurora_v1.blend and a report.
Massing is modelled with real architectural detail (balconies, glass rails, brise-soleil, colonnades, lantern crown); see Docs/GRAND_AURORA_MODELAGEM.md.
"""
import argparse
import json
import math
import random
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--render", action="store_true")
parser.add_argument("--night", action="store_true")
parser.add_argument("--only", default="", help="render only cameras whose name contains this")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Blender"))
sys.path.insert(0, str(root / "Tools" / "Map"))

import sa_bl  # noqa: E402
import sa_detail  # noqa: E402
import sa_materials  # noqa: E402
import sa_resort as R  # noqa: E402
import sa_vegetation  # noqa: E402
from sa_resort import S  # noqa: E402

res_dir = root / "FacilityOps" / "Assets" / "_Game" / "Resources" / "Resort"
site = json.loads((res_dir / "ResortSite.json").read_text(encoding="utf-8"))
NX, NZ, STEP = site["columns"], site["rows"], site["step"]
raw = (res_dir / "ResortSiteHeights.bytes").read_bytes()
H = struct.unpack("<%df" % (NX * NZ), raw)


def height_at(x, y):
    fx, fy = max(0.0, min(x / STEP, NX - 1.001)), max(0.0, min(y / STEP, NZ - 1.001))
    i, j = int(fx), int(fy)
    tx, ty = fx - i, fy - j
    a, b, c, d = H[j * NX + i], H[j * NX + i + 1], H[(j + 1) * NX + i], H[(j + 1) * NX + i + 1]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


sa_bl.clear_scene()
scene = bpy.context.scene
scene.name = "SantaAurora_GrandAurora"
scene.unit_settings.system = "METRIC"
lib = sa_materials.build_library()
sa_detail.extend_library(lib)
R.extend_library(lib)
MATS = R.materials_for(lib)

top = sa_bl.collection("GrandAurora")
coll = {n: sa_bl.collection(n, top) for n in ("Terreno", "Contexto", "Arquitetura", "Agua", "Paisagem", "Cameras")}

# ------------------------------------------------------------------------------------------------ site layout (platô frame)
P5 = next(p for p in site["parcels"] if p["id"] == "P5")
TERR = [t for t in site["terraces"] if t["parcel"] == "P5"]
TERR.sort(key=lambda t: t["z"])
OX, OY = P5["x"], P5["z"]
W = P5["width"]
TH = [t["height"] for t in TERR]                       # terrace surface heights T1..T4 (south to north)
TV = [i * 40.0 for i in range(5)]                      # terrace boundaries in v


def X(u):
    return OX + u


def Y(v):
    return OY + v


def Z_of_v(v):
    return TH[min(3, max(0, int(v // 40.0)))]


# ------------------------------------------------------------------------------------------------ terrain (vertex colours)
def terrain_object():
    verts, faces, cols = [], [], []
    road_ns = site["streetsNS"]
    for j in range(NZ):
        for i in range(NX):
            x, y, z = i * STEP, j * STEP, H[j * NX + i]
            verts.append((x, y, z))
            prom = _prom_z(x)
            if abs(y - prom) < 6:
                c = (.62, .60, .55)
            elif abs(y - site["avenue"]["z"]) < site["avenue"]["width"] / 2 or any(abs(y - s["z"]) < s["width"] / 2 for s in site["streetsEW"]) \
                    or any(s["from"] <= y <= s["to"] and abs(x - s["x"]) < s["width"] / 2 for s in road_ns):
                c = (.09, .09, .10)
            elif z < 0.5:
                t = max(0.0, min(1.0, (z + 1.0) / 1.5))
                c = (.50 + .30 * t, .42 + .27 * t, .30 + .20 * t)
            elif z < 3.2:
                c = (.78, .68, .50)
            else:
                t = max(0.0, min(1.0, (z - 3.2) / 2.5))
                n = (math.sin(x * .13) * math.cos(y * .11)) * .03
                c = (.62 - .40 * t + n, .54 - .22 * t + n, .38 - .27 * t + n)
            cols.append(c)
    for j in range(NZ - 1):
        for i in range(NX - 1):
            a = j * NX + i
            faces.append((a, a + 1, a + NX + 1, a + NX))
    me = bpy.data.meshes.new("Terreno")
    me.from_pydata(verts, [], faces)
    me.update()
    me.shade_smooth()
    ca = me.color_attributes.new(name="Col", type="FLOAT_COLOR", domain="POINT")
    for k, c in enumerate(cols):
        ca.data[k].color = (c[0], c[1], c[2], 1.0)
    mat = bpy.data.materials.new("terreno_cores")
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    attr = nt.nodes.new("ShaderNodeVertexColor")
    attr.layer_name = "Col"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.92
    noise = nt.nodes.new("ShaderNodeTexNoise")                           # breaks up the flat vertex colour (mowing, patchiness)
    noise.inputs["Scale"].default_value = 0.35
    noise.inputs["Detail"].default_value = 6.0
    mapn = nt.nodes.new("ShaderNodeMapRange")
    mapn.inputs["To Min"].default_value = 0.78
    mapn.inputs["To Max"].default_value = 1.18
    nt.links.new(noise.outputs["Fac"], mapn.inputs["Value"])
    mulc = nt.nodes.new("ShaderNodeMix")
    mulc.data_type = "RGBA"
    mulc.blend_type = "MULTIPLY"
    mulc.inputs["Factor"].default_value = 1.0
    nt.links.new(attr.outputs["Color"], mulc.inputs["A"])
    nt.links.new(mapn.outputs["Result"], mulc.inputs["B"]) if False else None
    grey = nt.nodes.new("ShaderNodeCombineColor")
    for ch in ("Red", "Green", "Blue"):
        nt.links.new(mapn.outputs["Result"], grey.inputs[ch])
    nt.links.new(grey.outputs["Color"], mulc.inputs["B"])
    nt.links.new(mulc.outputs["Result"], bsdf.inputs["Base Color"])
    me.materials.append(mat)
    o = bpy.data.objects.new("Terreno", me)
    coll["Terreno"].objects.link(o)
    return o


def _prom_z(x):
    p = site["promenade"]
    if x <= p[0]["x"]:
        return p[0]["z"]
    for k in range(1, len(p)):
        if x <= p[k]["x"]:
            t = (x - p[k - 1]["x"]) / max(1e-6, p[k]["x"] - p[k - 1]["x"])
            return p[k - 1]["z"] + t * (p[k]["z"] - p[k - 1]["z"])
    return p[-1]["z"]


terrain_object()

sea = bpy.data.objects.new("Mar", bpy.data.meshes.new("Mar"))
sea.data.from_pydata([(-1500, -900, 0), (2500, -900, 0), (2500, 80, 0), (-1500, 80, 0)], [], [(0, 1, 2, 3)])
sea.data.materials.append(lib["agua_mar"])
coll["Terreno"].objects.link(sea)

# context: the vila as massing (real lot data) so the resort sits in its neighbourhood
mbv = sa_bl.MeshBuilder()
wall_idx = [0, 1, 2, 3]
for l in site["lots"]:
    z0 = min(height_at(l["x"] - l["w"] / 2, l["z"]), height_at(l["x"] + l["w"] / 2, l["z"])) - 0.8
    mbv.box(l["x"], l["z"], z0, l["w"], l["d"], l["h"] + 0.8, wall_idx[l["c"] % 4], math.radians(l["rot"]))
    mbv.box(l["x"], l["z"], z0 + l["h"] + 0.8, l["w"] + .5, l["d"] + .5, .35, 4, math.radians(l["rot"]))
vmats = [lib["reboco_pintado"], lib["concreto_pintado"], lib["reboco_antigo"], lib["reboco_pastilha"], lib["ceramica_telha"]]
mbv.to_object("Vila", vmats, coll["Contexto"])

# ------------------------------------------------------------------------------------------------ architecture
arch = {k: sa_bl.MeshBuilder() for k in ("T1", "T2", "T3", "T4", "Eixo", "Tower")}
water = sa_bl.MeshBuilder()
land = sa_bl.MeshBuilder()          # foliage / shrubs (folhagem)
flowers = sa_bl.MeshBuilder()       # bougainvillea masses (buganvile)
trunks = sa_bl.MeshBuilder()
fronds = sa_bl.MeshBuilder()
stats = {"wings": 0, "villas": 0, "pools": 0, "palms": 0, "arches": 0}
TB = [0.0, 39.0, 81.0, 120.0, 189.0]         # terrace boundaries (v)


def frame(group, u, v, angle=0.0):
    return R.Frame(arch[group], (X(u), Y(v)), angle)


def waterquad(u0, v0, u1, v1, z):
    water.quad((X(u0), Y(v0), z), (X(u1), Y(v0), z), (X(u1), Y(v1), z), (X(u0), Y(v1), z), 0)


rng = random.Random(7)
t1, t2, t3, t4 = TH

# ---- terrace pavings: every terrace gets a travertine/marble plaza skeleton so the resort reads as built, not as lawn with boxes
for n in range(4):
    z = TH[n]
    mb = arch["T%d" % (n + 1)]
    v0, v1 = TB[n], TB[n + 1]
    cxm = X(W / 2)
    mb.box(cxm, Y((v0 + v1) / 2), z - 0.03, 52.0, v1 - v0, 0.05, S["travertino"], top=True)          # central promenade (the axis)
    for u in (4.0, 212.0):
        mb.box(X(u + 12), Y((v0 + v1) / 2), z - 0.03, 24.0, v1 - v0, 0.05, S["travertino"], top=True)  # side garden promenades

# ---- retaining arcades with the central water stair (3 walls between terraces)
for n in (1, 2, 3):
    v = TB[n] - 0.75                                                         # wall sits in the middle of the 1.5 m step cell
    zl, zh = TH[n - 1], TH[n]
    for (u0, u1) in ((0, 96), (144, W)):
        Lw = u1 - u0
        cnt = max(2, int(round(Lw / 6.0)))
        fw = R.Frame(arch["Eixo"], (X(u0), Y(v)), 0.0)
        R.arcade(fw, Lw, cnt, zl, zh)
        fw.box(0, Lw, 0.9, 1.4, zl, zh + 0.1, S["estuque"])                     # dark-ish back wall behind the arches (blind arcade)
        stats["arches"] += cnt
    for (u0, u1) in ((96, 112), (128, 144)):
        fs = R.Frame(arch["Eixo"], (X(u0), Y(v - 8.0)), 0.0)
        R.stairs(fs, u1 - u0, 8.0, zl, zh)
    # cascade between the stairs: stepped weirs + the falling sheet + the lower basin
    waterquad(112, v - 0.02, 128, v + 0.02, zh - 0.07)
    water.quad((X(112), Y(v), zh - 0.07), (X(128), Y(v), zh - 0.07), (X(128), Y(v - 0.06), zl - 0.07), (X(112), Y(v - 0.06), zl - 0.07), 0)
    water.quad((X(112), Y(v - 0.06), zl - 0.07), (X(128), Y(v - 0.06), zl - 0.07), (X(128), Y(v), zh - 0.07), (X(112), Y(v), zh - 0.07), 0)   # back face (single-sided in the engine)
    fb = R.Frame(arch["Eixo"], (X(111), Y(v - 8.0)), 0.0)
    fb.box(0, 18, 0, 7.4, zl - 1.0, zl - 0.1, S["azulejo"], top=False)
    fb.box(-0.5, 0.0, 0, 8.0, zl - 1.0, zl + 0.35, S["travertino"])
    fb.box(18, 18.5, 0, 8.0, zl - 1.0, zl + 0.35, S["travertino"])
    fb.box(-0.5, 18.5, 7.4, 8.0, zl - 1.0, zh - 0.1, S["basalto"])
    waterquad(112, v - 8.0, 128, v - 0.6, zl - 0.12)
    stats["pools"] += 1

# ---- reflecting canals along the axis and formal gardens
R.pool(arch["T2"], water, X(111), Y(42), X(129), Y(71), t2, depth=1.0)
R.pool(arch["T4"], water, X(111), Y(122), X(129), Y(129), t4, depth=1.0)
for (u0, w_) in ((70, 24), (146, 24)):
    R.parterre(frame("T4", u0, 122), w_, 6, t4 + 0.0, flowers, seed=u0)
for (u0, w_) in ((8, 48), (184, 48)):
    R.parterre(frame("T1", u0, 20), w_, 14, t1 + 0.0, flowers, seed=u0 + 1)
for (u0, w_) in ((82, 24), (134, 24)):
    R.parterre(frame("T2", u0, 74), w_, 5, t2 + 0.0, flowers, seed=u0 + 2)

# ---- T4: arrival terrace (z=15.8): Grand Hall + Torre Aurora + wings + fountain court
lobby_top = R.lobby(frame("T4", 75, 132), 90, 24, t4, H=13.0)
tower_top = R.tower(frame("Tower", 98, 156), 44, 16, t4 + 0.9, floors=18, fh=3.3)
for u0, L, v0, fl, d in ((6, 62, 134, 5, 18), (172, 62, 134, 5, 18), (6, 52, 164, 7, 18), (182, 52, 164, 7, 18)):
    R.wing(frame("T4", u0, v0), L, d, t4, fl, seed=u0 + v0)
    stats["wings"] += 1
# porte-cochère: broad canopy on slender bronze columns north of the tower, drive and fountain court
fn = frame("T4", 92, 172)
fn.box(0, 56, 0, 14, t4, t4 + 0.4, S["travertino"], bottom=True)
for k in range(7):
    fn.cyl(k * 9.3, 12.5, t4, 0.35, 6.4, 16, S["estuque"])
    fn.cyl(k * 9.3, 1.5, t4, 0.35, 6.4, 16, S["estuque"])
fn.box(-3, 59, -1, 15.5, t4 + 6.4, t4 + 6.9, S["concreto"], bottom=True)
fn.box(-3.1, 59.1, -1.1, 15.6, t4 + 6.9, t4 + 7.15, S["latao"])
fnt = frame("T4", 120, 184)
fx, fy, fz, fr_ = R.fountain(fnt, 0, 0, t4, r=6.0)
water.add_face([(fx + (fr_ - 0.1) * math.cos(2 * math.pi * k / 28), fy + (fr_ - 0.1) * math.sin(2 * math.pi * k / 28), fz) for k in range(28)], 0)
for k in range(10):
    ang = 2 * math.pi * k / 10
    R.lamp(frame("T4", 120 + 13.0 * math.cos(ang), 184 + 13.0 * math.sin(ang)), 0, 0, t4)
mbT = arch["T4"]
mbT.box(X(120), Y(184), t4 - 0.04, 36, 30, 0.04, S["marmore"], top=True)                          # arrival court paving
for k in range(14):
    R.lamp(frame("T4", 24 + k * 16, 128), 0, 0, t4, h=3.6)

# ---- T3 (z=12.7): lagoon, restaurant, event hall, wings
for u0, L in ((6, 74), (160, 74)):
    R.wing(frame("T3", u0, 100), L, 16, t3, 4, seed=u0 + 3, pitched=True)
    stats["wings"] += 1
R.lobby(frame("T3", 14, 84), 52, 11, t3, H=6.5)                                                   # Restaurante Horizonte (pavilion)
R.lobby(frame("T3", 174, 84), 52, 11, t3, H=6.5)                                                  # Salão de Eventos
R.pool(arch["T3"], water, X(84), Y(84), X(156), Y(112), t3, depth=1.6)
stats["pools"] += 1
R.pergola(frame("T3", 84, 78), 72, 5, t3, h=3.2, canopy=True)
arch["T3"].box(X(120), Y(98), t3 - 1.5, 20, 9, 1.6, S["travertino"])                              # island + palapa
R.thatch_roof(frame("T3", 120, 98), 0, 0, t3 + 3.6, 6.0, 3.2)
for k in range(14):
    R.lounger(frame("T3", 84 + k * 5.0, 112.6), 0, 0, t3)
for k in range(6):
    R.umbrella(frame("T3", 90 + k * 12.0, 114.8), 0, 0, t3)

# ---- T2 (z=9.6): spa, reflecting canals, wings
for u0, L in ((6, 66), (168, 66)):
    R.wing(frame("T2", u0, 58), L, 16, t2, 3, seed=u0 + 5, pitched=True)
    stats["wings"] += 1
R.villa(frame("T2", 88, 58), 64, 14, t2, seed=2)                                                  # Spa Maré
R.pool(arch["T2"], water, X(30), Y(46), X(70), Y(54), t2, depth=1.2)
R.pool(arch["T2"], water, X(170), Y(46), X(210), Y(54), t2, depth=1.2)
stats["pools"] += 2

# ---- T1 (z=6.5): beach club, infinity pool, bangalôs
R.pool(arch["T1"], water, X(58), Y(8), X(182), Y(30), t1, depth=1.6, infinity_side="s")
stats["pools"] += 1
for k in range(14):
    R.lounger(frame("T1", 62 + k * 8.4, 31.0), 0, 0, t1)
for k in range(8):
    R.umbrella(frame("T1", 66 + k * 14.0, 36.0), 0, 0, t1)
for k in range(8):                                                                                # bangalôs, four each side
    u = (8 + k * 12.5) if k < 4 else (190 + (k - 4) * 12.5 - 8)
    R.villa(frame("T1", u, 10), 11, 8, t1, seed=k)
    pu = u + 1.5
    R.pool(arch["T1"], water, X(pu), Y(-6), X(pu + 6), Y(-2.6), t1, depth=1.2)
    stats["villas"] += 1
for k in range(11):                                                                               # palapas along the south edge
    f = frame("T1", 60 + k * 11.5, 2)
    f.box(-1.6, 1.6, -1.2, 1.6, t1, t1 + 0.12, S["teca"])
    R.thatch_roof(f, 0, 0.2, t1 + 2.8, 2.7, 1.8)
bar = frame("T1", 30, 26)
R.lobby(bar, 22, 9, t1, H=4.4)                                                                    # beach bar pavilion

# ---- skyline accents: campaniles flanking the Grand Hall, rotundas at the arrival, domed massage pavilions on T2
for u in (71.5, 168.5):
    R.campanile(frame("T4", u, 142), 0, 0, t4, w=7.0, h=27.0)
for u in (84.0, 156.0):
    fq = frame("T4", u, 176)
    fq.box(-6, 6, -6, 6, t4, t4 + 0.5, S["marmore"], bottom=True)
    R.dome(fq, 0, 0, t4 + 0.5, r=4.6, drum_h=3.4)
for u in (20.0, 220.0):
    fq = frame("T2", u, 48)
    fq.box(-11, 11, -11, 11, t2, t2 + 0.5, S["travertino"], bottom=True)
    R.dome(fq, 0, 0, t2 + 0.5, r=8.0, drum_h=5.0)
    for k in range(10):
        a = 2 * math.pi * k / 10
        fq.cyl(9.6 * math.cos(a), 9.6 * math.sin(a), t2 + 0.5, 0.3, 5.0, 12, S["estuque"])
# north retaining wall and balustrade of the arrival terrace (the hill falls away behind the resort)
fnw = frame("T4", 0, 189.0)
fnw.box(0, W, 0, 1.2, t4 - 9.0, t4, S["travertino"])
fnw.box(-0.1, W + 0.1, -0.1, 1.3, t4, t4 + 0.2, S["marmore"])
for k in range(int(W // 0.55)):
    fnw.box(k * 0.55 + 0.1, k * 0.55 + 0.3, 0.1, 0.5, t4 + 0.2, t4 + 0.9, S["marmore"], top=False)
fnw.box(-0.1, W + 0.1, 0.0, 0.6, t4 + 0.9, t4 + 1.0, S["marmore"])

# ------------------------------------------------------------------------------------------------ landscape
for n in range(4):                                                                                # royal palm alley, 2 rows per terrace
    for k in range(8):
        v = TB[n] + 4.5 + k * (35.0 / 7 if n < 3 else 11.0)
        if v > TB[n + 1] - 3:
            continue
        for u in (89.0, 151.0):
            R.palm_royal(trunks, fronds, (X(u), Y(v), TH[n]), h=rng.uniform(11, 15), lean=(rng.uniform(-.02, .02), rng.uniform(-.02, .02)), seed=int(u + v * 7), crown=5.4)
            stats["palms"] += 1
for k in range(16):                                                                               # palm alley continuing south to the avenue
    v = -4 - k * 11.0
    for u in (89.0, 151.0):
        R.palm_royal(trunks, fronds, (X(u), Y(v), height_at(X(u), Y(v))), h=rng.uniform(12, 15), seed=int(u + v), crown=5.4)
        stats["palms"] += 1
for k in range(60):                                                                               # scattered palms in the garden bands
    n = rng.randrange(4)
    u = rng.choice((rng.uniform(4, 82), rng.uniform(158, 236)))
    v = rng.uniform(TB[n] + 3, TB[n + 1] - 3)
    R.palm_royal(trunks, fronds, (X(u), Y(v), TH[n]), h=rng.uniform(7, 12), lean=(rng.uniform(-.05, .05), rng.uniform(-.05, .05)), seed=k * 13, crown=4.6)
    stats["palms"] += 1
for n in range(4):                                                                                # shrub masses + bougainvillea along walls and paths
    for k in range(70):
        u = rng.uniform(3, W - 3)
        if 94 < u < 146:
            continue
        v = TB[n] + rng.uniform(1.5, TB[n + 1] - TB[n] - 1.5)
        target = flowers if rng.random() < 0.28 else land
        R.blob(target, (X(u), Y(v), TH[n] + 0.3), rng.uniform(.7, 1.7), 0, seed=n * 100 + k)
    for k in range(40):                                                                           # clipped hedges along the arcade foot
        u = rng.uniform(2, W - 2)
        if 92 < u < 148:
            continue
        R.blob(land, (X(u), Y(TB[n] + 2.0), TH[n] + 0.4), 1.0, 0, seed=900 + n * 50 + k)

crowns = sa_bl.MeshBuilder()
for k in range(46):                                                                              # shade trees: garden bands, side lawns and the avenue approach
    n = rng.randrange(4)
    u = rng.choice((rng.uniform(4, 60), rng.uniform(180, 236)))
    v = rng.uniform(TB[n] + 4, TB[n + 1] - 4)
    R.shade_tree(trunks, crowns, (X(u), Y(v), TH[n]), h=rng.uniform(5.5, 8.5), r=rng.uniform(3.4, 5.0), seed=k)
for k in range(16):
    u = rng.uniform(-30, 270)
    v = rng.uniform(-60, -8)
    R.shade_tree(trunks, crowns, (X(u), Y(v), height_at(X(u), Y(v))), h=rng.uniform(6, 9), r=rng.uniform(3.6, 5.2), seed=100 + k)

# ------------------------------------------------------------------------------------------------ materialise objects
for name, mb in arch.items():
    if len(mb):
        mb.to_object("Arq_" + name, MATS, coll["Arquitetura"])
if len(water):
    water.to_object("Agua", [lib["agua_piscina"]], coll["Agua"])
if len(land):
    land.to_object("Arbustos", [lib["folhagem"]], coll["Paisagem"])
if len(crowns):
    crowns.to_object("Arvores_copas", [lib["folhagem"]], coll["Paisagem"], smooth=True)
if len(flowers):
    flowers.to_object("Buganvilias", [lib["buganvile"]], coll["Paisagem"])
if len(trunks):
    trunks.to_object("Palmeiras_troncos", [lib["tronco"]], coll["Paisagem"], smooth=True)
if len(fronds):
    fronds.to_object("Palmeiras_folhas", [lib["folhagem"]], coll["Paisagem"], smooth=True)

# ------------------------------------------------------------------------------------------------ light, cameras, render
night = opts.night
sun = sa_bl.production_look(scene, coll["Cameras"], elevation_deg=14 if night else 24, azimuth_deg=235, sun_energy=0.4 if night else 5.0,
                            sky_strength=0.04 if night else 0.35, exposure=0.0 if night else -1.2, haze=0.0)
# interior fills (the hall reads lit inside from outside, day and night)
for name, (lx_, ly_, lz_, en) in {"hall": (X(120), Y(142), t4 + 8.0, 4000 if night else 1800), "hall_w": (X(92), Y(142), t4 + 6.0, 1500), "hall_e": (X(148), Y(142), t4 + 6.0, 1500)}.items():
    ld = bpy.data.lights.new("LUZ_" + name, "POINT")
    ld.energy = en
    ld.color = (1.0, .82, .6)
    ld.shadow_soft_size = 2.0
    lo = bpy.data.objects.new("LUZ_" + name, ld)
    lo.location = (lx_, ly_, lz_)
    coll["Cameras"].objects.link(lo)
if night:
    lib["luz_quente"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 18.0
    vg = lib["vidro"].node_tree.nodes["Principled BSDF"]                              # lit rooms behind the glass
    vg.inputs["Emission Color"].default_value = (1.0, .78, .5, 1)
    vg.inputs["Emission Strength"].default_value = 1.6
cx = X(W / 2)
cams = {
    "01_aerea_mar": ((cx + 30, Y(-170), 90), (cx, Y(110), 20), 28),
    "02_aerea_alta": ((cx - 200, Y(-60), 110), (cx, Y(100), 15), 32),
    "03_eixo_central": ((cx, Y(-14), TH[0] + 1.7), (cx, Y(160), TH[3] + 10), 22),
    "04_lobby_frente": ((cx + 20, Y(100), TH[2] + 1.7), (cx, Y(140), TH[3] + 8), 24),
    "05_piscina_infinita": ((X(40), Y(-10), TH[0] + 1.6), (X(120), Y(60), TH[1] + 12), 22),
    "06_torre": ((cx + 90, Y(30), TH[1] + 1.8), (cx, Y(160), TH[3] + 30), 30),
    "07_chegada": ((cx, Y(215), TH[3] + 1.7), (cx, Y(160), TH[3] + 12), 20),
    "08_aerea_noroeste": ((X(-60), Y(230), 80), (cx, Y(90), 15), 30),
}
for name, (loc, tgt, lens) in cams.items():
    sa_bl.camera("CAM_" + name, coll["Cameras"], loc, target=tgt, lens=lens, clip=(0.5, 6000.0))

out_dir = root / "ArtSource" / "Blender" / "Resort"
out_dir.mkdir(parents=True, exist_ok=True)
blend = out_dir / ("SantaAurora_GrandAurora_v1_noite.blend" if night else "SantaAurora_GrandAurora_v1.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
tris = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
report = {"blend": blend.relative_to(root).as_posix(), "polygons": tris, "stats": stats, "terraceHeights": TH, "platoOrigin": [OX, OY]}
(out_dir / "grand_aurora_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("GRAND AURORA", json.dumps(report))

if opts.render:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 90
    shots = out_dir / ("Capturas_noite" if night else "Capturas")
    shots.mkdir(exist_ok=True)
    for ob in [o for o in coll["Cameras"].objects if o.type == "CAMERA"]:
        if opts.only and opts.only not in ob.name:
            continue
        scene.camera = ob
        scene.render.filepath = str(shots / (ob.name[4:] + ".jpg"))
        bpy.ops.render.render(write_still=True)
        print("rendered", ob.name)
