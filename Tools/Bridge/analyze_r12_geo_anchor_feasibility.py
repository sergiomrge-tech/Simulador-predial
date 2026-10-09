#!/usr/bin/env python3
"""Pure-Python, conservative, frozen-OSM feasibility audit for ResortSite parcel sizes.

No new gameplay anchors are approved or activated by this script.
Every proposal stays CANDIDATE_UNVERIFIED until native Unity collision,
navigability, building entrance and mission/save regression tests.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve()
GAME=HERE.parents[2]
DEFAULT_VISUAL=Path(r"D:\ProjectResort_R13_Sol61_Pass2")
SITE=GAME/"FacilityOps/Assets/_Game/Resources/Resort/ResortSite.json"
BASE=GAME/"FacilityOps/Assets/_Game/Resources/Resort/R12GameplayAnchorInventory.json"
REPORT=GAME/"Docs/PROJECT_RESORT_EXECUTION/R12_GEO_ANCHOR_FEASIBILITY.json"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def polygon_contains(point,ring):
    x,y=point
    inside=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if ((a[1]>y)!=(b[1]>y)) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            inside=not inside
    return inside

def segment_rect(a,b,rect):
    """Liang–Barsky test inclusive of touching. All positions are local metres."""
    xmin,ymin,xmax,ymax=rect
    x0,y0=a;dx,dy=b[0]-x0,b[1]-y0
    low,high=0.,1.
    for p,q in ((-dx,x0-xmin),(dx,xmax-x0),(-dy,y0-ymin),(dy,ymax-y0)):
        if abs(p)<1e-12:
            if q<0:return False
            continue
        t=q/p
        if p<0:low=max(low,t)
        else:high=min(high,t)
        if low>high:return False
    return True

def point_rect(point,rect):
    return rect[0]<=point[0]<=rect[2] and rect[1]<=point[1]<=rect[3]

def polygon_rect(ring,rect):
    if any(point_rect(p,rect) for p in ring):return True
    corners=((rect[0],rect[1]),(rect[0],rect[3]),(rect[2],rect[1]),(rect[2],rect[3]))
    if any(polygon_contains(c,ring) for c in corners):return True
    return any(segment_rect(a,b,rect) for a,b in zip(ring,ring[1:]+ring[:1]))

def rect_intersection(a,b):
    return a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]

def bbox(points):
    return (min(p[0] for p in points),min(p[1] for p in points),
        max(p[0] for p in points),max(p[1] for p in points))

def expand(rect,amount):
    return (rect[0]-amount,rect[1]-amount,rect[2]+amount,rect[3]+amount)

def land_coast_y(x,coast):
    vals=[]
    for a,b in zip(coast,coast[1:]):
        if min(a[0],b[0])<=x<=max(a[0],b[0]) and abs(a[0]-b[0])>1.e-8:
            vals.append(a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0]))
    if len(vals)!=1:
        raise ValueError("OSM_COASTLENGTH_UNSUPPORTED_X: "+str((x,vals)))
    return vals[0]

def read_osm(visual):
    sys.path.insert(0,str(visual/"Tools/geo"))
    from generate_r6_vegetation import Frame,DEFAULT_ROAD_WIDTH_M
    framefile=visual/"geo/procedural/R4_SOURCE_FRAME.json"
    geo=json.loads(framefile.read_text(encoding="utf8"))
    frame=Frame(geo)
    osmfile=visual/"geo/data/copacabana.osm.gz"
    xml=ET.parse(gzip.open(osmfile,"rb")).getroot()
    nodes={n.get("id"):(float(n.get("lon")),float(n.get("lat"))) for n in xml.findall("node")}
    roads=[];coast=[]
    for way in xml.findall("way"):
        tags={t.get("k"):t.get("v") for t in way.findall("tag")}
        nd=[frame.local(*nodes[n.get("ref")]) for n in way.findall("nd") if n.get("ref") in nodes]
        if way.get("id")=="70574890":
            coast=nd
        highway=tags.get("highway","")
        if highway and len(nd)>=2:
            width_text=tags.get("width","")
            try:
                width=float(width_text.strip().lower().replace("meters","").replace("meter","").replace("m",""))
                if width<=0:raise ValueError
            except ValueError:
                width=DEFAULT_ROAD_WIDTH_M.get(highway,4.0)
            margin=width/2+1.5
            for a,b in zip(nd,nd[1:]):
                roads.append((a,b,margin,expand(bbox((a,b)),margin)))
    if len(coast)<120 or len(roads)<200:
        raise ValueError("UNEXPECTED_FROZEN_OSM_INPUT")
    return roads,coast,{"osm_gzip_sha256":sha(osmfile),"source_frame_sha256":sha(framefile),
        "road_segments":len(roads),"shoreline_points":len(coast),"geo_frame":geo}

def building_polygons(visual):
    file=visual/"geo/procedural/R4_OSM_50_STYLE_ASSIGNMENTS.json"
    buildingdata=json.loads(file.read_text(encoding="utf8"))["buildings"]
    if len(buildingdata)!=1468:raise ValueError("BUILDING_FOOTPRINT_COUNT_DRIFT")
    roofs=[]
    for entry in buildingdata:
        ring=[tuple(p) for p in entry["footprint_ring_local_xy_m"]]
        if len(ring)<3:continue
        roofs.append((entry["building_id"],ring,bbox(ring)))
    return roofs,{"building_data_sha256":sha(file),"osm_buildings":len(buildingdata)}

def parcel_clear(rect,roofs,roads,coast,already):
    rect_extra=expand(rect,1.25)
    if not (-998<=rect_extra[0] and rect_extra[2]<=998 and
            -498<=rect_extra[1] and rect_extra[3]<=498):
        return False,"FRAME"
    for other in already:
        if rect_intersection(expand(other,4.0),rect):
            return False,"OTHER_GAME_PARCEL"
    for x in (rect_extra[0],(rect_extra[0]+rect_extra[2])/2,rect_extra[2]):
        if rect_extra[1]<land_coast_y(x,coast)+55:
            return False,"OSM_SHORE_55M_BUFFER"
    for _,ring,rb in roofs:
        if rect_intersection(rect_extra,rb) and polygon_rect(ring,rect_extra):
            return False,"OSM_BUILDING"
    for a,b,margin,rb in roads:
        if rect_intersection(rect_extra,rb) and segment_rect(a,b,expand(rect_extra,margin)):
            return False,"OSM_ROAD_ENVELOPE"
    return True,"CLEAR_OF_KNOWN_PLANIMETRY"

def sector_of(x):
    return min(9,max(0,int((x+1000)//200)))

def score_point(rect,parcel,already):
    cx=(rect[0]+rect[2])/2;cy=(rect[1]+rect[3])/2
    # Gameplay priority is proximity to coastal commerce for P0/P1, then
    # spread out inland for other development lots. Only a heuristic;
    # never a real building/parcel entitlement or approved location.
    coast_preference= -290 if parcel["id"] in ("P0","P1","P7") else 85
    return abs(cy-coast_preference)+abs(cx)*.08+sum(max(0,150-abs(cx-((a[0]+a[2])/2)))*.08 for a in already)

def candidate_slots(parcels,roofs,roads,coast):
    # Largest-first allocation to avoid artificially stealing scarce space
    # with smaller parcels. Preserve source parcel IDs and exact dimensions.
    taken=[];result={}
    order=sorted(parcels,key=lambda p:p["width"]*p["depth"],reverse=True)
    for parcel in order:
        w=float(parcel["width"]);h=float(parcel["depth"])
        tested=0;rejected={};feasible=[]
        # Non-destructive candidate lattice in the frozen LOCAL OSM frame.
        x_points=[-900+i*25 for i in range(73)]
        y_points=[-445+i*25 for i in range(37)]
        for cx in x_points:
            for cy in y_points:
                if cy-h/2<-498 or cy+h/2>498 or cx-w/2<-998 or cx+w/2>998:
                    continue
                rect=(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
                tested+=1
                ok,reason=parcel_clear(rect,roofs,roads,coast,taken)
                if ok:
                    feasible.append((score_point(rect,parcel,taken),rect,(cx,cy)))
                else:
                    rejected[reason]=rejected.get(reason,0)+1
        feasible.sort(key=lambda t:t[0])
        chosen=feasible[0] if feasible else None
        if chosen:taken.append(chosen[1])
        result[parcel["id"]]={
            "status":"GEOMETRY_CANDIDATE_UNVERIFIED" if chosen else "NO_FREE_CANDIDATE_ON_25M_GRID",
            "size_m":{"width":parcel["width"],"depth":parcel["depth"]},
            "grid_candidates_tested":tested,
            "free_candidates_before_reserving":len(feasible),
            "rejection_counts":rejected,
            "provisional_center_xy_m":({"x":chosen[2][0],"y":chosen[2][1]} if chosen else None),
            "provisional_rectangle_xy_m":list(chosen[1]) if chosen else None,
            "sector":("S%02d"%sector_of(chosen[2][0]) if chosen else None),
            "never_approved":True}
    return result

def main(visual=DEFAULT_VISUAL,save=True):
    data=json.loads(SITE.read_text(encoding="utf8"))
    base=json.loads(BASE.read_text(encoding="utf8"))
    roads,coast,source=read_osm(visual)
    roofs,roofmeta=building_polygons(visual)
    source.update(roofmeta)
    source["legacy_site_sha256"]=sha(SITE)
    source["legacy_anchor_inventory_sha256"]=sha(BASE)
    source["frame_file_sha256_for_bridge"]=base["source_frame_sha256"]
    parcels=candidate_slots(data["parcels"],roofs,roads,coast)
    assert len(parcels)==8 and all(p["never_approved"] for p in parcels.values())
    record={
      "schemaVersion":1,
      "status":"OSM_GEOMETRIC_ONLY_CANDIDATES_NOT_GAMEPLAY_PLACEMENTS",
      "source_hashes":source,
      "frame":"2000m coastline x 1000m inland, EPSG:32723, 46deg",
      "parcel_rule":"exact legacy width/depth, 1.25m building clearance, road class width/2 + 1.5m, 55m inland from OSM shoreline, 4m interparcel buffer",
      "grid_step_m":25,
      "source_footprints_unchanged":True,
      "source_road_geometry_unchanged":True,
      "original_gameplay_unchanged":True,
      "migration_enabled":False,
      "home_building_entry":"NOT_MAPPED_NO_ENTRANCE_GEOMETRY_VERIFIED",
      "stall_access":"NOT_MAPPED_REQUIRES_ACTUAL_COAST_PEDESTRIAN_NAVIGATION",
      "parcels":parcels,
      "remaining_native_gates":["real building entrance and home mapping",
            "usable/legal site vs GIS footprint/road exclusion",
            "Unity colliders, navmesh, player+NPC paths and spawn height",
            "persisting all old saves and quest waypoints",
            "single ocean/road/terrain and tested game performance"] }
    if save:
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",
            encoding="utf-8",newline="\n")
    brief={"parcel_candidates_found":sum(p["provisional_center_xy_m"] is not None for p in parcels.values()),
       "no_site":sorted([id for id,p in parcels.items() if p["provisional_center_xy_m"] is None]),
       "sha_source":source["osm_gzip_sha256"][:12],"source_roads":len(roads)}
    print("R12_GEO_FEASIBILITY_ANALYSIS_PASS",json.dumps(brief,ensure_ascii=False),flush=True)
    return record

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--visual",type=Path,default=DEFAULT_VISUAL)
    ap.add_argument("--check",action="store_true")
    opts=ap.parse_args()
    m=main(opts.visual,not opts.check)
    if opts.check:
        old=json.loads(REPORT.read_text(encoding="utf-8"))
        if old!=m:
            mismatches=[]
            def compare(a,b,where="report"):
                if type(a)!=type(b):
                    mismatches.append((where,"different types",str(type(a)),str(type(b))))
                elif isinstance(a,dict):
                    for k in sorted(set(a)|set(b)):
                        if k not in a or k not in b:
                            mismatches.append((where+"."+k,"key absent",str(k in a),str(k in b)))
                        else:compare(a[k],b[k],where+"."+k)
                elif isinstance(a,list):
                    if len(a)!=len(b):mismatches.append((where,"different length",str(len(a)),str(len(b))))
                    else:
                        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,where+"["+str(i)+"]")
                elif a!=b:
                    mismatches.append((where,"different value",repr(a),repr(b)))
            compare(old,m)
            for diff in mismatches[:22]:
                print("R12_GEO_CROSS_PLATFORM_DIFF",*diff,flush=True)
            raise SystemExit("NOT_REPRODUCIBLE "+str(len(mismatches))+" field(s)")
