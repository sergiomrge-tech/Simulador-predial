#!/usr/bin/env python3
"""Generate Editor-only candidate parcel polygons in world X/Z (NO gameplay spawn).

Converts the frozen Blender local x/y into Unity FBX x/z under the
original 46-degree source rotation. Altitude and collisions MUST be
confirmed in Unity; NEVER populate gameplay target anchors from here.
"""
import argparse
import json
import math
from pathlib import Path
from analyze_r12_geo_anchor_feasibility import GAME,sha
SOURCE=GAME/"Docs/PROJECT_RESORT_EXECUTION/R12_GEO_ANCHOR_FEASIBILITY.json"
ACCESS=GAME/"Docs/PROJECT_RESORT_EXECUTION/R12_ACCESS_AND_P5_OPTIONS.json"
FRAME=GAME/"Docs/PROJECT_RESORT_EXECUTION/R12_SOURCE_FRAME.json"
OUTPUT=GAME/"Docs/PROJECT_RESORT_EXECUTION/R12_GEO_UNITY_REVIEW_MARKERS.json"

def world_xz(local, angle):
    # Blender mesh rotates counterclockwise in XY (Z is up);
    # FBX -Z-forward,Y-up means Blender Y -> Unity -Z.
    rad=math.radians(angle)
    c,s=math.cos(rad),math.sin(rad)
    x,y=local
    return {"x":round(x*c-y*s,6),"z":round(-x*s-y*c,6)}

def local_xy(pos,angle):
    rad=math.radians(angle)
    c,s=math.cos(rad),math.sin(rad)
    x,z=pos["x"],pos["z"]
    return (x*c-z*s,-x*s-z*c)

def build():
    source=json.loads(SOURCE.read_text(encoding="utf8"))
    access=json.loads(ACCESS.read_text(encoding="utf8"))
    frame=json.loads(FRAME.read_text(encoding="utf8"))
    assert frame["axis_angle_degrees_counterclockwise_from_east"]==46.0
    assert (frame["along_coast_length_m"],frame["inland_width_m"])==(2000,1000)
    assert source["migration_enabled"] is False and access["migration_enabled"] is False
    angle=float(frame["axis_angle_degrees_counterclockwise_from_east"])
    shapes=[]
    for name,p in sorted(source["parcels"].items()):
        rect=p["provisional_rectangle_xy_m"]
        if rect is None:continue
        x0,y0,x1,y1=rect
        local=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        verts=[world_xz(q,angle) for q in local]
        center=(sum(q[0] for q in local)/4,sum(q[1] for q in local)/4)
        assert all(abs(v-w)<1e-5 for localp,world in zip(local,verts)
                   for v,w in zip(localp,local_xy(world,angle)))
        assert abs((x1-x0)*(y1-y0)-p["size_m"]["width"]*p["size_m"]["depth"])<1e-4
        shapes.append({"id":name,"status":"EDITOR_REVIEW_ONLY_NOT_A_SPAWN_OR_RESERVED_LOT",
            "planar_only":True,"world_height_y":None,
            "center_world_xz":world_xz(center,angle),
            "outline_world_xz":verts,
            "local_rectangle_xy":rect,
            "sector":p["sector"],"source":"R12_GEO_ANCHOR_FEASIBILITY.json"})
    assert [p["id"] for p in shapes]==["P0","P1","P2","P3","P4","P6","P7"]
    return {"schemaVersion":1,
        "status":"EDITOR_PREVIEW_MARKERS_ONLY_NOT_APPROVED_FOR_GAMEPLAY",
        "source_revision":"Resort-Simulator- R13 Pass2 5217a65751a334f8ea3934ae1e7f0c75f7594a9c",
        "r12_frame":{"axis_angle_degrees":angle,
             "along_coast_m":2000,"inland_m":1000,"crs":"EPSG:32723",
             "source_frame_sha256":sha(FRAME)},
        "source_report_sha256":sha(SOURCE),"source_access_report_sha256":sha(ACCESS),
        "blender_to_unity_transform":"WorldX=x*cos(46)-y*sin(46); WorldZ=-x*sin(46)-y*cos(46).",
        "world_y_verified":False,"scene_alignment_verified_natively":False,
        "playmode_navmesh_pass":False,"gameplay_spawn_enabled":False,
        "user_original_gameplay_files_untouched":True,
        "excluded":["P5 — no valid original-size planar location","HOME_DOOR — entrance not geo-verified",
          "STALL_PROMENADE — pedestrian path not geo-verified"],
        "candidates":shapes}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    content=build()
    if args.check:
        assert json.loads(OUTPUT.read_text(encoding="utf8"))==content,"MARKERS_REPORT_NOT_REPRODUCIBLE"
    else:
        OUTPUT.write_text(json.dumps(content,ensure_ascii=False,indent=2)+"\n",
            encoding="utf8",newline="\n")
    print("R12_GEO_UNITY_XZ_CANDIDATES_PASS",
      json.dumps({"outlines":len(content["candidates"]),"world_y_verified":False,
          "runtime_activated":False}),flush=True)

if __name__=="__main__":main()
