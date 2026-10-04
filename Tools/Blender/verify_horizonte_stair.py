"""Geometric regression check for the Edifício Horizonte stair and stair doors (W2_horizonte.blend, no Unity needed).

Run (opens the file itself, never saves it):
blender -b --factory-startup ArtSource/Blender/World/OldTown/Heroes/W2_horizonte.blend --python Tools/Blender/verify_horizonte_stair.py -- --out report.json

Checks (CharacterController of the game: height 1.8 m, radius 0.28 m, step 0.3 m):
- head room: for every stair, the clear height above the walkable tread centres of both flights and the turn landing must be >= 1.9 m;
- slab openings: no floor slab over the flights (covered by the head-room rays; a slab shows up as a short ceiling);
- stair doors (ground floor and the typical floor): the 1.12 m x 2.3 m door passage must be free of geometry along the wall normal
  at every sampled width/height, and the opening must be at least 2.4 m high at the centre line.
Exit status is non-zero when any check fails, so the script can gate a pipeline.
"""
import json
import math
import sys

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out_path = argv[argv.index("--out") + 1] if "--out" in argv else None
HEAD_REQUIRED = 1.9
dg = bpy.context.evaluated_depsgraph_get()


def world_bvh(objs):
    verts, polys = [], []
    for o in objs:
        me = o.evaluated_get(dg).to_mesh()
        base = len(verts)
        verts.extend(o.matrix_world @ v.co for v in me.vertices)
        polys.extend(tuple(base + i for i in p.vertices) for p in me.polygons)
        o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(verts, polys)


meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("W2_horizonte__") and not o.name.endswith(("__ROOF",))
          and "curtain" not in o.name and not o.hide_render]
stairs = sorted((o for o in meshes if "__stair_F" in o.name), key=lambda o: o.name)
doors = sorted((o for o in meshes if o.name.endswith("_stair_door__frame")), key=lambda o: o.name)
all_bvh = world_bvh(meshes)
errors, report = [], {"stairs": {}, "doors": {}}

for st in stairs:
    corners = [st.matrix_world @ Vector(c) for c in st.bound_box]
    x0, x1 = min(c.x for c in corners), max(c.x for c in corners)
    y0, y1 = min(c.y for c in corners), max(c.y for c in corners)
    ztop = max(c.z for c in corners)
    sbvh = world_bvh([st])
    w = (x1 - x0) / 2.0
    lanes = (x0 + w / 2, x1 - w / 2)                       # centre of each flight (the turn landing spans both)
    samples, worst, low = 0, 99.0, 0
    ys = [y0 + .15 + k * .1 for k in range(int((y1 - y0 - .3) / .1) + 1)]
    for lx in lanes:
        for y in ys:
            hit = sbvh.ray_cast(Vector((lx, y, ztop + 1.0)), Vector((0, 0, -1)))
            if hit[0] is None:
                continue
            surface = hit[0] + Vector((0, 0, .03))
            up = all_bvh.ray_cast(surface, Vector((0, 0, 1)), 6.0)
            clear = up[3] if up[0] is not None else 6.0
            samples += 1
            worst = min(worst, clear)
            if clear < HEAD_REQUIRED:
                low += 1
    ok = samples > 20 and low == 0
    report["stairs"][st.name] = {"samples": samples, "worstHeadRoomM": round(worst, 3), "samplesBelowRequired": low, "ok": ok}
    if not ok:
        errors.append(f"{st.name}: head room {worst:.2f} m < {HEAD_REQUIRED} m at {low}/{samples} samples")

for fr in doors:
    corners = [fr.matrix_world @ Vector(c) for c in fr.bound_box]
    cx = (min(c.x for c in corners) + max(c.x for c in corners)) / 2
    cy = (min(c.y for c in corners) + max(c.y for c in corners)) / 2
    zf = min(c.z for c in corners)
    blocked, tested = 0, 0
    for dx in (-.45, -.3, -.15, 0.0, .15, .3, .45):
        for h in (.25, .6, 1.0, 1.4, 1.8, 2.2):
            tested += 1
            hit = all_bvh.ray_cast(Vector((cx + dx, cy - 1.5, zf + .02 + h)), Vector((0, 1, 0)), 3.0)
            if hit[0] is not None:
                blocked += 1
    top = all_bvh.ray_cast(Vector((cx, cy, zf + .02)), Vector((0, 0, 1)), 4.0)
    opening_h = (top[3] if top[0] is not None else 4.0)
    ok = blocked == 0 and opening_h >= 2.4
    report["doors"][fr.name] = {"raysBlocked": blocked, "raysTested": tested, "openingHeightAtCentreM": round(opening_h, 3), "ok": ok}
    if not ok:
        errors.append(f"{fr.name}: {blocked}/{tested} passage rays blocked, opening {opening_h:.2f} m")

if not stairs:
    errors.append("no stair objects found")
if len(doors) < 2:
    errors.append("expected the ground-floor and typical-floor stair doors")
report["errors"] = errors
report["passed"] = not errors
report["headRoomRequiredM"] = HEAD_REQUIRED
txt = json.dumps(report, indent=2, ensure_ascii=False)
if out_path:
    open(out_path, "w", encoding="utf-8").write(txt + "\n")
print("HORIZONTE STAIR CHECK", "PASS" if not errors else "FAIL", json.dumps({"errors": errors}))
if errors:
    sys.exit(1)
