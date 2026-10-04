"""W3.2: dump the scene-only interior fill lights of a W2 hero file to JSON (world transforms), so the slice can recreate them.

Run (reads the hero file, never saves it):
blender -b --factory-startup ArtSource/Blender/World/OldTown/Heroes/W2_x.blend --python Tools/Blender/dump_hero_fills.py -- --root ROOT --out hero_interior_fills_w32.json
The hero files keep their fills in W2_<id>__SceneOnly (not part of the linked W2_<id> collection), so a slice that links the hero
only receives the practical lamps; the fills restore the warm, occluded interior light the hero captures were made with.
"""
import json
import sys
from pathlib import Path

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
root = Path(argv[argv.index("--root") + 1])
out = root / "ArtSource" / "Blender" / "World" / "OldTown" / argv[argv.index("--out") + 1]
hid = bpy.context.scene.get("sa_hero", "")
fills = []
for o in bpy.data.objects:
    if o.type == "LIGHT" and o.data.type != "SUN" and "fill" in o.name:
        d = o.data
        fills.append({"name": o.name, "type": d.type, "energy": d.energy, "color": list(d.color), "shape": getattr(d, "shape", ""),
                      "size": getattr(d, "size", 0.0), "size_y": getattr(d, "size_y", 0.0), "shadow": bool(getattr(d, "use_shadow", True)),
                      "matrix": [list(r) for r in o.matrix_world]})
db = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
db[hid] = fills
out.write_text(json.dumps(db, indent=1) + "\n", encoding="utf-8")
print("HERO FILLS", hid, len(fills))
