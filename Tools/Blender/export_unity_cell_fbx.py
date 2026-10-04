"""Export one Santa Aurora 250 m cell to FBX layer files for Unity staging.

This script is intentionally non-destructive:
- it never saves the source .blend;
- it exports only objects tagged with the requested sa_subcell;
- linked hero collection instances are reported, not baked into the static cell;
- Gameplay and Lighting are exported separately by their dedicated pipelines.

Example:
blender -b ArtSource/Blender/World/OldTown/SantaAurora_CidadeAntiga_Base_v1.blend \
  --python Tools/Blender/export_unity_cell_fbx.py -- \
  --root . --cell SA_M01_01_S00_02

Output:
ArtSource/Blender/World/UnityExport/Cells/<cell>/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from unity_export_staging import stage_meshes, bounds, cleanup

CELL_RE = re.compile(r"^SA_M(\d{2})_(\d{2})_S(\d{2})_(\d{2})$")
STATIC_LAYERS = (
    "Terrain",
    "Roads",
    "Architecture",
    "Infrastructure",
    "Props",
    "Vegetation",
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--output", default="")
    p.add_argument("--layers", default="", help="comma-separated subset of layers to (re)export; the cell manifest keeps the other entries")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return p.parse_args(argv)


def validate_cell(cell: str) -> None:
    m = CELL_RE.fullmatch(cell)
    if not m:
        raise SystemExit(f"invalid cell id: {cell}")
    mx, mz, sx, sz = map(int, m.groups())
    if not (0 <= mx < 8 and 0 <= mz < 8 and 0 <= sx < 4 and 0 <= sz < 4):
        raise SystemExit(f"cell outside Santa Aurora grid: {cell}")


def selected_exportable(objects):
    exportable = []
    linked = []
    unsupported = []

    for obj in objects:
        if obj.instance_type == "COLLECTION" and obj.instance_collection is not None:
            linked.append(
                {
                    "object": obj.name,
                    "collection": obj.instance_collection.name,
                    "facilityId": obj.get("facility_id"),
                    "source": obj.get("source"),
                }
            )
            continue

        if obj.type in {"MESH", "CURVE", "SURFACE", "FONT", "META", "EMPTY"}:
            exportable.append(obj)
        else:
            unsupported.append({"name": obj.name, "type": obj.type})

    return exportable, linked, unsupported


VEHICLE_FAMILIES = ("hatch_antigo", "hatch", "sedan", "picape", "suv", "van")


def vehicle_family(obj):
    src = str(obj.get("vehicle", ""))
    for fam in VEHICLE_FAMILIES:
        if src.startswith("VEH_" + fam + "_"):
            return fam
    return None


def export_vehicle_lods(vehicles, output: Path):
    """W3.2 parked cars as LOD groups: one empty per car at its world transform with children _LOD0 (14k tris), _LOD1 and _LOD2 (proxy) that share
    the library meshes, so Unity builds a LODGroup per car and a single mesh per variant instead of 889 unique copies. The Blender slice swaps far cars to
    LOD1 for its own render budget; Unity decides by distance, so every car is exported with its LOD0 mesh regardless of that swap."""
    created = []
    library = {}                                                         # (kind, variant) -> library mesh; Blender may have suffixed names (.002)
    for me in bpy.data.meshes:
        if me.library is not None or not me.name.startswith("VEH_"):
            continue
        key = re.sub(r"\.\d+$", "", me.name)
        kind = "L1" if key.endswith("_LOD1") else "P" if key.endswith("_PROXY") else "L0"
        library[(kind, key[:-5] if kind == "L1" else key)] = me
    try:
        for o in vehicles:
            key = re.sub(r"\.\d+$", "", o.data.name)
            key = key[:-5] if key.endswith("_LOD1") else key
            lod0, lod1 = library.get(("L0", key)), library.get(("L1", key))
            family = vehicle_family(o)
            proxy = library.get(("P", f"VEH_{family}_PROXY")) if family else None
            if lod0 is None:
                raise RuntimeError(f"vehicle {o.name}: LOD0 mesh for '{key}' not found")
            holder = bpy.data.objects.new("EXPORT_" + o.name, None)
            bpy.context.scene.collection.objects.link(holder)
            holder.matrix_world = o.matrix_world.copy()
            created.append(holder)
            for suffix, mesh in ((0, lod0), (1, lod1), (2, proxy)):
                if mesh is None:
                    continue
                child = bpy.data.objects.new(f"EXPORT_{o.name}_LOD{suffix}", mesh)
                bpy.context.scene.collection.objects.link(child)
                child.parent = holder
                created.append(child)
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        for obj in created:
            obj.select_set(True)
        bpy.ops.export_scene.fbx(
            filepath=str(output),
            use_selection=True,
            object_types={"MESH", "EMPTY"},
            use_mesh_modifiers=False,
            use_custom_props=False,
            add_leaf_bones=False,
            bake_anim=False,
            apply_unit_scale=True,
            apply_scale_options="FBX_SCALE_UNITS",
            axis_forward="-Z",
            axis_up="Y",
            path_mode="AUTO",
            embed_textures=False,
        )
    finally:
        for obj in created:
            bpy.data.objects.remove(obj, do_unlink=True)
    return len(vehicles)


def export_layer(layer: str, objects, out_dir: Path):
    exportable, linked, unsupported = selected_exportable(objects)

    # W1 hero volumes overlap the linked W2 hero and would obstruct its doors.
    # The authored hero is exported independently, including its gameplay data.
    exportable = [o for o in exportable if not o.get('facility_id')
                  and not o.name.startswith(('HERO_', 'GP_', 'SLOT_', 'PROXY_'))]

    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable:
        try:
            obj.hide_set(False)
        except RuntimeError:
            pass
        obj.select_set(True)

    vehicles = []
    if layer == "Props":
        vehicles = [o for o in exportable if o.get("sa_kind") == "vehicle"]
        exportable = [o for o in exportable if o.get("sa_kind") != "vehicle"]
    lod_file, lod_bytes, lod_error = None, 0, None
    if vehicles:
        lod_path = out_dir / "Props_Vehicles.fbx"
        try:
            export_vehicle_lods(vehicles, lod_path)
            lod_file, lod_bytes = lod_path.name, lod_path.stat().st_size
        except Exception as exc:
            lod_error = repr(exc)

    output = out_dir / f"{layer}.fbx"
    status = "SKIPPED"
    error = None

    if exportable:
        staged, groups = [], []
        try:
            staged, groups = stage_meshes(exportable)
            bpy.ops.object.select_all(action="DESELECT")
            for obj in staged:
                obj.select_set(True)
            source_bounds = bounds(staged)
            bpy.ops.export_scene.fbx(
                filepath=str(output),
                use_selection=True,
                object_types={"MESH"},
                use_mesh_modifiers=True,
                use_mesh_modifiers_render=True,
                use_custom_props=True,
                add_leaf_bones=False,
                bake_anim=False,
                apply_unit_scale=True,
                apply_scale_options="FBX_SCALE_UNITS",
                axis_forward="-Z",
                axis_up="Y",
                path_mode="AUTO",
                embed_textures=False,
            )
            status = "EXPORTED"
        except Exception as exc:
            status = "FAIL"
            error = repr(exc)
        finally:
            cleanup(staged, groups)

    return {
        "layer": layer,
        "status": status,
        "file": output.name if status == "EXPORTED" else None,
        "fileBytes": output.stat().st_size if output.exists() else 0,
        "sourceObjects": len(objects),
        "exportedObjects": len(exportable),
        "linkedInstancesExcluded": linked,
        "unsupportedExcluded": unsupported,
        "error": error,
        "blenderBounds": source_bounds if status == 'EXPORTED' else None,
        "lodFile": lod_file,
        "lodFileBytes": lod_bytes,
        "lodVehicles": len(vehicles),
        "lodError": lod_error,
    }


def main() -> int:
    opt = parse_args()
    validate_cell(opt.cell)
    root = Path(opt.root).resolve()

    manifest_path = (
        root
        / "ArtSource"
        / "Blender"
        / "World"
        / "OldTown"
        / "oldtown_streaming_manifest_v1.json"
    )
    if not manifest_path.is_file():
        raise SystemExit("missing oldtown_streaming_manifest_v1.json")

    world_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if opt.cell not in (world_manifest.get("subcells") or {}):
        raise SystemExit(f"cell is not present in streaming manifest: {opt.cell}")

    out_dir = (
        Path(opt.output).resolve()
        if opt.output
        else root
        / "ArtSource"
        / "Blender"
        / "World"
        / "UnityExport"
        / "Cells"
        / opt.cell
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    per_layer = []
    all_linked = []
    failure = False

    wanted = [x for x in opt.layers.split(",") if x] or list(STATIC_LAYERS)
    for layer in STATIC_LAYERS:
        if layer not in wanted:
            continue
        objects = [
            obj
            for obj in bpy.data.objects
            if obj.get("sa_subcell") == opt.cell
            and obj.get("sa_layer") == layer
            and obj.library is None
        ]
        result = export_layer(layer, objects, out_dir)
        per_layer.append(result)
        all_linked.extend(result["linkedInstancesExcluded"])
        if result["status"] == "FAIL" or result.get("lodError"):
            failure = True

    manifest_file = out_dir / "cell_export_manifest.json"
    if opt.layers and manifest_file.is_file():                          # partial re-export: keep the entries of the layers that were not touched
        previous = json.loads(manifest_file.read_text(encoding="utf-8"))
        kept = [item for item in previous.get("layers", []) if item["layer"] not in wanted]
        per_layer = kept + per_layer
        per_layer.sort(key=lambda item: STATIC_LAYERS.index(item["layer"]))
    required = {item["layer"]: item for item in per_layer}
    for layer in ("Terrain", "Roads", "Architecture"):
        if required[layer]["status"] != "EXPORTED":
            failure = True
            required[layer]["error"] = required[layer]["error"] or (
                f"required layer {layer} contains no exportable objects"
            )

    report = {
        "schemaVersion": 1,
        "status": "FAIL" if failure else "PASS",
        "cell": opt.cell,
        "sourceBlend": Path(bpy.data.filepath).as_posix(),
        "blenderVersion": bpy.app.version_string,
        "axisContract": {
            "fbxForward": "-Z",
            "fbxUp": "Y",
            "expectedUnity": "X east, Y up, Z north",
            "requiresFirstCellScaleAxisValidation": True,
        },
        "layers": per_layer,
        "linkedHeroInstancesExcluded": all_linked,
        "gameplayExport": "Use Tools/Blender/export_unity_gameplay_markers.py",
        "sourceBlendModified": False,
    }

    report_path = out_dir / "cell_export_manifest.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    bpy.ops.object.select_all(action="DESELECT")
    print(
        json.dumps(
            {
                "status": report["status"],
                "cell": opt.cell,
                "output": str(out_dir),
                "fbxFiles": sum(1 for item in per_layer if item["status"] == "EXPORTED"),
                "linkedHeroesExcluded": len(all_linked),
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
