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


def export_layer(layer: str, objects, out_dir: Path):
    exportable, linked, unsupported = selected_exportable(objects)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in exportable:
        try:
            obj.hide_set(False)
        except RuntimeError:
            pass
        obj.select_set(True)

    output = out_dir / f"{layer}.fbx"
    status = "SKIPPED"
    error = None

    if exportable:
        try:
            bpy.ops.export_scene.fbx(
                filepath=str(output),
                use_selection=True,
                object_types={"MESH", "CURVE", "SURFACE", "FONT", "META", "EMPTY"},
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

    for layer in STATIC_LAYERS:
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
        if result["status"] == "FAIL":
            failure = True

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
