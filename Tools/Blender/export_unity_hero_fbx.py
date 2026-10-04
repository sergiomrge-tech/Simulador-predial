"""Export one authored hero location as a separate Unity FBX.

Run with the hero .blend opened, for example:
blender -b ArtSource/Blender/World/OldTown/Heroes/W2_horizonte.blend \
  --python Tools/Blender/export_unity_hero_fbx.py -- \
  --root . --hero horizonte

Gameplay markers are intentionally excluded and exported separately with
export_unity_gameplay_markers.py.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unity_export_staging import stage_meshes, bounds, cleanup

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--hero", required=True)
parser.add_argument("--output", default="")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

root = Path(opts.root).resolve()
hero = opts.hero

roots = [
    o for o in bpy.data.objects
    if o.library is None
    and o.get("facility_id") == hero
    and o.type == "EMPTY"
    and o.name.endswith("_ROOT")
]
if len(roots) != 1:
    raise SystemExit(f"expected exactly one root for {hero}, found {len(roots)}")

hero_root = roots[0]


def descendant_of(obj, parent):
    p = obj.parent
    while p is not None:
        if p == parent:
            return True
        p = p.parent
    return False


def is_gameplay(obj):
    if obj.name.startswith(("GP_", "SLOT_", "PROXY_", "HERO_", "W2_SLOT_")):
        return True
    return obj.get("sa_layer") == "Gameplay" or obj.get("sa_kind") in {
        "spawn", "interaction", "state_slot", "gameplay_marker", "trigger", "entry", "exit"
    }


visual = []
excluded = []
for obj in bpy.data.objects:
    if obj.library is not None:
        continue
    if obj != hero_root and not descendant_of(obj, hero_root):
        continue

    if obj == hero_root:
        visual.append(obj)
        continue

    if is_gameplay(obj):
        excluded.append({"name": obj.name, "reason": "gameplay"})
        continue

    if obj.type in {"CAMERA", "LIGHT"}:
        excluded.append({"name": obj.name, "reason": obj.type.lower()})
        continue

    if obj.type in {"MESH", "CURVE", "SURFACE", "FONT", "META", "EMPTY"}:
        visual.append(obj)
    else:
        excluded.append({"name": obj.name, "reason": obj.type})


def subcell(x, y):
    ix = int((x + 4000.0) // 1000.0)
    iz = int((y + 4000.0) // 1000.0)
    sx = int(((x + 4000.0) % 1000.0) // 250.0)
    sz = int(((y + 4000.0) % 1000.0) // 250.0)
    return f"SA_M{ix:02d}_{iz:02d}_S{sx:02d}_{sz:02d}"


if not visual:
    raise SystemExit("hero contains no exportable visual objects")

out_dir = (
    Path(opts.output).resolve()
    if opts.output
    else root / "ArtSource" / "Blender" / "World" / "UnityExport" / "Heroes" / hero
)
out_dir.mkdir(parents=True, exist_ok=True)
fbx = out_dir / (hero.replace(".", "_") + ".fbx")

bpy.ops.object.select_all(action="DESELECT")
for obj in visual:
    try:
        obj.hide_set(False)
    except RuntimeError:
        pass
    obj.select_set(True)
bpy.context.view_layer.objects.active = hero_root

status = "PASS"
error = None
try:
    staged, groups = stage_meshes(visual)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in staged:
        obj.select_set(True)
    source_bounds = bounds(staged)
    bpy.ops.export_scene.fbx(
        filepath=str(fbx),
        use_selection=True,
        object_types={"MESH"},
        use_mesh_modifiers=True,
        use_mesh_modifiers_render=True,
        use_custom_props=True,
        add_leaf_bones=False,
        bake_anim=False,
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        path_mode="AUTO",
        embed_textures=False,
    )
except Exception as exc:
    status = "FAIL"
    error = repr(exc)
finally:
    cleanup(staged if 'staged' in globals() else [], groups if 'groups' in globals() else [])

world = hero_root.matrix_world.translation
manifest = {
    "schemaVersion": 1,
    "status": status,
    "hero": hero,
    "sourceBlend": Path(bpy.data.filepath).as_posix(),
    "rootObject": hero_root.name,
    "cell": subcell(float(world.x), float(world.y)),
    "blenderWorldPosition": [round(float(world.x), 6), round(float(world.y), 6), round(float(world.z), 6)],
    "unityWorldPosition": [round(float(world.x), 6), round(float(world.z), 6), round(float(world.y), 6)],
    "fbx": fbx.name if status == "PASS" else None,
    "fileBytes": fbx.stat().st_size if fbx.exists() else 0,
    "exportedObjects": len(visual),
    "excluded": excluded,
    "gameplayMarkers": f"ArtSource/Blender/World/UnityExport/Markers/{hero}.markers.json",
    "error": error,
    "blenderBounds": source_bounds if status == 'PASS' else None,
}
(out_dir / "hero_export_manifest.json").write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

bpy.ops.object.select_all(action="DESELECT")
print(json.dumps({
    "status": status,
    "hero": hero,
    "cell": manifest["cell"],
    "objects": len(visual),
    "fbx": str(fbx),
}, ensure_ascii=False))
raise SystemExit(0 if status == "PASS" else 1)
