#!/usr/bin/env python3
"""Validate Santa Aurora masterplan_spec_v1.json without Blender."""
import json
import math
import sys
from pathlib import Path

root=Path(sys.argv[1] if len(sys.argv)>1 else ".").resolve()
path=root/"ArtSource"/"Blender"/"World"/"masterplan_spec_v1.json"
data=json.loads(path.read_text(encoding="utf-8"))
errors=[]
warnings=[]
world=data["world"]
minx,maxx,minz,maxz=world["minX"],world["maxX"],world["minZ"],world["maxZ"]
districts={d["id"]:d for d in data["districts"]}

def inside_world(x,z):
    return minx<=x<=maxx and minz<=z<=maxz

def inside_bounds(x,z,b):
    bx0,bz0,bx1,bz1=b
    return bx0<=x<=bx1 and bz0<=z<=bz1

all_ids=set()
for category in ("campaignLocations","lifeLocations"):
    for loc in data[category]:
        if loc["id"] in all_ids: errors.append(f"duplicate id: {loc['id']}")
        all_ids.add(loc["id"])
        if loc["district"] not in districts: errors.append(f"unknown district: {loc['id']} -> {loc['district']}")
        if not inside_world(loc["x"],loc["z"]): errors.append(f"outside world: {loc['id']}")
        d=districts.get(loc["district"])
        if d and not inside_bounds(loc["x"],loc["z"],d["bounds"]):
            warnings.append(f"outside nominal district bounds: {loc['id']}")

for loc in data["campaignLocations"]:
    if loc["width"]<=0 or loc["depth"]<=0: errors.append(f"invalid footprint: {loc['id']}")
    halfw,halfd=loc["width"]/2,loc["depth"]/2
    if not (inside_world(loc["x"]-halfw,loc["z"]-halfd) and inside_world(loc["x"]+halfw,loc["z"]+halfd)):
        errors.append(f"footprint outside world: {loc['id']}")

for road in data["roads"]:
    for p in (road["from"],road["to"]):
        if not inside_world(p[0],p[1]): errors.append(f"road endpoint outside world: {road['id']}")

macro=data["streaming"]["macroCellMeters"]
sub=data["streaming"]["subCellMeters"]
if (maxx-minx)%macro or (maxz-minz)%macro: errors.append("world not divisible by macro cell")
if macro%sub: errors.append("macro cell not divisible by subcell")

# Warn only on obvious campaign footprint collisions. Close urban lots are allowed.
campaign=data["campaignLocations"]
for i,a in enumerate(campaign):
    for b in campaign[i+1:]:
        if a["district"]!=b["district"]: continue
        dx=abs(a["x"]-b["x"]); dz=abs(a["z"]-b["z"])
        overlap_x=(a["width"]+b["width"])/2-dx
        overlap_z=(a["depth"]+b["depth"])/2-dz
        if overlap_x>0 and overlap_z>0:
            errors.append(f"campaign footprints overlap: {a['id']} / {b['id']}")

report={
    "schemaVersion":data["schemaVersion"],
    "worldMeters":[maxx-minx,maxz-minz],
    "districts":len(data["districts"]),
    "campaignLocations":len(data["campaignLocations"]),
    "lifeLocations":len(data["lifeLocations"]),
    "roads":len(data["roads"]),
    "errors":errors,
    "warnings":warnings,
    "passed":not errors
}
out=root/"Docs"/"masterplan-validation-v1.json"
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2,ensure_ascii=False))
raise SystemExit(0 if report["passed"] else 1)
