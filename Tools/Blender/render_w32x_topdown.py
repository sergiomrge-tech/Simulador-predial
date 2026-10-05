"""Top-down / oblique review renders of the W3 slice (never saves the .blend).  --out DIR --name PREFIX"""
import argparse, sys, math
from pathlib import Path
import bpy
from mathutils import Vector
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--name", default="w32x")
ap.add_argument("--cx", type=float, default=-2625.0); ap.add_argument("--cy", type=float, default=-1875.0); ap.add_argument("--size", type=float, default=1300.0)
ap.add_argument("--res", type=int, default=2400)
opt = ap.parse_args(sys.argv[sys.argv.index("--") + 1:])
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = opt.res
sc.render.image_settings.file_format = "JPEG"; sc.render.image_settings.quality = 88
cam = bpy.data.cameras.new("TOP"); cam.type = "ORTHO"; cam.ortho_scale = opt.size; cam.clip_end = 3000
co = bpy.data.objects.new("TOP", cam); sc.collection.objects.link(co)
co.location = (opt.cx, opt.cy, 600); co.rotation_euler = (0, 0, 0)
sc.camera = co
out = Path(opt.out); out.mkdir(parents=True, exist_ok=True)
sc.render.filepath = str(out / f"{opt.name}_topdown.jpg")
bpy.ops.render.render(write_still=True)
print("RENDERED", sc.render.filepath)
