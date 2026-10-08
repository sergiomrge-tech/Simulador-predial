"""Open a real OSM-derived OBJ in Blender and save an editable .blend.

Usage:
  blender --background --factory-startup --python Tools/Copacabana/blender_build.py
The BlenderGIS add-on can additionally open copacabana.osm for GIS workflows.
This script does not need BlenderGIS enabled just to import the OBJ.
"""
from pathlib import Path
import bpy

base = Path(__file__).resolve().parent
data = base / "data"
obj = data / "copacabana_base.obj"
if not obj.exists():
    raise RuntimeError("Missing real OSM OBJ. Run pipeline.py first.")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
if hasattr(bpy.ops.wm, "obj_import"):
    bpy.ops.wm.obj_import(filepath=str(obj), forward_axis="Y", up_axis="Z")
else:
    bpy.ops.import_scene.obj(filepath=str(obj), axis_forward="Y", axis_up="Z")
scene = bpy.context.scene
scene["source"] = "© OpenStreetMap contributors (ODbL 1.0)"
scene["source_url"] = "https://www.openstreetmap.org/copyright"
scene["local_frame"] = "X along Copacabana shoreline; Y inland; Z up; meters"
scene["realism_notice"] = "OSM building footprints; missing heights are estimated"
bpy.ops.wm.save_as_mainfile(filepath=str(data / "Copacabana_OSM_Base.blend"))
print("SAVED:", data / "Copacabana_OSM_Base.blend")
