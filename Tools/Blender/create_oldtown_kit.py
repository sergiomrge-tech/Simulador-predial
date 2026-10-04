"""Generate the Old Town modular kit + PBR material library + building families as a reusable asset library (W1.5).

Run:
blender --background --factory-startup --python Tools/Blender/create_oldtown_kit.py -- --root PROJECT_ROOT

Output:
ArtSource/Blender/Kits/SantaAurora_CidadeAntiga_Kit_v1.blend   (assets marked for the Asset Browser)
ArtSource/Blender/Kits/kit_report.json
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Map"))
sys.path.insert(0, str(root / "Tools" / "Blender"))

import sa_arch  # noqa: E402
import sa_detail  # noqa: E402
import sa_bl  # noqa: E402
import sa_kit  # noqa: E402
import sa_materials  # noqa: E402
from urban_fabric import OLDTOWN_VARIANTS  # noqa: E402

sa_bl.clear_scene()
scene = bpy.context.scene
scene.name = "SantaAurora_Kit_CidadeAntiga"
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
lib = sa_materials.build_library()
sa_detail.extend_library(lib)
c_kit = sa_bl.collection("KIT_Modular")
c_props = sa_bl.collection("KIT_Infraestrutura")
c_fam = sa_bl.collection("KIT_Familias")
c_mat = sa_bl.collection("KIT_Materiais")
c_lbl = sa_bl.collection("KIT_Labels")
c_cam = sa_bl.collection("KIT_Cameras")
kit = sa_kit.build_kit(lib, c_kit)
props = sa_kit.build_props(lib, c_props)


def label(text, x, y, z=0.02, size=.28, coll=c_lbl):
    cu = bpy.data.curves.new("L_" + text, "FONT")
    cu.body = text
    cu.align_x = "CENTER"
    cu.size = size
    o = bpy.data.objects.new("LBL_" + text, cu)
    o.location = (x, y, z)
    cu.materials.append(lib["plastico"])
    coll.objects.link(o)


def grid(objs, x0, y0, cols, dx, dy):
    for k, o in enumerate(objs):
        x = x0 + (k % cols) * dx
        y = y0 - (k // cols) * dy
        o.location = (x, y, 0)
        label(o.name.replace("KIT_", "").replace("PROP_", ""), x + 1.0, y - 1.6)
        try:
            o.asset_mark()
            o.asset_data.description = o.get("sa_stage", "")
            o.asset_data.tags.new(o.get("sa_kit_family", o.get("sa_prop", "kit")))
        except Exception:
            pass


grid(sorted(kit.values(), key=lambda o: o.name), 0, 0, 8, 5.5, 6.5)
grid(sorted(props.values(), key=lambda o: o.name), 0, -36, 8, 5.5, 8.0)
fam_objs = []
for k, v in enumerate(OLDTOWN_VARIANTS):
    mb = sa_bl.MeshBuilder()
    sa_arch.building_mesh(mb, v, k)
    o = mb.to_object("FAM_" + v["id"], [lib[n] for n in sa_arch.variant_materials(v, k)], c_fam)
    sa_bl.props(o, sa_family=v["family"], sa_variant=v["id"], footprint_m=[v["w"], v["d"]], floors=v["floors"])
    fam_objs.append((v, o))
x = 0.0
row_y = -120.0
row_w = 0.0
for v, o in fam_objs:
    if x + v["w"] > 180:
        x = 0.0
        row_y -= 46.0
    o.location = (x + v["w"] / 2, row_y, 0)
    label(v["id"] + " " + v["family"], x + v["w"] / 2, row_y - v["d"] / 2 - 3, size=1.2)
    try:
        o.asset_mark()
        o.asset_data.tags.new(v["family"])
    except Exception:
        pass
    x += v["w"] + 4
# W2 detail components (sa_detail): one sample of each, each with its own pivot, ready to become prefabs.
c_det = sa_bl.collection("KIT_Detalhe_W2")
K = sa_detail.Kit(lib, c_det)
samples = [
    lambda n, p: K.window_sliding(n, 1.6, 1.2, p, 0.0, grille=True), lambda n, p: K.window_basculante(n, .6, .5, p, 0.0),
    lambda n, p: K.door(n, .8, 2.1, p, 0.0, open_deg=-35)[0], lambda n, p: K.door_entrance_metal(n, 1.2, 2.3, p, 0.0),
    lambda n, p: K.panel_qdc(n, p, 0.0), lambda n, p: K.outlet(n, p, 0.0), lambda n, p: K.switch(n, p, 0.0),
    lambda n, p: K.shower_electric(n, p, 0.0), lambda n, p: K.toilet(n, p, 0.0), lambda n, p: K.sink_pedestal(n, p, 0.0),
    lambda n, p: K.kitchen_counter(n, 1.8, p, 0.0), lambda n, p: K.water_tank(n, p), lambda n, p: K.entrance_meter(n, p, 0.0),
    lambda n, p: K.intercom(n, p, 0.0), lambda n, p: K.mailboxes(n, p, 0.0), lambda n, p: K.extinguisher(n, p, 0.0),
    lambda n, p: K.stair_u(n, 1.1, 2.5, 3.0, p, 0.0), lambda n, p: K.mattress(n, p, 0.0), lambda n, p: K.chair_old(n, p, 0.0),
    lambda n, p: K.cardboard_box(n, .6, .45, .4, p, 0.0), lambda n, p: K.toolcase(n, p, 0.0), lambda n, p: K.folding_table(n, p, 0.0),
    lambda n, p: K.old_pc(n, p, 0.0), lambda n, p: K.workbench(n, 2.0, p, 0.0, pro=True), lambda n, p: K.shelving(n, 1.8, p, 0.0),
    lambda n, p: K.job_board(n, p, 0.0)]
names_det = ["janela_correr", "basculante", "porta_interna", "porta_entrada_metal", "quadro_distribuicao", "tomada", "interruptor",
             "chuveiro_eletrico", "vaso_sanitario", "lavatorio", "bancada_cozinha", "caixa_dagua_1000L", "padrao_entrada", "interfone",
             "caixas_correio", "extintor", "escada_U", "colchao", "cadeira_velha", "caixa_papelao", "maleta_guto", "mesa_dobravel",
             "pc_antigo", "bancada_pro", "estante_aco", "quadro_chamados"]
for k, (fn, n) in enumerate(zip(samples, names_det)):
    x, y = 52 + (k % 7) * 4.5, -2 - (k // 7) * 6.0
    o = fn("DET_" + n, (x, y, 0))
    label(n, x, y - 2.0, size=.3)
    try:
        o.asset_mark()
        o.asset_data.tags.new("w2_detalhe")
    except Exception:
        pass
# Material swatches: bevelled slabs, one per library material.
names = sorted(lib)
for k, name in enumerate(names):
    mb = sa_bl.MeshBuilder()
    mb.box(0, 0, 0, 1.8, .25, 1.8, 0)
    mb.cylinder(0, -.9, 0, .45, .9, 24, 0)
    o = sa_bl.bevelled_object("MAT_" + name, mb, [lib[name]], c_mat, bevel=.03)
    o.location = (-30 + (k % 8) * 2.6, -10 - (k // 8) * 3.2, 0)
    label(name, o.location.x, o.location.y - 1.6, size=.22)
ground = sa_bl.MeshBuilder()
ground.box(70, -160, -.05, 360, 440, .05, 0)
sa_bl.MeshBuilder.to_object(ground, "KIT_Ground", [lib["concreto"]], c_lbl)
sa_bl.sun_and_sky(scene, c_cam)
sa_bl.camera("CAM_Kit_Modular", c_cam, (19, -38, 16), target=(19, -10, .5), lens=30)
sa_bl.camera("CAM_Kit_Infra", c_cam, (19, -64, 10), target=(19, -44, 2), lens=30)
sa_bl.camera("CAM_Kit_Families", c_cam, (90, -345, 105), target=(90, -185, 4), lens=35)
sa_bl.camera("CAM_Kit_Materials", c_cam, (-21, -31, 9), target=(-21, -16.5, .5), lens=32)
sa_bl.camera("CAM_Kit_Detail_W2", c_cam, (65.5, -34, 13), target=(65.5, -11, .6), lens=30)
scene["sa_captures"] = json.dumps([["w2_kit_detalhe", "CAM_Kit_Detail_W2", 2400, 1350, ["KIT_Ground__none"]],
                                   ["w2_kit_materiais", "CAM_Kit_Materials", 2400, 1350, []]])
scene["sa_hero"] = "kit"
scene["sa_no_root"] = True
scene.render.engine = "BLENDER_EEVEE"
out = root / "ArtSource" / "Blender" / "Kits"
out.mkdir(parents=True, exist_ok=True)
blend = out / "SantaAurora_CidadeAntiga_Kit_v1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
rep = {"blend": blend.relative_to(root).as_posix(), "blenderVersion": bpy.app.version_string, "kitPieces": sorted(kit), "props": sorted(props),
       "familyVariants": [v["id"] for v, _ in fam_objs], "materials": names,
       "polycount": {o.name: len(o.data.polygons) for o in list(kit.values()) + list(props.values())},
       "status": "W1.5 kit base: bevelled LOD0 base pieces, procedural PBR base materials; final textures/decals in W3"}
(out / "kit_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("KIT GENERATED", len(kit), len(props), len(fam_objs), len(names))
