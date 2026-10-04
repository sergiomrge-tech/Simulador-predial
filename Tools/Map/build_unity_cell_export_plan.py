#!/usr/bin/env python3
"""Build a machine-readable Unity export plan for the approved pilot corridor.

Read-only; does not run Blender or Unity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=None)
    p.add_argument("--output", type=Path, default=None)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parents[2]

    world = root / "ArtSource" / "Blender" / "World" / "OldTown"
    manifest = json.loads((world / "oldtown_streaming_manifest_v1.json").read_text(encoding="utf-8"))
    corridor = json.loads((root / "Docs" / "unity-vertical-slice-corridor-v1.json").read_text(encoding="utf-8"))

    hero_by_cell: dict[str, list[str]] = {}
    for hero_id, hero in manifest.get("heroes", {}).items():
        hero_by_cell.setdefault(hero["subcell"], []).append(hero_id)

    lots_by_cell: dict[str, int] = {}
    for lot in manifest.get("lots", []):
        lots_by_cell[lot["subcell"]] = lots_by_cell.get(lot["subcell"], 0) + 1

    plan_cells = []
    for cell in corridor["cells"]:
        layers = manifest.get("subcells", {}).get(cell)
        if layers is None:
            raise SystemExit(f"corridor cell missing from manifest: {cell}")

        plan_cells.append(
            {
                "cell": cell,
                "unityScene": "SA_Cell_" + cell,
                "heroes": sorted(hero_by_cell.get(cell, [])),
                "lots": lots_by_cell.get(cell, 0),
                "layers": {name: len(items) for name, items in layers.items()},
                "preflightReport": f"ArtSource/Blender/World/UnityExport/preflight_{cell}.json",
                "staticExportLayers": [
                    "Terrain",
                    "Roads",
                    "Architecture",
                    "Infrastructure",
                    "Props",
                    "Vegetation",
                ],
                "separateDataLayers": ["Gameplay", "Lighting"],
            }
        )

    result = {
        "schemaVersion": 1,
        "sourceManifest": "ArtSource/Blender/World/OldTown/oldtown_streaming_manifest_v1.json",
        "sourceCorridor": "Docs/unity-vertical-slice-corridor-v1.json",
        "cells": plan_cells,
        "cellCount": len(plan_cells),
        "rules": {
            "blenderToUnityAxis": "X->X, Y->Z, Z->Y",
            "metersToUnityUnits": 1.0,
            "linkedHeroesSeparatePrefab": True,
            "gameplayMarkersSeparateData": True,
            "doNotModifySourceBlend": True,
        },
    }

    output = (
        args.output.resolve()
        if args.output
        else root / "Docs" / "unity-cell-export-plan-v1.json"
    )
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "cells": len(plan_cells), "output": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
