"""Generate the metric Santa Aurora masterplan blockout from masterplan_spec_v1.json.

This script creates a PRODUCTION MASTERPLAN BLOCKOUT only.
It intentionally does not create final low-poly art.

Run:
blender --background --factory-startup --python Tools/Blender/create_santa_aurora_masterplan.py -- --root PROJECT_ROOT

Output:
ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend
ArtSource/Blender/World/masterplan_generation_report.json
"""

import argparse
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root)
world_dir = root / "ArtSource" / "Blender" / "World"
spec_path = world_dir / "masterplan_spec_v1.json"
if not spec_path.exists():
    raise FileNotFoundError(spec_path)
spec = json.loads(spec_path.read_text(encoding="utf-8"))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0

def make_collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c

collections = {
    "terrain": make_collection("00_Terrain"),
    "districts": make_collection("01_Districts"),
    "roads": make_collection("02_Roads"),
    "campaign": make_collection("03_Campaign_Locations"),
    "life": make_collection("04_Life_Economy_Locations"),
    "labels": make_collection("05_Labels"),
    "guides": make_collection("06_Streaming_Guides"),
}

def material(name, color, roughness=.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mats = {
    "ground": material("MP_Ground", (.11,.13,.12), .95),
    "road": material("MP_Road", (.035,.04,.045), .88),
    "campaign": material("MP_Campaign", (.18,.32,.38), .7),
    "hero": material("MP_Hero", (.55,.32,.08), .62),
    "super": material("MP_SuperHero", (.55,.12,.08), .55),
    "life": material("MP_Life", (.18,.42,.20), .72),
    "guide": material("MP_Guide", (.35,.35,.38), .9),
    "district": material("MP_District", (.20,.22,.25), .92),
    "text": material("MP_Text", (.82,.85,.82), .8),
}

def link_only(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    return obj

def box(name, x, y, z, sx, sy, sz, mat, collection):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x,y,z))
    o = bpy.context.object
    o.name = name
    o.dimensions = (sx,sy,sz)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    link_only(o, collection)
    return o

def label(text, x, y, z, size=18, collection=None):
    curve = bpy.data.curves.new("MP_Label", "FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = .15
    obj = bpy.data.objects.new("Label_" + text, curve)
    (collection or collections["labels"]).objects.link(obj)
    obj.location = (x,y,z)
    obj.rotation_euler = (0,0,0)
    curve.materials.append(mats["text"])
    return obj

# Blender: X east/west, Y north/south, Z vertical.
world = spec["world"]
width = world["maxX"] - world["minX"]
depth = world["maxZ"] - world["minZ"]
box("World_Ground_8km", 0, 0, -2, width, depth, 4, mats["ground"], collections["terrain"])

# District bounds as shallow plates, slightly above terrain.
district_index = {d["id"]: d for d in spec["districts"]}
for d in spec["districts"]:
    minx,minz,maxx,maxz = d["bounds"]
    cx=(minx+maxx)/2
    cy=(minz+maxz)/2
    sx=maxx-minx
    sy=maxz-minz
    plate=box("District_"+d["id"],cx,cy,.25,sx,sy,.35,mats["district"],collections["districts"])
    plate.display_type="WIRE"
    label(d["name"], d["center"][0], d["center"][1], 40, 34)

# Roads as curves with metric widths.
def road_curve(r):
    curve_data=bpy.data.curves.new("Road_"+r["id"],"CURVE")
    curve_data.dimensions="3D"
    curve_data.bevel_depth=8.0 if r["class"]=="arterial" else 5.0
    curve_data.bevel_resolution=2
    spline=curve_data.splines.new("POLY")
    spline.points.add(1)
    a,b=r["from"],r["to"]
    spline.points[0].co=(a[0],a[1],1.0,1.0)
    spline.points[1].co=(b[0],b[1],1.0,1.0)
    obj=bpy.data.objects.new(r["id"]+"_"+r["name"],curve_data)
    collections["roads"].objects.link(obj)
    curve_data.materials.append(mats["road"])
    return obj

for road in spec["roads"]:
    road_curve(road)

# Campaign building envelopes.
for loc in spec["campaignLocations"]:
    priority=loc["priority"].lower()
    height = 30
    if priority=="hero": height=48
    if priority=="super-hero": height=70
    if loc["id"] in ("blackouttower","smarttower"): height=110
    if loc["id"]=="horizonte": height=38
    if loc["id"] in ("factory","logistics","drainage"): height=16
    mat=mats["campaign"]
    if priority=="hero": mat=mats["hero"]
    if priority=="super-hero": mat=mats["super"]
    o=box("LOC_"+loc["id"],loc["x"],loc["z"],height/2,loc["width"],loc["depth"],height,mat,collections["campaign"])
    o["facility_id"]=loc["id"]
    o["district"]=loc["district"]
    o["priority"]=loc["priority"]
    label(loc["id"],loc["x"],loc["z"],height+10,14)

# Life/economy markers: envelopes are deliberately small until property designs exist.
for loc in spec["lifeLocations"]:
    o=box("LIFE_"+loc["id"],loc["x"],loc["z"],6,20,20,12,mats["life"],collections["life"])
    o["facility_id"]=loc["id"]
    o["district"]=loc["district"]
    label(loc["id"],loc["x"],loc["z"],20,10)

# Streaming grid: empty guide objects at 1km intersections.
macro = spec["streaming"]["macroCellMeters"]
for x in range(world["minX"], world["maxX"]+1, macro):
    for y in range(world["minZ"], world["maxZ"]+1, macro):
        empty=bpy.data.objects.new(f"GRID_{x}_{y}",None)
        empty.empty_display_type="PLAIN_AXES"
        empty.empty_display_size=20
        empty.location=(x,y,5)
        collections["guides"].objects.link(empty)

# Cameras: top masterplan + oblique review.
bpy.ops.object.camera_add(location=(0,0,9000))
cam_top=bpy.context.object
cam_top.name="CAM_Masterplan_Top"
cam_top.data.type="ORTHO"
cam_top.data.ortho_scale=8800
cam_top.rotation_euler=(0,0,0)
# Camera points down local -Z by default; no rotation needed at origin when located above.
link_only(cam_top, collections["guides"])

bpy.ops.object.camera_add(location=(6200,-6200,4200))
cam_oblique=bpy.context.object
cam_oblique.name="CAM_Masterplan_Oblique"
link_only(cam_oblique, collections["guides"])
direction=Vector((0,0,0))-cam_oblique.location
cam_oblique.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
cam_oblique.data.lens=52

scene.camera=cam_oblique

# World metadata.
scene["facility_world"]="Santa Aurora"
scene["facility_masterplan_schema"]=spec["schemaVersion"]
scene["facility_world_size_m"]=8000
scene["facility_blockout_only"]=True

output = world_dir / "SantaAurora_Masterplan_v1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(output))

report={
    "blend":str(output.relative_to(root)),
    "schemaVersion":spec["schemaVersion"],
    "units":"meters",
    "worldSizeMeters":[width,depth],
    "districts":len(spec["districts"]),
    "campaignLocations":len(spec["campaignLocations"]),
    "lifeEconomyLocations":len(spec["lifeLocations"]),
    "roads":len(spec["roads"]),
    "macroCellMeters":spec["streaming"]["macroCellMeters"],
    "subCellMeters":spec["streaming"]["subCellMeters"],
    "status":"generated-blockout-not-final-art"
}
(world_dir/"masterplan_generation_report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("SANTA AURORA MASTERPLAN BLOCKOUT GENERATED", json.dumps(report))
