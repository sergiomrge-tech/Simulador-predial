#!/usr/bin/env python3
"""Validate the Santa Aurora masterplan (spec + W1.5 layout) without Blender.

Usage: python Tools/Map/validate_masterplan.py [PROJECT_ROOT]
Writes Docs/masterplan-validation-v1.json (keeps the W1 keys; adds the W1.5 layout report).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from masterplan_layout import Layout, load_registry  # noqa: E402

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
path = root / "ArtSource" / "Blender" / "World" / "masterplan_spec_v1.json"
data = json.loads(path.read_text(encoding="utf-8"))
errors, warnings = [], []
world = data["world"]
minx, maxx, minz, maxz = world["minX"], world["maxX"], world["minZ"], world["maxZ"]
districts = {d["id"]: d for d in data["districts"]}


def inside_world(x, z):
    return minx <= x <= maxx and minz <= z <= maxz


def inside_bounds(x, z, b):
    return b[0] <= x <= b[2] and b[1] <= z <= b[3]


all_ids = set()
for category in ("campaignLocations", "lifeLocations"):
    for loc in data[category]:
        if loc["id"] in all_ids:
            errors.append(f"duplicate id: {loc['id']}")
        all_ids.add(loc["id"])
        if loc["district"] not in districts:
            errors.append(f"unknown district: {loc['id']} -> {loc['district']}")
        if not inside_world(loc["x"], loc["z"]):
            errors.append(f"outside world: {loc['id']}")
        d = districts.get(loc["district"])
        if d and not inside_bounds(loc["x"], loc["z"], d["bounds"]):
            warnings.append(f"outside nominal district bounds: {loc['id']}")
for loc in data["campaignLocations"]:
    if loc["width"] <= 0 or loc["depth"] <= 0:
        errors.append(f"invalid footprint: {loc['id']}")
for road in data["roads"]:
    for p in road.get("points") or (road["from"], road["to"]):
        if not inside_world(p[0], p[1]):
            errors.append(f"road point outside world: {road['id']}")
for rail in data.get("railways", []):
    for p in rail["points"]:
        if not inside_world(p[0], p[1]):
            errors.append(f"rail point outside world: {rail['id']}")
macro = data["streaming"]["macroCellMeters"]
sub = data["streaming"]["subCellMeters"]
if (maxx - minx) % macro or (maxz - minz) % macro:
    errors.append("world not divisible by macro cell")
if macro % sub:
    errors.append("macro cell not divisible by subcell")

layout = Layout(data, load_registry(root), root=root)
layout_report = layout.checks()
errors.extend(layout.errors)
warnings.extend(layout.warnings)

report = {
    "schemaVersion": data["schemaVersion"],
    "revision": data.get("revision", "W1"),
    "worldMeters": [maxx - minx, maxz - minz],
    "districts": len(data["districts"]),
    "campaignLocations": len(data["campaignLocations"]),
    "lifeLocations": len(data["lifeLocations"]),
    "roads": len(data["roads"]),
    "railways": len(data.get("railways", [])),
    "transitionZones": len(data.get("transitionZones", [])),
    "errors": errors,
    "warnings": warnings,
    "layout": layout_report,
    "passed": not errors,
}
out = root / "Docs" / "masterplan-validation-v1.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
summary = {k: v for k, v in report.items() if k != "layout"}
summary["layoutSummary"] = {k: v for k, v in layout_report.items() if k not in ("access", "oldTown")}
print(json.dumps(summary, indent=2, ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
