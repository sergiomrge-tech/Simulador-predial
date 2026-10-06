"""Grand Aurora luxury suite (interior hero room for first-person inspection), with terrace and plunge pool.

blender --background --factory-startup --python Tools/Blender/create_suite.py -- --root PROJECT_ROOT [--render] [--night]

Writes ArtSource/Blender/Resort/SantaAurora_Suite_v1.blend. Local frame: X = along the facade (0..9 m), Y = depth inward (0..11 m), the sea
view looks toward -Y. Furniture is modelled with real proportions (king bed 2.0 x 2.2 m, sofa 2.6 m, freestanding tub 1.7 m).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--render", action="store_true")
parser.add_argument("--night", action="store_true")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_bl  # noqa: E402
import sa_detail  # noqa: E402
import sa_materials  # noqa: E402
import sa_resort as R  # noqa: E402
from sa_resort import S  # noqa: E402

sa_bl.clear_scene()
scene = bpy.context.scene
lib = sa_materials.build_library()
sa_detail.extend_library(lib)
R.extend_library(lib)
MATS = R.materials_for(lib)
top = sa_bl.collection("Suite")
cam_coll = sa_bl.collection("Cameras", top)
mb = sa_bl.MeshBuilder()
water = sa_bl.MeshBuilder()
fr = R.Frame(mb, (0.0, 0.0), 0.0)
W_, D_, H_ = 9.0, 11.0, 3.2          # room width, depth, ceiling height
F = 0.0                                # floor level


def box(u0, u1, d0, d1, z0, z1, m, **kw):
    fr.box(u0, u1, d0, d1, z0, z1, S[m] if isinstance(m, str) else m, **kw)


# ------------------------------------------------------------------------------------------------ shell
box(-0.2, W_ + 0.2, -0.2, D_ + 0.2, -0.3, F, "concreto", bottom=True)                       # slab
box(0, W_, 0, D_, F, F + 0.02, "teca")                                                      # hardwood floor (living + sleeping)
box(4.0, W_, 6.0, D_, F + 0.02, F + 0.04, "marmore")                                        # bathroom marble
box(0, 4.0, 6.0, D_, F + 0.02, F + 0.03, "teca")                                            # dressing room
box(-0.2, 0.0, 0, D_, F, F + H_, "estuque", back=False)                                     # side walls
box(W_, W_ + 0.2, 0, D_, F, F + H_, "estuque", back=False)
box(0, W_, D_, D_ + 0.2, F, F + H_, "estuque", front=False)                                 # back wall
box(0, 4.2, 6.0 - 0.1, 6.0 + 0.1, F, F + H_, "estuque")                                     # partition (bedroom | dressing + bath) with a doorway
box(5.2, W_, 6.0 - 0.1, 6.0 + 0.1, F, F + H_, "estuque")
box(4.2, 5.2, 5.9, 6.1, F + 2.4, F + H_, "estuque")                                         # lintel over the doorway
box(0, W_, 0, D_, F + H_ - 0.3, F + H_, "estuque", bottom=True, top=False)                  # ceiling slab
box(0, W_, 0.0, 0.7, F + H_ - 0.36, F + H_ - 0.3, "luz", top=False)                         # cove light strip at the glass
box(0.3, W_ - 0.3, 5.6, 5.9, F + H_ - 0.36, F + H_ - 0.3, "luz", top=False)
# floor-to-ceiling glass wall (sliding doors) with brass mullions
box(0.0, W_, -0.05, 0.05, F + 0.04, F + H_ - 0.3, "vidro", top=False, bottom=False, sides=False)
for k in range(0, 7):
    u = k * W_ / 6
    box(u - 0.04, u + 0.04, -0.1, 0.12, F, F + H_ - 0.3, "latao", top=False)
box(0, W_, -0.1, 0.12, F + H_ - 0.38, F + H_ - 0.3, "latao")
box(0, W_, -0.1, 0.12, F, F + 0.05, "latao")
# curtains (linen) gathered at the sides
box(0.05, 0.75, 0.15, 0.4, F, F + H_ - 0.32, "tecido", top=False)
box(W_ - 0.75, W_ - 0.05, 0.15, 0.4, F, F + H_ - 0.32, "tecido", top=False)

# ------------------------------------------------------------------------------------------------ terrace + plunge pool + sea-view balustrade
box(-0.2, W_ + 0.2, -4.6, 0.0, F - 0.1, F + 0.03, "teca")
box(-0.2, W_ + 0.2, -4.7, -4.6, F, F + 1.05, "vidro", top=False, bottom=False, sides=False)
box(-0.2, W_ + 0.2, -4.75, -4.55, F + 1.05, F + 1.12, "latao")
R.pool(mb, water, 5.4, -3.9, 8.7, -1.0, F + 0.03, depth=1.3)
for k in range(2):
    R.lounger(fr, 0.8 + k * 1.1, -3.7, F + 0.03)
box(2.9, 3.5, -3.2, -2.6, F + 0.03, F + 0.55, "basalto")                                      # side table
box(0.1, 0.9, -1.0, -0.4, F + 0.03, F + 0.6, "basalto")                                       # planter

# ------------------------------------------------------------------------------------------------ sleeping zone
bu0 = 5.5
box(bu0 - 0.1, bu0 + 2.2, 4.1, 5.9, F, F + 0.4, "madeira_escura")                           # bed base with a floating look
box(bu0 - 0.05, bu0 + 2.15, 4.15, 5.85, F + 0.4, F + 0.62, "tecido")                       # mattress
box(bu0 - 0.1, bu0 + 2.2, 5.6, 5.9, F + 0.1, F + 1.35, "teca")                             # headboard (timber slats)
for k in range(10):
    box(bu0 - 0.1 + k * 0.23, bu0 + 0.0 + k * 0.23, 5.55, 5.62, F + 0.1, F + 1.35, "brise", top=False)
for k in range(2):
    box(bu0 + 0.1 + k * 1.0, bu0 + 0.9 + k * 1.0, 5.1, 5.55, F + 0.62, F + 0.8, "tecido")   # pillows
box(bu0, bu0 + 2.1, 4.1, 4.9, F + 0.62, F + 0.67, "tecido")                                # bed throw
for k in range(2):                                                                         # nightstands + lamps
    nu = bu0 - 0.85 if k == 0 else bu0 + 2.35
    box(nu, nu + 0.6, 5.2, 5.8, F + 0.05, F + 0.5, "madeira_escura")
    fr.cyl(nu + 0.3, 5.5, F + 0.5, 0.05, 0.5, 8, S["latao"])
    fr.cyl(nu + 0.3, 5.5, F + 1.0, 0.2, 0.3, 12, S["luz"])
box(bu0 - 1.2, bu0 + 3.4, 3.6, 6.0, F + 0.02, F + 0.04, "tecido")                          # rug
box(bu0 - 0.3, bu0 + 2.4, 3.6, 4.0, F + 0.02, F + 0.5, "tecido")                           # bench at the foot of the bed

# ------------------------------------------------------------------------------------------------ living zone
box(0.5, 4.0, 1.4, 4.9, F + 0.02, F + 0.04, "tecido")                                      # rug
box(0.8, 3.4, 4.0, 5.0, F + 0.0, F + 0.45, "tecido")                                       # sofa seat (2.6 m)
box(0.8, 3.4, 4.7, 5.0, F + 0.45, F + 0.95, "tecido")                                      # sofa back
box(0.7, 0.95, 4.0, 5.0, F + 0.0, F + 0.65, "tecido")
box(3.25, 3.5, 4.0, 5.0, F + 0.0, F + 0.65, "tecido")
box(1.5, 2.9, 2.5, 3.4, F + 0.02, F + 0.4, "marmore")                                      # coffee table
box(1.5, 2.9, 2.5, 3.4, F + 0.4, F + 0.44, "latao")
for (cu, cd, rot) in ((0.7, 2.0, 0), (3.2, 2.1, 0)):                                        # armchairs
    box(cu, cu + 0.9, cd, cd + 0.9, F + 0.0, F + 0.45, "tecido")
    box(cu, cu + 0.9, cd + 0.7, cd + 0.9, F + 0.45, F + 0.95, "tecido")
box(0.0, 0.1, 1.4, 4.0, F + 0.9, F + 2.3, "madeira_escura")                                 # TV wall panel
box(0.1, 0.18, 1.8, 3.6, F + 1.1, F + 1.95, "aco_preto")                                    # TV
box(0.1, 0.5, 1.4, 4.0, F + 0.35, F + 0.45, "teca")                                        # media console
fr.cyl(0.4, 5.3, F, 0.03, 1.6, 8, S["latao"])                                              # floor lamp
fr.cyl(0.4, 5.3, F + 1.6, 0.22, 0.35, 14, S["luz"])

# ------------------------------------------------------------------------------------------------ dressing room
box(0.0, 0.5, 6.2, D_, F + 0.04, F + 2.6, "madeira_escura")                                 # wardrobe wall
box(0.5, 4.0, D_ - 0.5, D_, F + 0.04, F + 2.6, "madeira_escura")
box(1.8, 3.4, 8.0, 9.6, F + 0.04, F + 0.9, "marmore")                                       # island
box(1.8, 3.4, 8.0, 9.6, F + 0.9, F + 0.95, "latao")

# ------------------------------------------------------------------------------------------------ bathroom
box(5.0, 7.4, 8.0, 9.7, F + 0.04, F + 0.55, "marmore")                                      # freestanding tub (sculpted block)
box(5.15, 7.25, 8.15, 9.55, F + 0.55, F + 0.62, "marmore")
water.quad((5.25, 8.25, F + 0.5), (7.15, 8.25, F + 0.5), (7.15, 9.45, F + 0.5), (5.25, 9.45, F + 0.5), 0)
fr.cyl(6.2, 9.9, F + 0.04, 0.03, 0.9, 8, S["latao"])                                        # tub filler
box(4.1, 6.6, D_ - 0.6, D_, F + 0.04, F + 0.85, "madeira_escura")                           # double vanity
box(4.1, 6.6, D_ - 0.62, D_, F + 0.85, F + 0.9, "marmore")
for k in range(2):
    box(4.5 + k * 1.2, 5.3 + k * 1.2, D_ - 0.55, D_ - 0.1, F + 0.9, F + 0.95, "marmore")
    box(4.65 + k * 1.2, 5.15 + k * 1.2, D_ - 0.05, D_ - 0.02, F + 1.15, F + 2.2, "vidro", top=False, bottom=False, sides=False)   # mirror
box(7.4, W_, 6.2, 8.0, F + 0.04, F + 0.06, "marmore")                                        # shower tray
box(7.4, W_, 6.15, 6.2, F + 0.06, F + 2.4, "vidro", top=False, bottom=False, sides=False)
box(7.4, 7.45, 6.2, 8.0, F + 0.06, F + 2.4, "vidro", top=False, bottom=False, sides=False)
fr.cyl(8.6, 7.8, F + 2.0, 0.015, 0.4, 6, S["latao"])
box(8.3, 8.9, 7.7, 8.0, F + 2.3, F + 2.34, "latao")                                          # rain shower head
box(W_ - 0.05, W_, 8.1, D_, F + 0.04, F + 2.4, "marmore")                                    # marble feature wall

# ------------------------------------------------------------------------------------------------ ceiling pendants
for (u, d) in ((2.2, 3.2), (6.6, 4.2), (6.2, 9.0)):
    fr.cyl(u, d, F + H_ - 1.6, 0.01, 1.3, 6, S["latao"])
    fr.cyl(u, d, F + H_ - 1.9, 0.28, 0.3, 14, S["luz"])

sa_bl.bevelled_object("Suite", mb, MATS, top, bevel=0.018, segments=2)
water.to_object("Agua", [lib["agua_piscina"]], top)

# ------------------------------------------------------------------------------------------------ light + cameras
night = opts.night
sun = sa_bl.production_look(scene, top, elevation_deg=14 if night else 38, azimuth_deg=0, sun_energy=0.3 if night else 9.0,
                            sky_strength=0.05 if night else 0.12, exposure=0.2 if night else -0.4, haze=0.0)
vs = scene.view_settings
vs.view_transform = "AgX"
try:
    vs.look = "AgX - Medium High Contrast"
except TypeError:
    pass
vs.exposure = 0.0 if night else -1.0
sun.rotation_euler = (math.radians(60), 0, math.radians(180))                    # sun enters through the sea-side glass (+Y direction)
if night:
    lib["luz_quente"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 14.0
else:
    lib["luz_quente"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3.0
for name, loc, en in (("sala", (2.2, 3.2, 2.6), 400), ("quarto", (6.6, 4.2, 2.6), 400), ("banho", (6.2, 9.0, 2.6), 300), ("closet", (2.2, 8.5, 2.6), 200)):
    ld = bpy.data.lights.new("LUZ_" + name, "POINT")
    ld.energy = en * 2.0
    ld.color = (1.0, .82, .62)
    ld.shadow_soft_size = 0.6
    lo = bpy.data.objects.new("LUZ_" + name, ld)
    lo.location = loc
    top.objects.link(lo)
cams = {
    "01_sala_para_o_mar": ((0.7, 5.6, 1.6), (6.0, -3.0, 1.1), 17),
    "02_quarto": ((0.5, 0.9, 1.6), (6.6, 5.0, 0.7), 20),
    "03_banheiro": ((4.2, 6.6, 1.6), (6.4, 9.5, 0.7), 22),
    "04_terraco": ((1.2, -4.1, 1.55), (6.5, 3.5, 1.1), 18),
    "05_entrada": ((4.7, 10.6, 1.6), (4.5, 1.0, 1.4), 16),
}
for name, (loc, tgt, lens) in cams.items():
    sa_bl.camera("CAM_" + name, cam_coll, loc, target=tgt, lens=lens, clip=(0.05, 200.0))

out_dir = root / "ArtSource" / "Blender" / "Resort"
blend = out_dir / ("SantaAurora_Suite_v1_noite.blend" if night else "SantaAurora_Suite_v1.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
polys = sum(len(o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
(out_dir / "suite_report.json").write_text(json.dumps({"blend": blend.relative_to(root).as_posix(), "polygons": polys, "size_m": [W_, D_, H_]}, indent=2) + "\n", encoding="utf-8")
print("SUITE", polys)

if opts.render:
    scene.eevee.taa_render_samples = 96
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x, scene.render.resolution_y = 1600, 900
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 90
    shots = out_dir / ("Suite_noite" if night else "Suite")
    shots.mkdir(exist_ok=True)
    for ob in sorted((o for o in cam_coll.objects if o.type == "CAMERA"), key=lambda c: c.name):
        scene.camera = ob
        scene.render.filepath = str(shots / (ob.name[4:] + ".jpg"))
        bpy.ops.render.render(write_still=True)
        print("rendered", ob.name)
