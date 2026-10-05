"""Eye-level / aerial review views of the W3 slice (never saves the .blend).

--views "name:x,y[,tx,ty][,h];..."   The camera snaps to the nearest asphalt (a player stands on the road), 1.65 m above it (h overrides).
  - with (tx,ty) it looks at that point; without, it looks along the street (direction of the asphalt strip under it).
  - "name:x,y,tx,ty,h,free" places the camera exactly at (x,y) (aerial views)."""
import argparse
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector, kdtree
from mathutils.bvhtree import BVHTree

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--views", required=True)
ap.add_argument("--w", type=int, default=1600)
ap.add_argument("--h", type=int, default=900)
ap.add_argument("--lens", type=float, default=24.0)
opt = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = opt.w, opt.h
sc.render.image_settings.file_format = "JPEG"
sc.render.image_settings.quality = 90
deps = bpy.context.evaluated_depsgraph_get()
bm = bmesh.new()
asphalt = []
for o in bpy.data.objects:
    if o.get("sa_layer") in ("Roads", "Terrain") and o.type == "MESH" and o.library is None:
        me = o.evaluated_get(deps).to_mesh()
        me.transform(o.matrix_world)
        if o.get("sa_layer") == "Roads":
            for p in me.polygons:
                mat = me.materials[p.material_index].name if p.material_index < len(me.materials) and me.materials[p.material_index] else ""
                if mat.startswith("asfalto") and p.area > 6.0:
                    vs = [me.vertices[i].co.copy() for i in p.vertices]
                    best = max(((vs[i], vs[(i + 1) % len(vs)]) for i in range(len(vs))), key=lambda e: (e[1] - e[0]).length)
                    d = (best[1] - best[0])
                    d.z = 0
                    if d.length > .1:
                        asphalt.append((p.center.copy(), d.normalized()))
        bm.from_mesh(me)
        o.evaluated_get(deps).to_mesh_clear()
bmesh.ops.triangulate(bm, faces=bm.faces[:])
G = BVHTree.FromBMesh(bm)
bm.free()
kd = kdtree.KDTree(len(asphalt))
for i, (c, _d) in enumerate(asphalt):
    kd.insert(c, i)
kd.balance()


def gz(x, y):
    h = G.ray_cast(Vector((x, y, 400)), Vector((0, 0, -1)), 800)
    return h[0].z if h[0] is not None else 0.0


cam = bpy.data.cameras.new("VIEW")
cam.lens = opt.lens
cam.clip_end = 3000
co = bpy.data.objects.new("VIEW", cam)
sc.collection.objects.link(co)
sc.camera = co
out = Path(opt.out)
out.mkdir(parents=True, exist_ok=True)
for item in opt.views.split(";"):
    name, rest = item.split(":")
    parts = rest.split(",")
    free = parts[-1] == "free"
    v = [float(t) for t in parts if t != "free"]
    x, y = v[0], v[1]
    h = 1.65
    target = None
    if len(v) >= 4:
        target = (v[2], v[3])
    if len(v) >= 5:
        h = v[4]
    if free:
        pos = Vector((x, y, gz(x, y) + h))
        look = Vector((target[0], target[1], gz(*target) + 1.0))
    else:
        c, idx, _dist = kd.find(Vector((x, y, 0)))
        centre, dirn = asphalt[idx]
        pos = Vector((centre.x, centre.y, centre.z + h))
        if target is not None:
            look = Vector((target[0], target[1], gz(*target) + 1.6))
        else:
            ahead = pos + dirn * 40
            look = Vector((ahead.x, ahead.y, gz(ahead.x, ahead.y) + 1.5))
    co.location = pos
    co.rotation_euler = (look - pos).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = str(out / f"{name}.jpg")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", sc.render.filepath, tuple(round(t, 1) for t in pos))
