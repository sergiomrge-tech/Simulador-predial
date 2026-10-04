"""Generate the metric Santa Aurora W1 masterplan blockout from masterplan_spec_v1.json.

This script creates a PRODUCTION MASTERPLAN BLOCKOUT (S0 / massing) only.
It intentionally does not create final art; the "no low-poly" rule applies to production assets, not to W1 massing.
The layout (roads, local streets, driveways, shells, composite massing) comes from Tools/Map/masterplan_layout.py,
the same module used by Tools/Map/validate_masterplan.py.

Run:
blender --background --factory-startup --python Tools/Blender/create_santa_aurora_masterplan.py -- --root PROJECT_ROOT

Output:
ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend
ArtSource/Blender/World/masterplan_generation_report.json
The older ArtSource/Blender/SantaAurora_Masterplan.blend is never touched.
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
root = Path(opts.root).resolve()
sys.path.insert(0, str(root / "Tools" / "Map"))
from masterplan_layout import Layout, ROAD_WIDTH, load_spec, load_registry  # noqa: E402

world_dir = root / "ArtSource" / "Blender" / "World"
spec = load_spec(root)
layout = Layout(spec, load_registry(root))
layout_report = layout.checks()
if layout.errors:
    raise RuntimeError("masterplan layout invalid; run Tools/Map/validate_masterplan.py:\n" + "\n".join(layout.errors))

for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for col in list(bpy.data.collections):
    bpy.data.collections.remove(col)

scene = bpy.context.scene
scene.name = "SantaAurora_W1"
scene.unit_settings.system = "METRIC"
scene.unit_settings.length_unit = "METERS"
scene.unit_settings.scale_length = 1.0


def make_collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or scene.collection).children.link(c)
    return c


collections = {
    "terrain": make_collection("00_Terrain"),
    "districts": make_collection("01_Districts"),
    "roads": make_collection("02_Roads"),
    "campaign": make_collection("03_Campaign_Locations"),
    "life": make_collection("04_Life_Economy_Locations"),
    "labels": make_collection("05_Labels"),
    "guides": make_collection("06_Streaming_Guides"),
    "shells": make_collection("07_Skyline_Shells"),
    "cameras": make_collection("08_Cameras"),
    "subgrid": make_collection("09_Streaming_Subgrid"),
    "fabric": make_collection("10_Block_Fabric"),
}
collections["subgrid"].hide_render = True


def material(name, color, roughness=.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)  # Workbench / viewport colour
    mat.roughness = roughness
    mat.metallic = metallic
    tree = getattr(mat, "node_tree", None)
    bsdf = tree.nodes.get("Principled BSDF") if tree else None
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


DISTRICT_COLORS = {
    "old": (.50, .38, .27), "expansion": (.38, .46, .32), "civic": (.48, .46, .38),
    "corporate": (.32, .38, .50), "industrial": (.42, .40, .37), "technology": (.28, .45, .48),
}
SHELL_COLORS = {
    "old": (.86, .74, .60), "expansion": (.86, .86, .78), "civic": (.90, .88, .80),
    "corporate": (.72, .80, .90), "industrial": (.70, .67, .62), "technology": (.74, .88, .90),
}
mats = {
    "ground": material("MP_Ground", (.24, .25, .22), .95),
    "arterial": material("MP_Road_Arterial", (.05, .05, .055), .88),
    "collector": material("MP_Road_Collector", (.08, .08, .085), .88),
    "local": material("MP_Road_Local", (.17, .17, .18), .9),
    "driveway": material("MP_Driveway", (.30, .28, .20), .9),
    "canal": material("MP_Canal_Water", (.06, .16, .22), .15),
    "park": material("MP_Park", (.12, .26, .10), .95),
    "pad": material("MP_Lot_Pad", (.42, .40, .36), .9),
    "campaign": material("MP_Campaign", (.18, .45, .55), .7),
    "hero": material("MP_Hero", (.85, .50, .12), .62),
    "super": material("MP_SuperHero", (.80, .16, .10), .55),
    "life": material("MP_Life", (.25, .75, .30), .72),
    "grid": material("MP_Streaming_Grid", (.85, .85, .20), .9),
    "subgrid": material("MP_Streaming_Subgrid", (.55, .55, .25), .9),
    "text": material("MP_Text", (.95, .95, .92), .8),
    "district_text": material("MP_District_Text", (1.0, .92, .70), .8),
}
for did, col in DISTRICT_COLORS.items():
    mats["district_" + did] = material("MP_District_" + did, col, .95)
for did, col in SHELL_COLORS.items():
    mats["shell_" + did] = material("MP_Shell_" + did, col, .85)
    mats["fabric_" + did] = material("MP_Fabric_" + did, tuple(c * .82 for c in col), .9)


def mesh_object(name, verts, faces, mat, collection):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    me.materials.append(mat)
    obj = bpy.data.objects.new(name, me)
    collection.objects.link(obj)
    return obj


def box_geometry(x, y, z0, sx, sy, sz, verts, faces):
    b = len(verts)
    x0, x1, y0, y1, z1 = x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z0 + sz
    verts += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces += [(b, b + 3, b + 2, b + 1), (b + 4, b + 5, b + 6, b + 7), (b, b + 1, b + 5, b + 4),
              (b + 1, b + 2, b + 6, b + 5), (b + 2, b + 3, b + 7, b + 6), (b + 3, b, b + 4, b + 7)]


def box(name, x, y, z0, sx, sy, sz, mat, collection):
    verts, faces = [], []
    box_geometry(x, y, z0, sx, sy, sz, verts, faces)
    return mesh_object(name, verts, faces, mat, collection)


def ribbon_geometry(points, width, z, verts, faces, joints=True):
    half = width / 2
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L == 0:
            continue
        nx, ny = -dy / L * half, dx / L * half
        b = len(verts)
        verts += [(ax + nx, ay + ny, z), (ax - nx, ay - ny, z), (bx - nx, by - ny, z), (bx + nx, by + ny, z)]
        faces.append((b, b + 1, b + 2, b + 3))
    if joints:
        for (px, py) in points[1:-1]:
            b = len(verts)
            verts.append((px, py, z))
            for k in range(8):
                a = k * math.pi / 4
                verts.append((px + math.cos(a) * half * 1.08, py + math.sin(a) * half * 1.08, z))
            for k in range(8):
                faces.append((b, b + 1 + k, b + 1 + (k + 1) % 8))


def label(text, x, y, z, size, collection=None, mat=None):
    curve = bpy.data.curves.new("MP_Label_" + text, "FONT")
    curve.body = text
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = size * .02
    obj = bpy.data.objects.new("Label_" + text, curve)
    (collection or collections["labels"]).objects.link(obj)
    obj.location = (x, y, z)
    curve.materials.append(mat or mats["text"])
    return obj


# Blender: X east, Y north (spec z), Z up.
wx0, wz0, wx1, wz1 = layout.world
width, depth = wx1 - wx0, wz1 - wz0
ground = box("World_Ground_8km", 0, 0, -4, width, depth, 4, mats["ground"], collections["terrain"])
ground["facility_world_size_m"] = width

# District tint plates from resolved ownership (250 m subcells), so seams never double up.
SUB = spec["streaming"]["subCellMeters"]
for d in spec["districts"]:
    verts, faces = [], []
    for ix in range(int(width // SUB)):
        for iz in range(int(depth // SUB)):
            cx, cz = wx0 + ix * SUB + SUB / 2, wz0 + iz * SUB + SUB / 2
            if layout.owner((cx, cz)) == d["id"]:
                b = len(verts)
                verts += [(cx - SUB / 2, cz - SUB / 2, .3), (cx + SUB / 2, cz - SUB / 2, .3),
                          (cx + SUB / 2, cz + SUB / 2, .3), (cx - SUB / 2, cz + SUB / 2, .3)]
                faces.append((b, b + 1, b + 2, b + 3))
    o = mesh_object("District_" + d["id"], verts, faces, mats["district_" + d["id"]], collections["districts"])
    o["district"] = d["id"]
    o["district_name"] = d["name"]
    o["nominal_bounds"] = d["bounds"]
    label(d["name"], d["center"][0], d["center"][1], 160, 120, mat=mats["district_text"])

# Open spaces.
for osp in layout.open_spaces:
    o = box("OPEN_" + osp["id"], osp["x"], osp["z"], 0, osp["width"], osp["depth"], .8, mats["park"], collections["terrain"])
    o["facility_id"] = osp["id"]

# Canal.
if layout.canal:
    verts, faces = [], []
    ribbon_geometry(layout.canal["points"], layout.canal["width"], .9, verts, faces)
    o = mesh_object("CANAL_" + layout.canal["id"], verts, faces, mats["canal"], collections["roads"])
    o["facility_id"] = layout.canal["id"]
    o["width_m"] = layout.canal["width"]

# Spec roads as flat metric ribbons (centre-line polylines kept as custom property).
ROAD_Z = {"arterial": 3.0, "collector": 2.5, "local": 2.0, "driveway": 1.5}
for road in layout.roads:
    verts, faces = [], []
    ribbon_geometry(road["points"], road["width"], ROAD_Z[road["class"]], verts, faces)
    o = mesh_object(f"{road['id']}_{road['name']}", verts, faces, mats[road["class"]], collections["roads"])
    o["road_id"] = road["id"]
    o["road_class"] = road["class"]
    o["width_m"] = road["width"]
    o["centerline"] = json.dumps(road["points"])
    mid = road["points"][len(road["points"]) // 2]
    label(f"{road['id']} {road['name']}", mid[0], mid[1] + 45, 8, 34)

for did, edges in layout.local_edges.items():
    verts, faces = [], []
    for a, b in edges:
        ribbon_geometry([a, b], ROAD_WIDTH["local"], ROAD_Z["local"], verts, faces, joints=False)
    o = mesh_object("LOCAL_Streets_" + did, verts, faces, mats["local"], collections["roads"])
    o["road_class"] = "local"
    o["district"] = did

verts, faces = [], []
for dw in layout.driveways:
    ribbon_geometry([dw["a"], dw["b"]], ROAD_WIDTH["driveway"], ROAD_Z["driveway"], verts, faces, joints=False)
mesh_object("ACCESS_Driveways", verts, faces, mats["driveway"], collections["roads"])

# Campaign locations: lot pad (canonical ID object) + composite massing volumes.
registry_by_id = {l["id"]: l for l in layout.registry.get("locations", [])}
for loc in layout.campaign:
    priority = loc["priority"].lower()
    mat = mats["campaign"]
    if priority == "hero":
        mat = mats["hero"]
    if priority.startswith("super-hero"):
        mat = mats["super"]
    pad = box("LOC_" + loc["id"], loc["x"], loc["z"], 0, loc["width"], loc["depth"], 1.0, mats["pad"], collections["campaign"])
    pad["facility_id"] = loc["id"]
    pad["district"] = loc["district"]
    pad["priority"] = loc["priority"]
    pad["footprint_m"] = [loc["width"], loc["depth"]]
    pad["access_road"] = layout.access[loc["id"]]["road"]
    reg = registry_by_id.get(loc["id"])
    if reg:
        pad["visible_floors"] = reg.get("visibleFloors", 0)
        pad["chapters"] = ",".join(reg.get("chapters", []))
    top = 0
    for v in layout.campaign_volumes(loc):
        vo = box(f"LOC_{loc['id']}__{v['role']}", v["x"], v["z"], 1.0, v["w"], v["d"], v["h"], mat, collections["campaign"])
        vo["facility_id"] = loc["id"]
        vo["massing_role"] = v["role"]
        vo.parent = pad
        vo.matrix_parent_inverse = pad.matrix_world.inverted()
        top = max(top, v["h"])
    label(loc["id"], loc["x"], loc["z"], top + 18, 40)

# Life/economy markers: deliberately small until property designs exist.
for loc in layout.life:
    h = {"home.starter": 13.0}.get(loc["id"], 12.0)
    o = box("LIFE_" + loc["id"], loc["x"], loc["z"], 0, 20, 20, h, mats["life"], collections["life"])
    o["facility_id"] = loc["id"]
    o["district"] = loc["district"]
    o["access_road"] = layout.access[loc["id"]]["road"]
    label(loc["id"], loc["x"], loc["z"] - 30, h + 6, 22)

# Skyline / background shells.
for s in layout.shells:
    o = box(s["id"], s["x"], s["z"], 0, s["w"], s["d"], s["h"], mats["shell_" + s["district"]], collections["shells"])
    o["district"] = s["district"]
    o["floors"] = s["floors"]
    o["shell"] = True

# Block fabric: one merged mesh per district (urban mass, not individual buildings).
for did in layout.districts:
    verts, faces = [], []
    for f in layout.fabric:
        if f["district"] == did:
            r = f["rect"]
            box_geometry((r[0] + r[2]) / 2, (r[1] + r[3]) / 2, 0, r[2] - r[0], r[3] - r[1], f["h"], verts, faces)
    o = mesh_object("FABRIC_" + did, verts, faces, mats["fabric_" + did], collections["fabric"])
    o["district"] = did
    o["block_fabric"] = True

# Streaming: 1 km macro grid strips + named cell empties; 250 m subgrid hidden from render by default.
macro = spec["streaming"]["macroCellMeters"]
verts, faces = [], []
for x in range(wx0, wx1 + 1, macro):
    ribbon_geometry([(x, wz0), (x, wz1)], 8, 6, verts, faces, joints=False)
for z in range(wz0, wz1 + 1, macro):
    ribbon_geometry([(wx0, z), (wx1, z)], 8, 6, verts, faces, joints=False)
mesh_object("GRID_Macro_1km", verts, faces, mats["grid"], collections["guides"])
verts, faces = [], []
for x in range(wx0, wx1 + 1, SUB):
    if (x - wx0) % macro:
        ribbon_geometry([(x, wz0), (x, wz1)], 3, 5.5, verts, faces, joints=False)
for z in range(wz0, wz1 + 1, SUB):
    if (z - wz0) % macro:
        ribbon_geometry([(wx0, z), (wx1, z)], 3, 5.5, verts, faces, joints=False)
mesh_object("GRID_Sub_250m", verts, faces, mats["subgrid"], collections["subgrid"])
for ix in range(int(width // macro)):
    for iz in range(int(depth // macro)):
        name = f"SA_M{ix:02d}_{iz:02d}"
        cx, cz = wx0 + ix * macro + macro / 2, wz0 + iz * macro + macro / 2
        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = "CUBE"
        empty.empty_display_size = macro / 2
        empty.location = (cx, cz, 0)
        empty["streaming_cell"] = name
        empty["district_owner"] = layout.owner((cx, cz)) or "transition"
        collections["guides"].objects.link(empty)
        label(name, cx - macro / 2 + 120, cz + macro / 2 - 50, 7, 34, collection=collections["subgrid"])


# Cameras.
def camera(name, loc, target=None, rot=None, ortho=None, lens=35):
    data = bpy.data.cameras.new(name)
    data.clip_start = 20
    data.clip_end = 30000
    if ortho:
        data.type = "ORTHO"
        data.ortho_scale = ortho
    else:
        data.lens = lens
    obj = bpy.data.objects.new(name, data)
    collections["cameras"].objects.link(obj)
    obj.location = loc
    if target is not None:
        obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    elif rot is not None:
        obj.rotation_euler = rot
    return obj


camera("CAM_Masterplan_Top", (0, 0, 9000), rot=(0, 0, 0), ortho=8400)
cam_oblique = camera("CAM_Masterplan_Oblique", (-3600, -7400, 3900), target=(0, -250, 0), lens=30)
TILT = math.radians(32)
for d in spec["districts"]:
    x0, z0, x1, z1 = d["bounds"]
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    dist = 7000
    scale = max((x1 - x0) * 1.06, (z1 - z0) * math.cos(TILT) * 16 / 9 * 1.04)
    camera("CAM_District_" + d["id"], (cx, cz - dist * math.sin(TILT), dist * math.cos(TILT)), rot=(TILT, 0, 0), ortho=scale)
camera("CAM_Skyline", (-1400, -3400, 420), target=(2300, 300, 40), lens=40)
scene.camera = cam_oblique

# Workbench review look (renders are real Blender captures of this scene).
scene.render.engine = "BLENDER_WORKBENCH"
shading = scene.display.shading
shading.light = "STUDIO"
shading.color_type = "MATERIAL"
shading.show_shadows = True
shading.shadow_intensity = .45
shading.show_cavity = True
shading.cavity_type = "WORLD"
shading.show_object_outline = False
scene.display.light_direction = (-0.45, -0.55, 0.7)
world = bpy.data.worlds.new("MP_World")
world.color = (.55, .62, .70)
scene.world = world

# World metadata.
scene["facility_world"] = "Santa Aurora"
scene["facility_masterplan_schema"] = spec["schemaVersion"]
scene["facility_world_size_m"] = width
scene["facility_blockout_only"] = True
scene["facility_stage"] = "W1-S0-massing"

output = world_dir / "SantaAurora_Masterplan_v1.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)

counts = {c.name: len(c.all_objects) for c in scene.collection.children}
report = {
    "blend": output.relative_to(root).as_posix(),
    "blenderVersion": bpy.app.version_string,
    "schemaVersion": spec["schemaVersion"],
    "units": "meters",
    "worldSizeMeters": [width, depth],
    "districts": len(spec["districts"]),
    "campaignLocations": len(spec["campaignLocations"]),
    "lifeEconomyLocations": len(spec["lifeLocations"]),
    "roads": len(spec["roads"]),
    "macroCellMeters": spec["streaming"]["macroCellMeters"],
    "subCellMeters": spec["streaming"]["subCellMeters"],
    "objectCount": len(bpy.data.objects),
    "collectionObjectCounts": counts,
    "layout": {k: v for k, v in layout_report.items() if k != "access"},
    "status": "generated-blockout-not-final-art",
}
(world_dir / "masterplan_generation_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("SANTA AURORA MASTERPLAN BLOCKOUT GENERATED", json.dumps({k: report[k] for k in ("blend", "objectCount", "blenderVersion")}))
