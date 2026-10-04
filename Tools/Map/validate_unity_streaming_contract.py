#!/usr/bin/env python3
"""Validate the Blender -> Unity streaming contract for Santa Aurora.

This is intentionally dependency-free and read-only. It validates the large
one-line manifest locally, where GitHub UI/connectors may not expose its content.

Usage:
    python Tools/Map/validate_unity_streaming_contract.py
    python Tools/Map/validate_unity_streaming_contract.py --root C:/path/to/Simulador-predial
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CELL_RE = re.compile(r"^SA_M(\d{2})_(\d{2})_S(\d{2})_(\d{2})$")
LAYERS = {
    "Terrain",
    "Roads",
    "Architecture",
    "Infrastructure",
    "Props",
    "Vegetation",
    "Lighting",
    "Gameplay",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    return parser.parse_args()


def fail(errors: list[str], summary: dict) -> int:
    summary["status"] = "FAIL"
    summary["errors"] = errors
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1


def main() -> int:
    args = parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parents[2]
    world = root / "ArtSource" / "Blender" / "World" / "OldTown"
    manifest_path = world / "oldtown_streaming_manifest_v1.json"
    heroes_path = world / "oldtown_heroes_v1.json"
    report_path = world / "oldtown_generation_report.json"

    errors: list[str] = []
    for path in (manifest_path, heroes_path, report_path):
        if not path.is_file():
            errors.append(f"missing file: {path}")

    summary = {
        "root": str(root),
        "manifest": str(manifest_path.relative_to(root)) if manifest_path.exists() else str(manifest_path),
    }
    if errors:
        return fail(errors, summary)

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        heroes_doc = json.loads(heroes_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail([f"json parse failed: {exc}"], summary)

    required = {"schemaVersion", "families", "props", "subcells", "heroes", "lots"}
    missing = sorted(required.difference(manifest))
    if missing:
        errors.append("manifest missing keys: " + ", ".join(missing))

    if manifest.get("schemaVersion") != 1:
        errors.append(f"schemaVersion={manifest.get('schemaVersion')!r}, expected 1")

    subcells = manifest.get("subcells") or {}
    lots = manifest.get("lots") or []
    manifest_heroes = manifest.get("heroes") or {}
    families = manifest.get("families") or {}

    bad_cell_names: list[str] = []
    bad_cell_ranges: list[str] = []
    bad_layers: list[str] = []
    for cell_id, layers in subcells.items():
        match = CELL_RE.fullmatch(cell_id)
        if not match:
            bad_cell_names.append(cell_id)
            continue
        mx, mz, sx, sz = map(int, match.groups())
        if not (0 <= mx < 8 and 0 <= mz < 8 and 0 <= sx < 4 and 0 <= sz < 4):
            bad_cell_ranges.append(cell_id)
        if not isinstance(layers, dict):
            errors.append(f"subcell {cell_id} is not an object")
            continue
        unknown = sorted(set(layers).difference(LAYERS))
        if unknown:
            bad_layers.append(f"{cell_id}: {unknown}")

    if bad_cell_names:
        errors.append("invalid subcell names: " + ", ".join(bad_cell_names[:20]))
    if bad_cell_ranges:
        errors.append("out-of-range subcells: " + ", ".join(bad_cell_ranges[:20]))
    if bad_layers:
        errors.append("unknown layer names: " + "; ".join(bad_layers[:20]))

    lot_ids: set[str] = set()
    duplicate_lots: list[str] = []
    referenced_cells: set[str] = set()
    missing_variants: set[str] = set()

    for lot in lots:
        lot_id = lot.get("id")
        if not isinstance(lot_id, str) or not lot_id:
            errors.append("lot without stable id")
            continue
        if lot_id in lot_ids:
            duplicate_lots.append(lot_id)
        lot_ids.add(lot_id)

        subcell = lot.get("subcell")
        if isinstance(subcell, str):
            referenced_cells.add(subcell)
        else:
            errors.append(f"lot {lot_id} without subcell")

        variant = lot.get("variant")
        if variant not in families:
            missing_variants.add(str(variant))

    if duplicate_lots:
        errors.append("duplicate lot ids: " + ", ".join(sorted(set(duplicate_lots))[:20]))
    if missing_variants:
        errors.append("lot variants missing from families: " + ", ".join(sorted(missing_variants)[:20]))

    expected_hero_ids = [h["id"] for h in heroes_doc.get("heroes", []) if isinstance(h, dict) and h.get("id")]
    if len(expected_hero_ids) != 9:
        errors.append(f"hero registry has {len(expected_hero_ids)} heroes, expected 9")

    if set(expected_hero_ids) != set(manifest_heroes):
        missing_h = sorted(set(expected_hero_ids).difference(manifest_heroes))
        extra_h = sorted(set(manifest_heroes).difference(expected_hero_ids))
        if missing_h:
            errors.append("heroes missing from manifest: " + ", ".join(missing_h))
        if extra_h:
            errors.append("unexpected heroes in manifest: " + ", ".join(extra_h))

    for hero_id, hero in manifest_heroes.items():
        subcell = hero.get("subcell") if isinstance(hero, dict) else None
        if isinstance(subcell, str):
            referenced_cells.add(subcell)
        else:
            errors.append(f"hero {hero_id} without subcell")

    missing_cells = sorted(referenced_cells.difference(subcells))
    if missing_cells:
        errors.append("referenced subcells missing from subcells map: " + ", ".join(missing_cells[:20]))

    report_lots = report.get("buildingInstances")
    if isinstance(report_lots, int) and report_lots != len(lots):
        errors.append(f"lot count mismatch: manifest={len(lots)} report={report_lots}")

    report_cells = report.get("subcells")
    if isinstance(report_cells, int) and report_cells != len(subcells):
        errors.append(f"subcell count mismatch: manifest={len(subcells)} report={report_cells}")

    summary.update(
        {
            "schemaVersion": manifest.get("schemaVersion"),
            "subcells": len(subcells),
            "lots": len(lots),
            "heroes": len(manifest_heroes),
            "families": len(families),
            "referencedSubcells": len(referenced_cells),
        }
    )

    if errors:
        return fail(errors, summary)

    summary["status"] = "PASS"
    summary["errors"] = []
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
