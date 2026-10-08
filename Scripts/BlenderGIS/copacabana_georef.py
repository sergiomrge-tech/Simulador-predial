"""Build a geographically referenced Blender scene using OFFICIAL BlenderGIS.

Requires a checkout of https://github.com/domlysz/BlenderGIS at /tmp/BlenderGIS.
This creates a separate scene from the gameplay-aligned OBJ (which uses local axes).
No proprietary basemap/imagery is imported.
"""
from pathlib import Path
import json
import math
import sys

import bpy

sys.path.insert(0, "/tmp")
from BlenderGIS.geoscene import GeoScene  # actual BlenderGIS library

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Tools" / "Copacabana" / "data"
config = json.loads((ROOT / "Tools" / "Copacabana" / "region.json").read_text())
source = DATA / "copacabana_base.obj"
if not source.is_file():
    raise RuntimeError("Source real OSM OBJ not available")

# OBJ: local X runs along shore, local Y inland.
# Rotate by +46 degrees so Blender world X runs East and Y runs North.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.obj_import(filepath=str(source), forward_axis="Y", up_axis="Z")
for ob in bpy.context.scene.objects:
    if ob.type == "MESH":
        ob.rotation_euler.z = math.radians(
            config["axis_angle_degrees_counterclockwise_from_east"])

# These values are computed from the Avenida Atlantica reference in
# EPSG:32723 and shifted 300 m inward, as defined in region.json.
# Recalculate if the region origin is changed.
utm_easting, utm_northing = 685834.9456167693, 7458580.830587678
gis = GeoScene(bpy.context.scene)
gis.crs = config["crs"]
gis.setOriginPrj(utm_easting, utm_northing, synch=False)
if not gis.isGeoref:
    raise RuntimeError("BlenderGIS does not validate georeferencing")
bpy.context.scene["source"] = "© OpenStreetMap contributors; ODbL 1.0"
bpy.context.scene["original_footprints"] = "Real OSM. Unknown heights visualized at 18 m."
bpy.context.scene["utm_center_easting"] = utm_easting
bpy.context.scene["utm_center_northing"] = utm_northing
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0

out = DATA / "Copacabana_BlenderGIS_UTM23S.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
print("GEOSCENE VERIFIED:", gis.isGeoref, gis.crs, gis.getOriginPrj())
print("GEOREFERENCED BLEND:", out, out.stat().st_size, "bytes")
