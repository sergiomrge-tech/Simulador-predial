"""Renders the Grand Aurora review cameras from the saved blend (separate process = clean GPU context).

blender --background ArtSource/Blender/Resort/SantaAurora_GrandAurora_v1.blend --python Tools/Blender/render_grand_aurora.py -- --root ROOT [--night] [--only NAME] [--samples N]
"""
import argparse
import sys
from pathlib import Path

import bpy

p = argparse.ArgumentParser()
p.add_argument("--root", required=True)
p.add_argument("--night", action="store_true")
p.add_argument("--only", default="")
p.add_argument("--samples", type=int, default=48)
o = p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])

sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x, sc.render.resolution_y = 1600, 900
sc.render.image_settings.file_format = "JPEG"
sc.render.image_settings.quality = 90
try:
    sc.eevee.taa_render_samples = o.samples
except AttributeError:
    pass
out = Path(o.root) / "ArtSource" / "Blender" / "Resort" / ("Capturas_noite" if o.night else "Capturas")
out.mkdir(parents=True, exist_ok=True)
for cam in sorted((x for x in bpy.data.objects if x.type == "CAMERA"), key=lambda c: c.name):
    if o.only and o.only not in cam.name:
        continue
    sc.camera = cam
    sc.render.filepath = str(out / (cam.name[4:] + ".jpg"))
    bpy.ops.render.render(write_still=True)
    print("rendered", cam.name)
