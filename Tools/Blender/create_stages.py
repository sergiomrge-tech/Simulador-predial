"""Resort Aurora - the seven stages of evolution on the same land: beach stall -> kiosk -> restaurant + pousada -> hotel -> complex ->
resort under construction -> Grand Aurora. One blend; every object carries st_from/st_to and the render loop shows only what exists at each stage.

blender --background --factory-startup --python Tools/Blender/create_stages.py -- --root PROJECT_ROOT [--render] [--stages 1,2,...]
Needs ArtSource/Blender/Resort/SantaAurora_GrandAurora_v1.blend (stage 6/7 reuse its platô geometry).
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--render", action="store_true")
parser.add_argument("--stages", default="1,2,3,4,5,6,7")
parser.add_argument("--samples", type=int, default=48)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_bl  # noqa: E402
import sa_detail  # noqa: E402
import sa_materials  # noqa: E402
import sa_resort as R  # noqa: E402
import sa_site  # noqa: E402
import sa_stages as ST  # noqa: E402
from sa_resort import S  # noqa: E402

site = sa_site.Site(root)
sa_bl.clear_scene()
scene = bpy.context.scene
scene.name = "ResortAurora_Estagios"
lib = sa_materials.build_library()
sa_detail.extend_library(lib)
R.extend_library(lib)
MATS = R.materials_for(lib)
top = sa_bl.collection("Estagios")
cn = {n: sa_bl.collection(n, top) for n in ("Terreno", "Contexto", "Edificios", "Paisagem", "Cameras")}

# ------------------------------------------------------------------------------------------------ terrain + context
for o, (a, b) in ((site.terrain_object("Terreno_natural", True, cn["Terreno"]), (1, 5)), (site.terrain_object("Terreno_terraceado", False, cn["Terreno"]), (6, 7))):
    o["st_from"], o["st_to"] = a, b
site.sea(lib, cn["Terreno"])
site.vila(lib, cn["Contexto"])

# ------------------------------------------------------------------------------------------------ element builders
pieces = {}


def mbk(a, b, name):
    key = (a, b, name)
    if key not in pieces:
        pieces[key] = sa_bl.MeshBuilder()
    return pieces[key]


def fr(a, b, name, x, y, angle=0.0):
    return R.Frame(mbk(a, b, name), (x, y), angle)


def gz(x, y):
    return site.height_at(x, y, True)


PI = math.pi
X0 = 450.0
promZ = site.prom_z(X0)

# --- 1: the stall (P0) on the promenade's seaward edge, counter facing the walkers (north)
sy = promZ - 7.2
ST.stall(fr(1, 1, "barraca", X0, sy, PI), gz(X0, sy))
for k in range(5):                                                      # a few parasols on the sand, a bench on the promenade
    ux = X0 - 30 + k * 14
    uy = promZ - 24 - (k % 2) * 8
    R.umbrella(fr(1, 7, "guardasois", ux, uy), 0, 0, gz(ux, uy), r=1.8, h=2.7)
    fr(1, 7, "guardasois", ux, uy).box(-0.4, 0.4, -0.8, 0.8, gz(ux, uy), gz(ux, uy) + 0.1, S["tecido"])

# --- 2-5: the kiosk (P1)
ST.kiosk(fr(2, 7, "quiosque", X0, sy, PI), gz(X0, sy))

# --- 3-5: covered restaurant beside the kiosk; the Seu Tonico pousada (P2)
ry = 232.0
R.lobby(fr(3, 5, "restaurante", 472, ry), 30, 9, gz(472, ry), H=5.0)
py = 342.0
ST.sobrado(fr(3, 7, "pousada", 386, py), gz(386, py), L=16, D=11, seed=1)

# --- 4-7: the hotel block on P3 with its pool court
hy = 346.0
ST.hotel_block(fr(4, 7, "hotel", 430, hy), gz(430, hy), L=60, floors=5, seed=4)
R.pool(mbk(4, 7, "hotel_piscina"), mbk(4, 7, "hotel_agua"), 436, 368, 470, 380, gz(450, 372) + 0.0, depth=1.4)
for k in range(8):
    R.lounger(fr(4, 7, "hotel_deck", 438 + k * 4.0, 382.0), 0, 0, gz(450, 382))

# --- 5-7: the complex: events hall, spa, beach bangalôs
ev = fr(5, 7, "complexo", 482, 372)
R.lobby(ev, 40, 14, gz(482, 372) + 0.0, H=7.0)
R.villa(fr(5, 7, "spa", 336, 318), 40, 12, gz(336, 318), seed=2)
for k in range(6):
    vx, vy = 404 + k * 18, 196.0
    R.villa(fr(5, 7, "bangalos", vx, vy), 11, 8, gz(vx, vy), seed=k)

# --- the player's home: Edificio Santa Clara, Apto 12 (kitnet), a short walk from the stall
ST.lar(fr(1, 7, "lar", 324.0, 341.0), gz(324.0, 341.0))

# --- the Grande Hotel Palmeiras (P4): ruin until stage 5, restored from stage 6
gy = 358.0
ST.grand_hotel(fr(1, 5, "grande_hotel_ruina", 505, gy), gz(550, gy), ruin=True)
ST.grand_hotel(fr(6, 7, "grande_hotel", 505, gy), gz(550, gy), ruin=False)

# --- the lighthouse on the headland (P6): dark until the final night
lx, ly = 835.0, 300.0
ST.lighthouse(fr(1, 6, "farol", lx, ly), 0, 0, gz(lx, ly) + 0.0, lit=False)
ST.lighthouse(fr(7, 7, "farol_aceso", lx, ly), 0, 0, gz(lx, ly) + 0.0, lit=True)

# --- stage 6: crane + concrete frame of the next wings on the platô
cr = fr(6, 6, "grua", 330 + 150, 480 + 150)
ST.crane(cr, 0, 0, 15.5 + 0.0, h=46.0, boom=44.0)
for (u0, v0, fl) in ((330 + 8, 480 + 134, 3), (330 + 172, 480 + 134, 2)):
    f = fr(6, 6, "estrutura", u0, v0)
    for fi in range(fl):
        z = 15.8 + fi * 3.4
        f.box(0, 62, -2.2, 16, z, z + 0.3, S["concreto"], bottom=True)
        for k in range(14):
            f.box(k * 4.8, k * 4.8 + 0.5, -2.0, -1.5, z + 0.3, z + 3.4, S["concreto"])
            f.box(k * 4.8, k * 4.8 + 0.5, 15.0, 15.5, z + 0.3, z + 3.4, S["concreto"])

# --- promenade palms: royal palms in a row, growing with the years
trunks, fronds = mbk(1, 7, "palmeiras_tronco"), mbk(1, 7, "palmeiras_folha")
rng = random.Random(11)
for k in range(26):
    px = 330 + k * 12.0
    py2 = site.prom_z(px) + 8.0
    R.palm_royal(trunks, fronds, (px, py2, gz(px, py2)), h=rng.uniform(9, 13), lean=(rng.uniform(-.03, .03), rng.uniform(-.03, .03)), seed=k, crown=4.8)

# ------------------------------------------------------------------------------------------------ materialise
for (a, b, name), mb in pieces.items():
    if not len(mb):
        continue
    mats = MATS
    if name.endswith("_agua"):
        mats = [lib["agua_piscina"]]
    elif name == "palmeiras_tronco":
        mats = [lib["tronco"]]
    elif name == "palmeiras_folha":
        mats = [lib["folhagem"]]
    o = mb.to_object(f"E{a}-{b}_{name}", mats, cn["Paisagem"] if name.startswith("palmeiras") else cn["Edificios"], smooth=name.startswith("palmeiras"))
    o["st_from"], o["st_to"] = a, b


def filtered_copy(src, ymax, a, b, coll):
    """Copy of an appended object keeping only faces entirely south of ymax (the platô terraces built so far)."""
    o = src.copy()
    o.data = src.data.copy()
    bm = bmesh.new()
    bm.from_mesh(o.data)
    kill = [f for f in bm.faces if max(v.co.y for v in f.verts) > ymax]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(o.data)
    bm.free()
    coll.objects.link(o)
    o.name = f"E{a}-{b}_{src.name}"
    o["st_from"], o["st_to"] = a, b
    return o


ga = root / "ArtSource" / "Blender" / "Resort" / "SantaAurora_GrandAurora_v1.blend"
want = ["Arq_T1", "Arq_T2", "Arq_T3", "Arq_T4", "Arq_Eixo", "Arq_Tower", "Agua", "Arbustos", "Buganvilias", "Palmeiras_troncos", "Palmeiras_folhas", "Arvores_copas"]
with bpy.data.libraries.load(str(ga), link=False) as (src, dst):
    dst.objects = [n for n in want if n in src.objects]
platoY = 480 + 82.0
for o in [x for x in dst.objects if x is not None]:
    full = o.copy()
    full.data = o.data
    full.name = f"E7-7_{o.name}"
    cn["Edificios"].objects.link(full)
    full["st_from"] = full["st_to"] = 7
    if o.name in ("Arq_T3", "Arq_T4", "Arq_Tower"):
        continue
    filtered_copy(o, platoY, 6, 6, cn["Edificios"])

# ------------------------------------------------------------------------------------------------ light, cameras, render
sun = sa_bl.production_look(scene, cn["Cameras"], elevation_deg=24, azimuth_deg=235, sun_energy=5.0, sky_strength=0.35, exposure=-1.5, haze=0.0)
cams = {
    "A_orla": ((X0 - 30, promZ - 34, 6.0), (X0 + 60, promZ + 30, 9), 24),
    "B_aerea": ((215, -20, 100), (520, 410, 8), 24),
    "D_barraca": ((X0 + 9, promZ + 3.5, gz(X0 + 9, promZ + 3.5) + 1.7), (X0, promZ - 7, gz(X0, promZ - 7) + 1.3), 32),
    "C_plato": ((450, 20, 65), (450, 560, 14), 30),
}
for name, (loc, tgt, lens) in cams.items():
    sa_bl.camera("CAM_" + name, cn["Cameras"], loc, target=tgt, lens=lens, clip=(0.5, 6000.0))

out = root / "ArtSource" / "Blender" / "Resort"
blend = out / "SantaAurora_Estagios_v1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
npoly = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
(out / "estagios_report.json").write_text(json.dumps({"blend": blend.relative_to(root).as_posix(), "polygons": npoly, "pieces": sorted(f"{a}-{b}:{n}" for (a, b, n) in pieces)}, indent=2) + "\n", encoding="utf-8")
print("ESTAGIOS", npoly)

if opts.render:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 90
    try:
        scene.eevee.taa_render_samples = opts.samples
    except AttributeError:
        pass
    shots = out / "Estagios"
    shots.mkdir(exist_ok=True)
    for st in [int(s) for s in opts.stages.split(",")]:
        for o in bpy.data.objects:
            if "st_from" in o:
                o.hide_render = not (o["st_from"] <= st <= o["st_to"])
        for cam in sorted((c for c in cn["Cameras"].objects if c.type == "CAMERA"), key=lambda c: c.name):
            if cam.name.startswith("CAM_C") and st < 6:
                continue
            if cam.name.startswith("CAM_D") and st > 2:
                continue
            scene.camera = cam
            scene.render.filepath = str(shots / f"estagio{st}_{cam.name[4:]}.jpg")
            bpy.ops.render.render(write_still=True)
            print("rendered", st, cam.name)
