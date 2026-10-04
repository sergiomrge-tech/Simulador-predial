"""Read-only preflight for one Santa Aurora streaming cell before Unity export.

Run with the Cidade Antiga base already opened:

blender -b ArtSource/Blender/World/OldTown/SantaAurora_CidadeAntiga_Base_v1.blend \
  --python Tools/Blender/preflight_unity_cell_export.py -- \
  --root . --cell SA_M01_01_S00_02

The script never saves the .blend and never edits source objects.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import bpy

CELL_RE = re.compile(r"^SA_M(\d{2})_(\d{2})_S(\d{2})_(\d{2})$")
LAYERS = (
    "Terrain",
    "Roads",
    "Architecture",
    "Infrastructure",
    "Props",
    "Vegetation",
    "Lighting",
    "Gameplay",
)


def args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--cell", required=True)
    p.add_argument("--output", default="")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return p.parse_args(argv)


def tris(mesh) -> int:
    return sum(max(0, len(poly.vertices) - 2) for poly in mesh.polygons)


def main() -> int:
    opt = args()
    root = Path(opt.root).resolve()
    match = CELL_RE.fullmatch(opt.cell)
    errors: list[str] = []
    warnings: list[str] = []

    if not match:
        errors.append(f"invalid cell id: {opt.cell}")
    else:
        mx, mz, sx, sz = map(int, match.groups())
        if not (0 <= mx < 8 and 0 <= mz < 8 and 0 <= sx < 4 and 0 <= sz < 4):
            errors.append(f"cell outside 8x8 km grid: {opt.cell}")

    manifest_path = root / "ArtSource" / "Blender" / "World" / "OldTown" / "oldtown_streaming_manifest_v1.json"
    if not manifest_path.is_file():
        errors.append("missing streaming manifest")
        manifest = {}
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expected_layers = (manifest.get("subcells") or {}).get(opt.cell)
    if expected_layers is None:
        errors.append("cell not present in streaming manifest")
        expected_layers = {}

    scene_objects = [o for o in bpy.data.objects if o.get("sa_subcell") == opt.cell]
    by_layer: dict[str, list] = defaultdict(list)
    for obj in scene_objects:
        by_layer[str(obj.get("sa_layer", "UNSPECIFIED"))].append(obj)

    manifest_names = set()
    for layer, names in expected_layers.items():
        if isinstance(names, list):
            manifest_names.update(names)

    actual_names = {o.name for o in scene_objects}
    missing_objects = sorted(manifest_names.difference(actual_names))
    if missing_objects:
        errors.append(f"{len(missing_objects)} manifest objects missing from opened blend")

    unexpected = sorted(actual_names.difference(manifest_names))
    if unexpected:
        warnings.append(f"{len(unexpected)} cell-tagged objects are not listed in manifest")

    layer_report = {}
    object_types = Counter()
    modifiers = Counter()
    total_mesh_tris = 0
    largest_mesh = ("", 0)
    collection_instances = []
    geometry_nodes = []
    gameplay_markers = []
    facility_ids = set()

    for layer, objects in sorted(by_layer.items()):
        layer_types = Counter(o.type for o in objects)
        layer_tris = 0
        for o in objects:
            object_types[o.type] += 1
            fid = o.get("facility_id")
            if fid:
                facility_ids.add(str(fid))

            if o.type == "MESH":
                t = tris(o.data)
                layer_tris += t
                total_mesh_tris += t
                if t > largest_mesh[1]:
                    largest_mesh = (o.name, t)

            for mod in o.modifiers:
                modifiers[mod.type] += 1
                if mod.type == "NODES":
                    geometry_nodes.append(o.name)

            if o.instance_type == "COLLECTION" and o.instance_collection is not None:
                collection_instances.append(
                    {
                        "object": o.name,
                        "collection": o.instance_collection.name,
                        "facility_id": fid,
                    }
                )

            if layer == "Gameplay" or o.name.startswith(("GP_", "SLOT_", "PROXY_")):
                gameplay_markers.append(
                    {
                        "name": o.name,
                        "type": o.type,
                        "facility_id": fid,
                        "kind": o.get("sa_kind"),
                    }
                )

        layer_report[layer] = {
            "objects": len(objects),
            "types": dict(sorted(layer_types.items())),
            "meshTris": layer_tris,
            "manifestObjects": len(expected_layers.get(layer, [])) if isinstance(expected_layers, dict) else 0,
        }

    for layer in LAYERS:
        layer_report.setdefault(
            layer,
            {
                "objects": 0,
                "types": {},
                "meshTris": 0,
                "manifestObjects": len(expected_layers.get(layer, [])) if isinstance(expected_layers, dict) else 0,
            },
        )

    if geometry_nodes:
        warnings.append(
            "Geometry Nodes present: export must evaluate/realize geometry in a staging copy, never destructively in source"
        )
    if collection_instances:
        warnings.append(
            "Linked collection instances present: hero assets should remain separate prefab sources instead of being blindly baked into static cell FBX"
        )

    report = {
        "schemaVersion": 1,
        "status": "FAIL" if errors else "PASS",
        "blend": bpy.data.filepath,
        "blenderVersion": bpy.app.version_string,
        "cell": opt.cell,
        "sourceManifest": manifest_path.relative_to(root).as_posix() if manifest_path.exists() else str(manifest_path),
        "objects": len(scene_objects),
        "objectTypes": dict(sorted(object_types.items())),
        "modifiers": dict(sorted(modifiers.items())),
        "layers": layer_report,
        "meshTris": total_mesh_tris,
        "largestMesh": {"name": largest_mesh[0], "tris": largest_mesh[1]},
        "geometryNodesObjects": sorted(geometry_nodes),
        "collectionInstances": collection_instances,
        "gameplayMarkers": gameplay_markers,
        "facilityIds": sorted(facility_ids),
        "missingManifestObjects": missing_objects[:100],
        "unexpectedCellObjects": unexpected[:100],
        "errors": errors,
        "warnings": warnings,
        "exportPolicy": {
            "staticMeshLayers": [
                "Terrain",
                "Roads",
                "Architecture",
                "Infrastructure",
                "Props",
                "Vegetation",
            ],
            "separateDataLayers": ["Gameplay", "Lighting"],
            "linkedHeroesSeparatePrefab": True,
            "sourceBlendMustRemainUnmodified": True,
        },
    }

    out = (
        Path(opt.output).resolve()
        if opt.output
        else root
        / "ArtSource"
        / "Blender"
        / "World"
        / "UnityExport"
        / f"preflight_{opt.cell}.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "cell": opt.cell, "report": str(out)}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
