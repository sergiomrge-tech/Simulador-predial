"""Open a real OSM-derived OBJ in Blender and save an editable .blend.

Usage:
  blender --background --factory-startup --python Tools/Copacabana/blender_build.py
The BlenderGIS add-on can additionally open copacabana.osm for GIS workflows.
This script does not need BlenderGIS enabled just to import the OBJ.
"""
from pathlib import Path
import bpy
from mathutils import Vector

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
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
bpy.ops.object.camera_add(location=(1200, -1400, 1850))
cam = bpy.context.object
direction = Vector((0, 0, 0)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
cam.data.type = "ORTHO"
cam.data.ortho_scale = 2800
scene.camera = cam
bpy.ops.object.light_add(type="SUN", location=(250, -200, 1500))
sun = bpy.context.object
sun.data.energy = 3.0
sun.rotation_euler = (0.5, -0.35, -0.45)
# Ubuntu's Blender build can lack the optional OpenImageDenoiser library.
# Keep a real render, but disable denoising for portable CPU headless mode.
if scene.render.engine == "CYCLES":
    if hasattr(scene.cycles, "use_denoising"):
        scene.cycles.use_denoising = False
    if hasattr(bpy.context.view_layer.cycles, "use_denoising"):
        bpy.context.view_layer.cycles.use_denoising = False
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(data / "Copacabana_OSM_Base_preview.png")
scene["source"] = "© OpenStreetMap contributors (ODbL 1.0)"
scene["source_url"] = "https://www.openstreetmap.org/copyright"
scene["local_frame"] = "X along Copacabana shoreline; Y inland; Z up; meters"
scene["realism_notice"] = "OSM building footprints; missing heights are estimated"
bpy.ops.wm.save_as_mainfile(filepath=str(data / "Copacabana_OSM_Base.blend"))
print("SAVED:", data / "Copacabana_OSM_Base.blend")
bpy.ops.render.render(write_still=True)
print("RENDERED:", scene.render.filepath)
