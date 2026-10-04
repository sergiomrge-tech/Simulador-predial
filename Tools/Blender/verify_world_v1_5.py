"""Reopen a W1.5 .blend in a fresh Blender process, audit it and render the W1.5 review captures.

Run (Blender opens the file itself, proving it reopens):
blender -b --factory-startup <file.blend> --python Tools/Blender/verify_world_v1_5.py -- --root ROOT --mode masterplan|oldtown|kit [--no-render]

Writes ArtSource/Blender/World/Reviews/W1_5/<NN_name>.jpg and reopen_<mode>.json. Never saves the .blend.
"""
import argparse
import json
import sys
from pathlib import Path

import bpy

parser = argparse.ArgumentParser()
parser.add_argument("--root", required=True)
parser.add_argument("--mode", required=True, choices=["masterplan", "oldtown", "kit"])
parser.add_argument("--no-render", action="store_true")
parser.add_argument("--review", default="W1_5", help="Reviews/<dir> for captures and the reopen report (W2 re-renders go to W2)")
parser.add_argument("--only", default="", help="comma-separated capture-name prefixes to render (default: all)")
opts = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
root = Path(opts.root).resolve()
review = root / "ArtSource" / "Blender" / "World" / "Reviews" / opts.review
review.mkdir(parents=True, exist_ok=True)
spec = json.loads((root / "ArtSource" / "Blender" / "World" / "masterplan_spec_v1.json").read_text(encoding="utf-8"))
heroes = json.loads((root / "ArtSource" / "Blender" / "World" / "OldTown" / "oldtown_heroes_v1.json").read_text(encoding="utf-8"))
scene = bpy.context.scene
errors, checks = [], {}

# ---------------------------------------------------------------- generic audit
missing = []
for lib in bpy.data.libraries:
    if not Path(bpy.path.abspath(lib.filepath)).exists():
        missing.append("library:" + lib.filepath)
for img in bpy.data.images:
    if img.source == "FILE" and not img.packed_file and img.filepath and not Path(bpy.path.abspath(img.filepath)).exists():
        missing.append("image:" + img.filepath)
for font in bpy.data.fonts:
    if font.filepath != "<builtin>" and not font.packed_file and not Path(bpy.path.abspath(font.filepath)).exists():
        missing.append("font:" + font.filepath)
if missing:
    errors.append("missing data: " + ", ".join(missing))
if scene.unit_settings.system != "METRIC" or abs(scene.unit_settings.scale_length - 1.0) > 1e-6:
    errors.append("scene units are not metric 1:1")
# Geometry Nodes instancers must point at a non-empty library collection.
gn = 0
for o in bpy.data.objects:
    for m in o.modifiers:
        if m.type == "NODES":
            gn += 1
            ng = m.node_group
            col = next((n for n in ng.nodes if n.bl_idname == "GeometryNodeCollectionInfo"), None) if ng else None
            c = col.inputs["Collection"].default_value if col else None
            if not c or len(c.objects) == 0:
                errors.append(f"instancer without library: {o.name}")
checks["geometryNodesInstancers"] = gn
checks["materials"] = len(bpy.data.materials)
checks["materialsWithTextureSlots"] = sum(1 for m in bpy.data.materials if m.node_tree and any(n.name.startswith("SLOT_") for n in m.node_tree.nodes))

if opts.mode == "masterplan":
    for loc in spec["campaignLocations"]:
        if "LOC_" + loc["id"] not in bpy.data.objects:
            errors.append("missing campaign object LOC_" + loc["id"])
        else:
            o = bpy.data.objects["LOC_" + loc["id"]]
            dims = [round(v, 1) for v in o.dimensions[:2]]
            if abs(dims[0] - loc["width"]) > .2 or abs(dims[1] - loc["depth"]) > .2:
                errors.append(f"footprint mismatch {loc['id']}: {dims}")
    for loc in spec["lifeLocations"]:
        if "LIFE_" + loc["id"] not in bpy.data.objects:
            errors.append("missing life object LIFE_" + loc["id"])
    cells = [o for o in bpy.data.objects if o.get("streaming_cell")]
    terr = [o for o in bpy.data.objects if o.name.startswith("Terrain_SA_M")]
    roads = [o for o in bpy.data.objects if o.get("road_id")]
    if len(cells) != 64 or len(terr) != 64:
        errors.append(f"streaming cells {len(cells)} / terrain cells {len(terr)} != 64")
    if len({r["road_id"] for r in roads}) < len(spec["roads"]):
        errors.append("road markers missing")
    wb = bpy.data.objects.get("World_Bounds_8km")
    if not wb or [round(v) for v in wb.scale[:2]] != [4000, 4000]:
        errors.append("world bounds is not 8x8 km")
    checks.update({"campaignObjects": sum(1 for l in spec["campaignLocations"] if "LOC_" + l["id"] in bpy.data.objects),
                   "lifeObjects": sum(1 for l in spec["lifeLocations"] if "LIFE_" + l["id"] in bpy.data.objects),
                   "streamingCells": len(cells), "terrainCells": len(terr), "roadMarkers": len(roads)})
elif opts.mode == "oldtown":
    for L in ("Terrain", "Roads", "Architecture", "Infrastructure", "Props", "Vegetation", "Lighting", "Gameplay"):
        if "OT_" + L not in bpy.data.collections:
            errors.append("missing layer collection OT_" + L)
    for h in heroes["heroes"]:
        hid = h["id"]
        if "HERO_" + hid not in bpy.data.collections:
            errors.append("missing hero collection " + hid)
        objs = [o for o in bpy.data.objects if o.get("facility_id") == hid]
        if not any("__F00" in o.name for o in objs) or not any(o.name.endswith("ROOF") for o in objs):
            errors.append(f"hero {hid} lacks floors/roof")
    slots = [o for o in bpy.data.objects if o.get("sa_kind") == "state_slot"]
    states = sorted({o["state"] for o in slots})
    for s in ("H0", "H1", "H2", "H3", "H4", "G0", "G1", "G2", "G3", "G4"):
        if s not in states:
            errors.append("missing state slots " + s)
    subcell_objs = [o for o in bpy.data.objects if o.get("sa_subcell")]
    fam = bpy.data.collections.get("OT_Lib_Families")
    if not fam or len(fam.objects) < 40:
        errors.append("family library incomplete")
    checks.update({"heroes": len(heroes["heroes"]), "stateSlots": len(slots), "states": states, "subcellObjects": len(subcell_objs),
                   "subcells": len({o["sa_subcell"] for o in subcell_objs}), "familyVariants": len(fam.objects) if fam else 0,
                   "gameplayMarkers": sum(1 for o in bpy.data.objects if o.get("sa_layer") == "Gameplay")})
else:
    kit = [o for o in bpy.data.objects if o.name.startswith("KIT_") and o.type == "MESH" and o.name != "KIT_Ground"]
    prps = [o for o in bpy.data.objects if o.name.startswith("PROP_")]
    marked = sum(1 for o in bpy.data.objects if o.asset_data)
    if len(kit) < 35 or len(prps) < 12:
        errors.append("kit incomplete")
    checks.update({"kitPieces": len(kit), "props": len(prps), "assetsMarked": marked})

# ---------------------------------------------------------------- captures
SHOTS = {
    "masterplan": [
        ("01_mundo_inteiro", "CAM_World_Top", (2048, 2048), {"labels": True}),
        ("02_mundo_obliquo", "CAM_World_Oblique", (2400, 1350), {}),
        ("09_industrial", "CAM_District_industrial", (2400, 1350), {"labels": True}),
        ("09b_industrial_baixo", "CAM_Industrial_Low", (2400, 1350), {}),
        ("10_empresarial", "CAM_District_corporate", (2400, 1350), {"labels": True}),
        ("11_tecnologico", "CAM_District_technology", (2400, 1350), {"labels": True}),
        ("12_central", "CAM_District_civic", (2400, 1350), {"labels": True}),
        ("13_skyline", "CAM_Skyline", (2400, 1350), {}),
        ("14_transicao_antiga_expansao", "CAM_Transition_OldExp", (2400, 1350), {}),
        ("15_grid_streaming", "CAM_World_Top", (2048, 2048), {"labels": True, "grid": True}),
        ("16_relevo_drenagem", "CAM_World_Top", (2048, 2048), {"relief": True}),
        ("17_cidade_antiga_masterplan", "CAM_District_old", (2400, 1350), {"labels": True}),
        ("18_expansao", "CAM_District_expansion", (2400, 1350), {"labels": True}),
    ],
    "oldtown": [
        ("03_cidade_antiga", "CAM_OT_Top", (2048, 2048), {}),
        ("04_cidade_antiga_obliqua", "CAM_OT_Oblique", (2400, 1350), {}),
        ("05_lar_inicial", "CAM_OT_Home_Exterior", (2400, 1350), {}),
        ("05b_lar_inicial_corte", "CAM_OT_Home_Cutaway", (1800, 1800), {"cut": ("home.starter", 1)}),
        ("06_oficina_aurora", "CAM_OT_Garage_Exterior", (2400, 1350), {}),
        ("06b_oficina_aurora_corte", "CAM_OT_Garage_Cutaway", (1800, 1800), {"cut": ("garage", 0)}),
        ("07_horizonte", "CAM_OT_Horizonte", (2400, 1350), {}),
        ("07b_horizonte_fachada", "CAM_OT_Horizonte_Frente", (2400, 1350), {}),
        ("08_teatro_imperial", "CAM_OT_Imperial", (2400, 1350), {}),
    ],
    "kit": [
        ("20_kit_modular", "CAM_Kit_Modular", (2400, 1350), {}),
        ("21_kit_infraestrutura", "CAM_Kit_Infra", (2400, 1350), {}),
        ("22_familias_edificacao", "CAM_Kit_Families", (2400, 1350), {}),
        ("23_materiais_pbr", "CAM_Kit_Materials", (2400, 1350), {}),
    ],
}
# Complexity estimate (W2): triangles of plain meshes + instanced triangles (library mesh tris x points per variant).
def _tris(me):
    return sum(len(p.vertices) - 2 for p in me.polygons)


cx = {"meshTris": 0, "instancedTris": 0, "instances": 0, "largestMesh": ["", 0]}
for o in bpy.data.objects:
    if o.type != "MESH" or any(c.hide_render for c in o.users_collection if c.name.startswith(("OT_Lib", "OT_Library"))):
        continue
    gnm = next((m for m in o.modifiers if m.type == "NODES"), None)
    if gnm is None:
        t = _tris(o.data)
        if any(c.name in ("OT_Library",) or c.name.startswith("OT_Lib") for c in o.users_collection):
            continue
        cx["meshTris"] += t
        if t > cx["largestMesh"][1]:
            cx["largestMesh"] = [o.name, t]
        continue
    col = next((n for n in gnm.node_group.nodes if n.bl_idname == "GeometryNodeCollectionInfo"), None)
    c = col.inputs["Collection"].default_value if col else None
    if not c or "variant" not in o.data.attributes:
        continue
    lib_t = [_tris(x.data) if x.type == "MESH" else 0 for x in sorted(c.objects, key=lambda x: x.name)]
    for a in o.data.attributes["variant"].data:
        if 0 <= a.value < len(lib_t):
            cx["instancedTris"] += lib_t[a.value]
            cx["instances"] += 1
checks["complexity"] = cx

renders = []
if not opts.no_render:
    scene.render.image_settings.file_format = "JPEG"
    scene.render.image_settings.quality = 88
    saved_hide = {o.name: o.hide_render for o in bpy.data.objects}
    only = [x for x in opts.only.split(",") if x]
    for name, cam, (w, h), fl in SHOTS[opts.mode]:
        if only and not any(name.startswith(x) for x in only):
            continue
        if cam not in bpy.data.objects:
            errors.append("missing camera " + cam)
            continue
        for o in bpy.data.objects:
            o.hide_render = saved_hide.get(o.name, False)   # keep authored state (e.g. W1.5 hero LOD1 hidden behind W2 LOD0)
        for cname in ("08_Labels",):
            if cname in bpy.data.collections:
                bpy.data.collections[cname].hide_render = not fl.get("labels", False)
        if "11_Streaming_Subgrid" in bpy.data.collections:
            bpy.data.collections["11_Streaming_Subgrid"].hide_render = not fl.get("grid", False)
        for cname in ("04_Fabric", "07_Vegetation", "05_Campaign_Locations", "06_Life_Economy_Locations"):
            if cname in bpy.data.collections:
                bpy.data.collections[cname].hide_render = fl.get("relief", False)
        if "cut" in fl:
            hid, max_floor = fl["cut"]
            for o in bpy.data.objects:
                if o.name.startswith(f"HERO_{hid}__"):
                    n = o.name
                    if n.endswith("ROOF") or n.endswith("details") or ("__F" in n and int(n.split("__F")[-1][:2]) > max_floor):
                        o.hide_render = True
        scene.camera = bpy.data.objects[cam]
        scene.render.resolution_x, scene.render.resolution_y = w, h
        scene.render.resolution_percentage = 100
        out = review / (f"{name}.jpg" if opts.review == "W1_5" else f"ot_{name}.jpg")
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        renders.append(out.relative_to(root).as_posix())

report = {"mode": opts.mode, "blend": Path(bpy.data.filepath).relative_to(root).as_posix(), "blenderVersion": bpy.app.version_string,
          "reopenedInFreshProcess": True, "objectCount": len(bpy.data.objects), "meshCount": len(bpy.data.meshes),
          "collections": {c.name: len(c.all_objects) for c in scene.collection.children}, "checks": checks, "missingData": missing,
          "renders": renders, "errors": errors, "passed": not errors}
(review / f"reopen_{opts.mode}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("W1.5 REOPEN", opts.mode, json.dumps({k: report[k] for k in ("objectCount", "passed", "errors")}))
