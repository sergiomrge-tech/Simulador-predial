"""Read-only: extracts evidence candidates (world positions) from the W3 slice for the W3.2.x Unity capture tour. Never saves the .blend.

Run: blender -b SantaAurora_W3_VerticalSlice.blend --python Tools/Blender/extract_w32x_evidence.py -- --root . --out evidence.json
Output lists: cars (pitch/roll/position/heading), entrances (door-canopy / threshold instances), roofs (rooftop pieces), all inside the corridor box."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=".")
ap.add_argument("--out", required=True)
opt = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
BOX = (-3000.0, -2500.0, -2250.0, -1250.0)
inside = lambda x, y: BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]
out = {"cars": [], "entrances": [], "roofs": [], "steps": []}

for o in bpy.data.objects:
    if o.get("sa_kind") == "vehicle" and o.library is None:
        x, y, z = o.matrix_world.translation
        if inside(x, y):
            out["cars"].append({"name": o.name, "x": round(x, 2), "y": round(y, 2), "z": round(z, 2), "heading": round(o.rotation_euler.z, 4),
                                "pitch_deg": round(-math.degrees(o.rotation_euler.y), 2), "roll_deg": round(math.degrees(o.rotation_euler.x), 2),
                                "kind": o.get("vehicle")})

deps = bpy.context.evaluated_depsgraph_get()
for inst in deps.object_instances:
    if not inst.is_instance:
        continue
    n = inst.object.name
    mw = inst.matrix_world
    x, y, z = mw.translation
    if not inside(x, y):
        continue
    if n.startswith("ACC_w31_porta_aba"):
        yaw = mw.to_euler().z
        out["entrances"].append({"x": round(x, 2), "y": round(y, 2), "z": round(z, 2), "yaw": round(yaw, 4)})
    elif n.startswith(("ACC_w32_colonial", "ACC_w32_caixa", "ACC_w32_claraboia", "ACC_w32_vol_tecnico", "ACC_w32_casa_escada", "ACC_w32_fibro", "ACC_w32_metal")):
        out["roofs"].append({"kind": n, "x": round(x, 2), "y": round(y, 2), "z": round(z, 2)})

for o in bpy.data.objects:
    if o.name.startswith("OT_SlopeWorks_") and o.library is None:
        out["steps"].append({"name": o.name, "faces": len(o.data.polygons)})

# ground heights for the layout evidence (curved chains, rounded corners, vacant lots)
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bm = bmesh.new()
for o in bpy.data.objects:
    if o.get("sa_layer") in ("Roads", "Terrain") and o.type == "MESH" and o.library is None:
        me = o.evaluated_get(deps).to_mesh(); me.transform(o.matrix_world); bm.from_mesh(me); o.evaluated_get(deps).to_mesh_clear()
bmesh.ops.triangulate(bm, faces=bm.faces[:])
G = BVHTree.FromBMesh(bm); bm.free()
gz = lambda x, y: (lambda h: None if h[0] is None else round(h[0].z, 2))(G.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)), 800))
lay = Path(opt.root, "Logs", "layout-evidence.json")
if lay.is_file():
    L = json.loads(lay.read_text(encoding="utf-8"))
    for c in L["curves"]:
        c["z"] = [gz(px, py) for px, py in c["points"]]
    for c in L["corners"]:
        c["z"] = gz(*c["at"])
    for v in L["voids"]:
        v["z"] = gz(v["x"], v["y"])
    out["layout"] = L
Path(opt.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
print("EVIDENCE", {k: len(v) for k, v in out.items()})
