"""Reopen a W2 hero .blend in a fresh Blender process, audit it, measure complexity and render its captures.

Run (Blender opens the file itself, proving it reopens):
blender -b --factory-startup <W2_*.blend> --python Tools/Blender/verify_w2_hero.py -- --root ROOT [--no-render]

Captures come from the scene property `sa_captures`: [[name, camera, w, h, [object-name prefixes hidden in render]], ...].
Writes ArtSource/Blender/World/Reviews/W2/<name>.jpg and reopen_<hero>.json. Never saves the .blend.
"""
import argparse
import json
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--no-render", action="store_true")
parser.add_argument("--review", default="W2", help="Reviews/<dir> for captures and reopen report")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
review = root / "ArtSource" / "Blender" / "World" / "Reviews" / opts.review
review.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
hero = scene.get("sa_hero", "unknown")
errors, checks = [], {}

missing = []
for lib in bpy.data.libraries:
    if not Path(bpy.path.abspath(lib.filepath)).exists():
        missing.append("library:" + lib.filepath)
for img in bpy.data.images:
    if img.source == "FILE" and not img.packed_file and img.filepath and not Path(bpy.path.abspath(img.filepath)).exists():
        missing.append("image:" + img.filepath)
if missing:
    errors.append("missing data: " + ", ".join(missing))
if scene.unit_settings.system != "METRIC" or abs(scene.unit_settings.scale_length - 1.0) > 1e-6:
    errors.append("scene units are not metric 1:1")

# Complexity: evaluated triangles per collection, largest single objects (no giant single geometry).
deps = bpy.context.evaluated_depsgraph_get()
per_coll, objs = {}, []
for o in scene.objects:
    if o.type != "MESH":
        continue
    ev = o.evaluated_get(deps)
    me = ev.to_mesh()
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    ev.to_mesh_clear()
    coll = o.users_collection[0].name if o.users_collection else "-"
    per_coll[coll] = per_coll.get(coll, 0) + tris
    objs.append((tris, o.name))
objs.sort(reverse=True)
checks["meshObjects"] = len(objs)
checks["triangles"] = sum(t for t, _ in objs)
checks["trianglesPerCollection"] = dict(sorted(per_coll.items()))
checks["largestObjects"] = [{"name": n, "tris": t} for t, n in objs[:8]]
checks["lights"] = sum(1 for o in scene.objects if o.type == "LIGHT")
checks["materials"] = len([m for m in bpy.data.materials if m.users])
checks["stateSlots"] = sorted({o.get("state") for o in scene.objects if o.get("sa_kind") == "state_slot"})
checks["interactive"] = sum(1 for o in scene.objects if o.get("interactive"))
if objs and objs[0][0] > 200000:
    errors.append(f"single object too heavy: {objs[0][1]} ({objs[0][0]} tris)")
roots = [o for o in scene.objects if o.name.endswith("_ROOT")]
if scene.get("sa_no_root"):
    pass
elif len(roots) != 1:
    errors.append("expected exactly one hero root empty")
else:
    checks["root"] = {"name": roots[0].name, "facility_id": roots[0].get("facility_id"), "location": [round(v, 3) for v in roots[0].location]}
    unparented = [o.name for o in scene.objects if o.parent is None and o is not roots[0] and o.type != "CAMERA" and not o.name.startswith("SA_")]
    if unparented:
        errors.append(f"objects outside the hero root: {unparented[:5]}")

renders = []
if not opts.no_render:
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 88
    for name, cam, w, h, hide in json.loads(scene.get("sa_captures", "[]")):
        if cam not in bpy.data.objects:
            errors.append("missing camera " + cam)
            continue
        for o in scene.objects:
            o.hide_render = any(o.name.startswith(p) for p in hide)
        scene.camera = bpy.data.objects[cam]
        scene.render.resolution_x, scene.render.resolution_y = w, h
        scene.render.resolution_percentage = 100
        out = review / f"{name}.jpg"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        renders.append(out.relative_to(root).as_posix())

report = {"hero": hero, "blend": Path(bpy.data.filepath).relative_to(root).as_posix(), "blenderVersion": bpy.app.version_string,
          "objects": len(bpy.data.objects), "checks": checks, "missingData": missing, "renders": renders, "errors": errors, "passed": not errors}
(review / f"reopen_{hero}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print("W2 VERIFY", hero, "PASS" if not errors else "FAIL", errors)
