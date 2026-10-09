#!/usr/bin/env python3
"""Phase-I *audit* of legacy gameplay anchors before map migration.

Do not guess geographic coordinates, warp geometry, modify save games, or
activate R12 from this file. The 2km OSM world remains authoritative.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAME_SITE = ROOT / "FacilityOps/Assets/_Game/Resources/Resort/ResortSite.json"
R4 = ROOT / "Docs/PROJECT_RESORT_EXECUTION/R12_SOURCE_FRAME.json"
OUTPUT = ROOT / "FacilityOps/Assets/_Game/Resources/Resort/R12GameplayAnchorInventory.json"
REPORT = ROOT / "Docs/PROJECT_RESORT_EXECUTION/R12_GAMEPLAY_ANCHORS_QA.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def finite(v):
    return isinstance(v, (int,float)) and not isinstance(v,bool) and math.isfinite(v)

def promenade_z(data, x):
    points = data["promenade"]
    if x <= points[0]["x"]:
        return float(points[0]["z"])
    for a,b in zip(points,points[1:]):
        if x <= b["x"]:
            t = (x-a["x"])/max(0.001,b["x"]-a["x"])
            return round(a["z"] + (b["z"]-a["z"])*t,6)
    return float(points[-1]["z"])

def record(id, label, source, x, z, role):
    if not finite(x) or not finite(z):
        raise ValueError("INVALID_LEGACY_ANCHOR: "+id)
    return {"id":id,"label":label,"source":source,
        "role":role,"legacy":{"x":round(float(x),6),"z":round(float(z),6)},
        "target":None,"status":"GEOGRAPHIC_PLACEMENT_UNVERIFIED"}

def build(site_path=GAME_SITE, r4_path=R4):
    data=json.loads(site_path.read_text(encoding="utf-8"))
    frame=json.loads(r4_path.read_text(encoding="utf-8"))
    dims=data["size"]
    if (dims["x"],dims["z"])!=(900.0,720.0):
        raise ValueError("LEGACY_SITE_FRAME_CHANGED_REAUDIT_REQUIRED")
    if (frame["along_coast_length_m"],frame["inland_width_m"])!=(2000.0,1000.0):
        raise ValueError("REAL_OSM_COAST_FRAME_CHANGED")
    if frame["crs"]!="EPSG:32723":
        raise ValueError("GEOREFERENCE_CRS_CHANGED")
    if len(data["lots"])!=234 or len(data["promenade"])!=76:
        raise ValueError("LEGACY_LAYOUT_COUNT_DRIFT")
    home=data["home"]
    anchors=[
        record("HOME_DOOR",home["name"]+" — "+home["unit"],
            "home.x / home.doorZ",home["x"],home["doorZ"],"player_spawn"),
        record("STALL_PROMENADE", "Quiosque inicial", "stall.x / interpolated promenade",
            data["stall"]["x"],promenade_z(data,data["stall"]["x"]),"shop"),
    ]
    for parcel in sorted(data["parcels"],key=lambda p:p["id"]):
        if not parcel["id"].startswith("P"):
            raise ValueError("INVALID_PARCEL_ID")
        x=parcel["x"]+parcel["width"]*.5
        z=parcel["z"]+parcel["depth"]*.5
        anchors.append(record("PARCEL_"+parcel["id"],parcel["name"],
            "parcels."+parcel["id"]+" (rectangle center)",x,z,"parcel"))
    ids=[x["id"] for x in anchors]
    if len(anchors)!=10 or len(set(ids))!=10:
        raise ValueError("REQUIRED_10_GAMEPLAY_ANCHORS_MISSING")
    for item in anchors:
        v=item["legacy"]
        if not 0 <= v["x"] <= dims["x"] or not 0 <= v["z"] <= dims["z"]:
            raise ValueError("GAMEPLAY_ANCHOR_OUTSIDE_OLD_SITE: "+item["id"])
    plan={
      "schemaVersion":1,
      "status":"NOT_APPROVED_MUST_KEEP_LEGACY_GAMEPLAY_WORLD",
      "approved":False,
      "source_site_sha256":sha(site_path),
      "source_frame_sha256":sha(r4_path),
      "source_gameplay_scene":"Assets/_Game/Scenes/ResortPrologue.unity",
      "target_scene":"Assets/_Game/Preview/CopacabanaR12/Scenes/R12_Copacabana_Lojas_Vitrines_Entradas.unity",
      "legacy_size_m":{"x":900.0,"z":720.0},
      "r12_geo":{"crs":frame["crs"],"along_coast_m":2000,
          "inland_m":1000,"axis_angle_degrees":frame["axis_angle_degrees_counterclockwise_from_east"]},
      "transform_policy":"ONE_TO_ONE_METRES_RIGID_ROTATION_TRANSLATION_ONLY_NO_RESIZE",
      "migration_enabled":False,
      "anchors":anchors,
      "remaining":["survey/geometrically verify target locations on R12 map",
          "validate free areas and existing building/road clearance per target",
          "find safe NPC/quest paths and parcels",
          "validate spawn collider and player navigation",
          "preserve historical save state and migrate only verified positions",
          "disable duplicate terrain/sea/roads in R12 mode",
          "run actual gameplay and FPS tests before enable"]
    }
    report={
        "status":"R12_ANCHOR_LEGACY_INVENTORY_PASS_GEOGRAPHIC_PLACEMENT_PENDING",
        "anchors_count":len(anchors),
        "legacy_home":anchors[0]["legacy"],
        "legacy_stall":anchors[1]["legacy"],
        "parcels_count":len(data["parcels"]),
        "legacy_lots":len(data["lots"]),
        "legacy_prompoints":len(data["promenade"]),
        "ready_to_switch":False,
        "no_world_coordinates_invented":all(x["target"] is None for x in anchors),
        "preserves_gameplay_site_sha256":plan["source_site_sha256"],
        "source_frame_sha256":plan["source_frame_sha256"]
    }
    return plan,report

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(obj,ensure_ascii=False,indent=2)+"\n"
    path.write_text(data,encoding="utf-8",newline="\n")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true",help="verify committed JSON without mutating it")
    args=parser.parse_args()
    plan,qa=build()
    if args.check:
        for dest,expected in ((OUTPUT,plan),(REPORT,qa)):
            if not dest.is_file() or json.loads(dest.read_text(encoding="utf-8"))!=expected:
                raise SystemExit("R12_ANCHOR_INVENTORY_CHANGED:"+str(dest))
    else:
        save(OUTPUT,plan)
        save(REPORT,qa)
    print("R12_GAMEPLAY_ANCHOR_INVENTORY_PASS",
          json.dumps({"anchors":qa["anchors_count"],"verified_target_coordinates":0,
                      "migration_enabled":False,"legacy_map":[900,720],
                      "target_map":[2000,1000]},ensure_ascii=False))
