#!/usr/bin/env python3
"""Select a continuous 250 m cell rectangle around chosen hero locations.

Default corridor: home.starter -> garage -> horizonte -> grocery.
It is intentionally deterministic and does not edit source world data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=None)
    p.add_argument(
        "--heroes",
        nargs="+",
        default=["home.starter", "garage", "horizonte", "grocery"],
    )
    p.add_argument("--padding", type=int, default=0, help="extra 250 m cells around bounding rectangle")
    return p.parse_args()


def global_cell(x: float, z: float) -> tuple[int, int]:
    gx = int((x + 4000.0) // 250.0)
    gz = int((z + 4000.0) // 250.0)
    return max(0, min(31, gx)), max(0, min(31, gz))


def cell_name(gx: int, gz: int) -> str:
    mx, sx = divmod(gx, 4)
    mz, sz = divmod(gz, 4)
    return f"SA_M{mx:02d}_{mz:02d}_S{sx:02d}_{sz:02d}"


def main() -> int:
    args = parse_args()
    root = args.root.resolve() if args.root else Path(__file__).resolve().parents[2]
    heroes_path = root / "ArtSource" / "Blender" / "World" / "OldTown" / "oldtown_heroes_v1.json"
    data = json.loads(heroes_path.read_text(encoding="utf-8"))
    by_id = {h["id"]: h for h in data["heroes"]}

    missing = [h for h in args.heroes if h not in by_id]
    if missing:
        raise SystemExit("unknown hero ids: " + ", ".join(missing))

    anchors = {}
    for hero_id in args.heroes:
        lot = by_id[hero_id]["lot"]
        x = (lot[0] + lot[2]) / 2.0
        z = (lot[1] + lot[3]) / 2.0
        gx, gz = global_cell(x, z)
        anchors[hero_id] = {
            "position": [round(x, 2), round(z, 2)],
            "globalCell": [gx, gz],
            "subcell": cell_name(gx, gz),
        }

    xs = [v["globalCell"][0] for v in anchors.values()]
    zs = [v["globalCell"][1] for v in anchors.values()]
    pad = max(0, args.padding)
    x0, x1 = max(0, min(xs) - pad), min(31, max(xs) + pad)
    z0, z1 = max(0, min(zs) - pad), min(31, max(zs) + pad)

    cells = [cell_name(gx, gz) for gz in range(z0, z1 + 1) for gx in range(x0, x1 + 1)]

    result = {
        "schemaVersion": 1,
        "purpose": "Unity vertical slice pilot corridor",
        "heroIds": args.heroes,
        "anchors": anchors,
        "boundsGlobalCells": {"x": [x0, x1], "z": [z0, z1]},
        "dimensionsInSubcells": [x1 - x0 + 1, z1 - z0 + 1],
        "dimensionsMeters": [(x1 - x0 + 1) * 250, (z1 - z0 + 1) * 250],
        "cells": cells,
        "cellCount": len(cells),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
