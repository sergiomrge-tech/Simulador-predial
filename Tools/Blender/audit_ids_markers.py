"""List stable IDs and gameplay markers of an Old Town base .blend (for before/after integrity checks).

blender -b --factory-startup <base.blend> --python Tools/Blender/audit_ids_markers.py -- --out <file.json>
Writes: marker names (GP_*, SLOT_*, PROXY_*, HERO_<id> anchors), facility_id properties, linked W2 hero instances.
Positions are not compared on purpose: W2.5 changes the terrain heights, IDs and names must stay identical.
"""
import argparse
import json
import sys

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--out", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
markers = sorted(o.name for o in bpy.data.objects if o.library is None and o.name.startswith(("GP_", "SLOT_", "PROXY_")))
anchors = sorted(o.name for o in bpy.data.objects if o.library is None and o.type == "EMPTY" and o.name.startswith("HERO_"))
fids = sorted({o.get("facility_id") for o in bpy.data.objects if o.library is None and o.get("facility_id")})
linked = sorted(o.name for o in bpy.data.objects if o.instance_type == "COLLECTION" and o.instance_collection is not None)
libs = sorted(bpy.path.abspath(l.filepath).replace("\\", "/").split("/Heroes/")[-1] for l in bpy.data.libraries)
json.dump({"markers": markers, "heroAnchors": anchors, "facilityIds": fids, "linkedInstances": linked, "libraries": libs},
          open(opts.out, "w", encoding="utf-8"), indent=1)
print("AUDIT", len(markers), len(anchors), len(fids), len(linked))
