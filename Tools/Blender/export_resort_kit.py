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
(out / "resort_stages.json").write_text(json.dumps({"schemaVersion": 1, "pieces": manifest}, indent=1) + "\n", encoding="utf-8")
print("EXPORTED", len(manifest), "pieces,", sum(m["polygons"] for m in manifest), "polygons")
