"""Exports every stage piece of SantaAurora_Estagios_v1.blend as an FBX for Unity plus a manifest (resort_stages.json).

blender --background ArtSource/Blender/Resort/SantaAurora_Estagios_v1.blend --python Tools/Blender/export_resort_kit.py -- --root PROJECT_ROOT

Pieces are modelled in site-local world coordinates (Blender X east, Y north, Z up), so each FBX keeps its position: instantiate at the
origin and it lines up with the Unity terrain (Unity x east, z north, y up). The terrain, sea and vila are not exported (Unity builds them).
Materials get their base colour / roughness / metallic written as plain values (procedural node trees do not survive FBX).
"""
import argparse
import json
import re
import sys
from pathlib import Path

import bpy

p = argparse.ArgumentParser()
p.add_argument("--root", required=True)
o = p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(o.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Blender"))
import sa_materials  # noqa: E402
import sa_resort  # noqa: E402

out = root / "FacilityOps" / "Assets" / "_Game" / "Resources" / "Art" / "Resort"
out.mkdir(parents=True, exist_ok=True)

# ---- flat values for every material (what Unity will read)
specs = {}
specs.update(sa_materials.LIB)
specs.update(sa_resort.LIB_RESORT)
for m in bpy.data.materials:
    sp = specs.get(m.name)
    if not m.use_nodes:
        continue
    b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if b is None:
        continue
    if sp:
        c = sp["c1"]
        b.inputs["Base Color"].default_value = (c[0], c[1], c[2], 1.0)
        b.inputs["Roughness"].default_value = sum(sp["rough"]) / 2.0
        b.inputs["Metallic"].default_value = float(sp.get("metal", 0.0))
        for l in list(b.inputs["Base Color"].links):
            m.node_tree.links.remove(l)
    if m.name == "luz_quente":
        b.inputs["Base Color"].default_value = (1.0, .85, .6, 1.0)
        b.inputs["Emission Color"].default_value = (1.0, .78, .5, 1.0)
        b.inputs["Emission Strength"].default_value = 2.5     # visible warm glow; the night look raises it in-engine
    if m.name == "agua_piscina":
        b.inputs["Base Color"].default_value = (.14, .80, .84, 1.0)

# appended platô pieces carry duplicated materials ("travertino.001"): point them back at the originals so Unity sees one name per material
dup = re.compile(r"^(.+)\.\d{3}$")
for ob in bpy.data.objects:
    if ob.type != "MESH":
        continue
    for slot in ob.material_slots:
        m = slot.material
        mt = dup.match(m.name) if m else None
        if mt and mt.group(1) in bpy.data.materials:
            slot.material = bpy.data.materials[mt.group(1)]

pat = re.compile(r"^E(\d)-(\d)_(.+)$")
manifest = []
for ob in sorted(bpy.data.objects, key=lambda x: x.name):
    mt = pat.match(ob.name)
    if not mt or ob.type != "MESH" or ob.name.startswith(("E1-7_guardasois",)):
        continue
    a, b, name = int(mt.group(1)), int(mt.group(2)), mt.group(3)
    if name in ("barraca", "quiosque"):                 # the stall is built by the game; the kiosk arrives with its gameplay
        continue
    for x in bpy.context.selected_objects:
        x.select_set(False)
    ob.hide_render = False
    ob.hide_viewport = False
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    fn = f"{ob.name}.fbx".replace(" ", "_")
    bpy.ops.export_scene.fbx(filepath=str(out / fn), use_selection=True, object_types={"MESH"}, global_scale=1.0, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y", bake_space_transform=True,
                             mesh_smooth_type="FACE", use_mesh_modifiers=True, path_mode="AUTO", add_leaf_bones=False)
    ob.select_set(False)
    manifest.append({"asset": fn[:-4], "from": a, "to": b, "name": name, "polygons": len(ob.data.polygons)})
# ---- material table for Unity: authored PBR sets (ArtSource/Textures) where a material maps onto one, flat values otherwise
import shutil
TEX = {   # material -> (texture set, tint, smoothness)
    "travertino": ("ladrilho", (.92, .84, .70), .35), "estuque": ("reboco", (.96, .94, .90), .15), "teca": ("madeira", (.95, .66, .40), .35),
    "brise": ("madeira", (.80, .55, .34), .30), "madeira_escura": ("madeira", (.42, .27, .17), .35), "terracota": ("telha", (1.0, .78, .66), .25),
    "marmore": ("ladrilho", (.98, .97, .95), .75), "azulejo": ("pastilha", (.25, .80, .86), .8), "basalto": ("granito", (.30, .30, .33), .45),
    "concreto": ("concreto", (.95, .95, .93), .15), "tronco": ("madeira", (.45, .34, .26), .1),
}
BUMP = {"marmore": 0.0, "travertino": 0.45, "azulejo": 0.4, "estuque": 0.5}   # polished or fine surfaces keep little or no relief
tex_dir = out / "Textures"
tex_dir.mkdir(exist_ok=True)
tile = {k: v["tile_m"] for k, v in json.loads((root / "ArtSource" / "Textures" / "texture_library_w3.json").read_text(encoding="utf-8"))["sets"].items()}
used = sorted({m.name for ob in bpy.data.objects if pat.match(ob.name) and ob.type == "MESH" for m in ob.data.materials if m})
table = {}
for name in used:
    sp = specs.get(name, {})
    c1 = sp.get("c1", (.6, .6, .6))
    e = {"color": list(c1), "smoothness": round(1.0 - sum(sp.get("rough", (.6, .6))) / 2.0, 3), "metallic": float(sp.get("metal", 0.0))}
    if name in TEX:
        sset, tint, sm = TEX[name]
        for kind in ("BaseColor", "Normal"):
            src = root / "ArtSource" / "Textures" / sset / f"{sset}_{kind}.jpg"
            if src.exists():
                shutil.copy2(src, tex_dir / src.name)
        e.update({"set": sset, "color": list(tint), "smoothness": sm, "tile": tile.get(sset, 1.0), "bump": BUMP.get(name, 0.9)})
    if name == "vidro":
        e.update({"color": [.30, .46, .55], "smoothness": .95, "metallic": .6})
    if name == "luz_quente":
        e.update({"color": [1, .85, .6], "emission": [1.0, .74, .45, 2.2]})
    if name == "agua_piscina":
        e.update({"color": [.12, .72, .78], "smoothness": .97, "emission": [.05, .45, .52, 0.5]})
    table[name] = e
(out / "resort_materials.json").write_text(json.dumps({"schemaVersion": 1, "materials": table}, indent=1) + "\n", encoding="utf-8")
(out / "resort_stages.json").write_text(json.dumps({"schemaVersion": 1, "pieces": manifest}, indent=1) + "\n", encoding="utf-8")
print("EXPORTED", len(manifest), "pieces,", sum(m["polygons"] for m in manifest), "polygons")
