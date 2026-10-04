"""Reopen SantaAurora_Masterplan_v1.blend in a fresh Blender process, audit it and render the W1 review captures.

Run (the .blend is opened by Blender itself, proving it reopens):
blender --background --factory-startup ArtSource/Blender/World/SantaAurora_Masterplan_v1.blend --python Tools/Blender/verify_masterplan_v1.py -- --root PROJECT_ROOT [--no-render]

Output:
ArtSource/Blender/World/Reviews/W1/*.jpg   real Workbench renders of the saved file
ArtSource/Blender/World/Reviews/W1/w1_reopen_report.json
"""

import argparse
import bpy
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--no-render", action="store_true")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
world_dir = root / "ArtSource" / "Blender" / "World"
review_dir = world_dir / "Reviews" / "W1"
review_dir.mkdir(parents=True, exist_ok=True)
spec = json.loads((world_dir / "masterplan_spec_v1.json").read_text(encoding="utf-8"))

scene = bpy.context.scene
errors = []

blend_path = Path(bpy.data.filepath)
if blend_path.name != "SantaAurora_Masterplan_v1.blend":
    errors.append(f"unexpected file opened: {bpy.data.filepath}")

# Missing data: linked libraries, external images, missing fonts.
missing = []
for lib in bpy.data.libraries:
    if not Path(bpy.path.abspath(lib.filepath)).exists():
        missing.append("library:" + lib.filepath)
for img in bpy.data.images:
    if img.source == "FILE" and not img.packed_file and not Path(bpy.path.abspath(img.filepath)).exists():
        missing.append("image:" + img.filepath)
for font in bpy.data.fonts:
    if font.filepath != "<builtin>" and not font.packed_file and not Path(bpy.path.abspath(font.filepath)).exists():
        missing.append("font:" + font.filepath)
if missing:
    errors.append("missing data: " + ", ".join(missing))

expected_collections = ["00_Terrain", "01_Districts", "02_Roads", "03_Campaign_Locations", "04_Life_Economy_Locations",
                        "05_Labels", "06_Streaming_Guides", "07_Skyline_Shells", "08_Cameras", "09_Streaming_Subgrid", "10_Block_Fabric"]
present = [c.name for c in scene.collection.children]
for name in expected_collections:
    if name not in present:
        errors.append("missing collection " + name)

by_facility = {}
for o in bpy.data.objects:
    fid = o.get("facility_id")
    if fid:
        by_facility.setdefault(fid, []).append(o.name)
for loc in spec["campaignLocations"]:
    if "LOC_" + loc["id"] not in bpy.data.objects:
        errors.append("missing campaign object LOC_" + loc["id"])
    else:
        pad = bpy.data.objects["LOC_" + loc["id"]]
        dims = [round(v, 2) for v in pad.dimensions[:2]]
        if dims != [loc["width"], loc["depth"]]:
            errors.append(f"footprint mismatch {loc['id']}: {dims} vs {[loc['width'], loc['depth']]}")
for loc in spec["lifeLocations"]:
    if "LIFE_" + loc["id"] not in bpy.data.objects:
        errors.append("missing life object LIFE_" + loc["id"])
for d in spec["districts"]:
    if "District_" + d["id"] not in bpy.data.objects:
        errors.append("missing district " + d["id"])
roads = [o for o in bpy.data.objects if o.get("road_id")]
if len(roads) != len(spec["roads"]):
    errors.append(f"road count {len(roads)} != {len(spec['roads'])}")
cells = [o for o in bpy.data.objects if o.get("streaming_cell")]
if len(cells) != 64:
    errors.append(f"streaming cells {len(cells)} != 64")
ground = bpy.data.objects.get("World_Ground_8km")
if not ground or [round(v) for v in ground.dimensions[:2]] != [8000, 8000]:
    errors.append("ground is not 8x8 km")
if scene.unit_settings.system != "METRIC" or abs(scene.unit_settings.scale_length - 1.0) > 1e-6:
    errors.append("scene units are not metric 1:1")

renders = []
SHOTS = [
    ("01_top_8km", "CAM_Masterplan_Top", (2048, 2048), False),
    ("02_oblique_city", "CAM_Masterplan_Oblique", (2400, 1350), False, "no-labels"),
    ("03_cidade_antiga", "CAM_District_old", (2400, 1350), False),
    ("04_expansao", "CAM_District_expansion", (2400, 1350), False),
    ("05_industrial", "CAM_District_industrial", (2400, 1350), False),
    ("06_corporate", "CAM_District_corporate", (2400, 1350), False),
    ("07_technology", "CAM_District_technology", (2400, 1350), False),
    ("08_santa_aurora_central", "CAM_District_civic", (2400, 1350), False),
    ("09_skyline", "CAM_Skyline", (2400, 1350), False, "no-labels"),
    ("10_streaming_grid", "CAM_Masterplan_Top", (2048, 2048), True),
    ("11_district_highlight", "CAM_Masterplan_Top", (2048, 2048), False, "highlight"),
]
# Review-only saturated district colours (render pass only; the file is never saved).
HIGHLIGHT = {"old": (.85, .35, .10), "expansion": (.30, .70, .20), "civic": (.90, .80, .15),
             "corporate": (.20, .40, .90), "industrial": (.55, .45, .40), "technology": (.10, .75, .80)}
if not opts.no_render:
    subgrid = bpy.data.collections["09_Streaming_Subgrid"]
    guides = bpy.data.collections["06_Streaming_Guides"]
    labels = bpy.data.collections["05_Labels"]
    massing = [bpy.data.collections[n] for n in ("07_Skyline_Shells", "10_Block_Fabric")]
    for name, cam, (w, h), grid, *flags in SHOTS:
        labels.hide_render = "no-labels" in flags
        highlight = "highlight" in flags
        for c in massing:
            c.hide_render = highlight
        for did, col in HIGHLIGHT.items():
            mat = bpy.data.materials.get("MP_District_" + did)
            if mat:
                if "orig_color" not in mat:
                    mat["orig_color"] = list(mat.diffuse_color)
                mat.diffuse_color = (*col, 1.0) if highlight else tuple(mat["orig_color"])
        if cam not in bpy.data.objects:
            errors.append("missing camera " + cam)
            continue
        scene.camera = bpy.data.objects[cam]
        scene.render.resolution_x, scene.render.resolution_y = w, h
        scene.render.resolution_percentage = 100
        subgrid.hide_render = not grid
        guides.hide_render = not grid
        scene.render.image_settings.file_format = "JPEG"
        scene.render.image_settings.quality = 90
        out = review_dir / f"{name}.jpg"
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        renders.append(out.relative_to(root).as_posix())
    # Never save: the review pass must not modify the generated file.

report = {
    "blend": blend_path.relative_to(root).as_posix() if blend_path.is_relative_to(root) else str(blend_path),
    "blenderVersion": bpy.app.version_string,
    "reopenedInFreshProcess": True,
    "objectCount": len(bpy.data.objects),
    "meshCount": len(bpy.data.meshes),
    "collectionObjectCounts": {c.name: len(c.all_objects) for c in scene.collection.children},
    "campaignObjects": sum(1 for l in spec["campaignLocations"] if "LOC_" + l["id"] in bpy.data.objects),
    "lifeObjects": sum(1 for l in spec["lifeLocations"] if "LIFE_" + l["id"] in bpy.data.objects),
    "facilityIdsTagged": len(by_facility),
    "roads": len(roads),
    "streamingCells": len(cells),
    "units": scene.unit_settings.system,
    "missingData": missing,
    "renders": renders,
    "errors": errors,
    "passed": not errors,
}
(review_dir / "w1_reopen_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("W1 REOPEN REPORT", json.dumps({k: report[k] for k in ("objectCount", "passed", "errors")}))
