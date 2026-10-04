"""Export gameplay markers from the currently opened Blender file for Unity.

The exporter is read-only. It serializes marker transforms and stable metadata to JSON.

Example:
blender -b ArtSource/Blender/World/OldTown/Heroes/W2_horizonte.blend \
  --python Tools/Blender/export_unity_gameplay_markers.py -- \
  --root . --name horizonte

Coordinate contract:
Blender X -> Unity X
Blender Y -> Unity Z
Blender Z -> Unity Y

For orientation the file stores Unity-space forward/up vectors. Unity can rebuild
rotation with Quaternion.LookRotation(forward, up).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--facility", default="")
    p.add_argument("--output", default="")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return p.parse_args(argv)


def unity_vec(v: Vector) -> list[float]:
    return [round(float(v.x), 6), round(float(v.z), 6), round(float(v.y), 6)]


def json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    try:
        return list(value)
    except TypeError:
        return str(value)


def is_marker(obj) -> bool:
    if obj.name.startswith(("GP_", "SLOT_", "PROXY_", "HERO_", "W2_SLOT_")):
        return True
    if obj.get("sa_layer") == "Gameplay":
        return True
    return obj.get("sa_kind") in {
        "spawn",
        "interaction",
        "state_slot",
        "gameplay_marker",
        "trigger",
        "entry",
        "exit",
    }


def record(obj) -> dict:
    mw = obj.matrix_world
    basis = mw.to_3x3()
    forward_blender = basis @ Vector((0.0, -1.0, 0.0))
    up_blender = basis @ Vector((0.0, 0.0, 1.0))
    scale_blender = mw.to_scale()

    custom = {}
    for key in obj.keys():
        if key == "_RNA_UI":
            continue
        custom[key] = json_value(obj.get(key))

    return {
        "name": obj.name,
        "type": obj.type,
        "facilityId": obj.get("facility_id"),
        "kind": obj.get("sa_kind"),
        "layer": obj.get("sa_layer"),
        "state": obj.get("state"),
        "item": obj.get("item"),
        "note": obj.get("note"),
        "position": unity_vec(mw.translation),
        "forward": unity_vec(forward_blender.normalized()),
        "up": unity_vec(up_blender.normalized()),
        "scale": unity_vec(scale_blender),
        "custom": custom,
    }


def main() -> int:
    opt = parse_args()
    root = Path(opt.root).resolve()
    markers = sorted((o for o in bpy.data.objects if is_marker(o)
                      and (not opt.facility or o.get('facility_id') == opt.facility)), key=lambda o: o.name)

    duplicate_names = []
    seen = set()
    for obj in markers:
        if obj.name in seen:
            duplicate_names.append(obj.name)
        seen.add(obj.name)

    records = [record(o) for o in markers]

    report = {
        "schemaVersion": 1,
        "name": opt.name,
        "sourceBlend": Path(bpy.data.filepath).as_posix(),
        "blenderVersion": bpy.app.version_string,
        "coordinateContract": "Blender X->Unity X, Blender Y->Unity Z, Blender Z->Unity Y",
        "orientationContract": "Quaternion.LookRotation(forward, up)",
        "markerCount": len(records),
        "duplicateNames": sorted(set(duplicate_names)),
        "markers": records,
        "status": "PASS" if not duplicate_names and records else "FAIL",
    }

    if opt.output:
        output = Path(opt.output).resolve()
    else:
        output = (
            root
            / "ArtSource"
            / "Blender"
            / "World"
            / "UnityExport"
            / "Markers"
            / f"{opt.name}.markers.json"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": report["status"],
                "markers": report["markerCount"],
                "duplicates": report["duplicateNames"],
                "output": str(output),
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
