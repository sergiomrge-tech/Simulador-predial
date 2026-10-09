#!/usr/bin/env python3
"""Frozen OSM access-distance review and P5 redesign options.

No route, navmesh, ownership or building entrance is validated here.
No gameplay anchors are moved; all returned coordinates are CANDIDATES.
"""
from __future__ import annotations
import argparse
import gzip
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from analyze_r12_geo_anchor_feasibility import (
    DEFAULT_VISUAL, GAME, SITE, REPORT as PARCEL_REPORT, read_osm,
    building_polygons, parcel_clear, score_point, sha, bbox
)
OUTPUT=GAME/"Docs/PROJECT_RESORT_EXECUTION/R12_ACCESS_AND_P5_OPTIONS.json"

def nearest(point, a,b):
    dx=b[0]-a[0];dy=b[1]-a[1]
    sq=dx*dx+dy*dy
    if sq<1e-12:return math.dist(point,a)
    t=max(0.,min(1.,((point[0]-a[0])*dx+(point[1]-a[1])*dy)/sq))
    return math.hypot(point[0]-a[0]-t*dx,point[1]-a[1]-t*dy)

def extract_access_lines(visual):
    sys.path.insert(0,str(visual/"Tools/geo"))
    from generate_r6_vegetation import Frame
    config=json.loads((visual/"geo/procedural/R4_SOURCE_FRAME.json").read_text(encoding="utf8"))
    frame=Frame(config)
    osm=visual/"geo/data/copacabana.osm.gz"
    root=ET.parse(gzip.open(osm,"rb")).getroot()
    nodes={n.get("id"):(float(n.get("lon")),float(n.get("lat"))) for n in root.findall("node")}
    pedestrian_types={"footway","pedestrian","path","steps","living_street"}
    street_types={"residential","service","tertiary","secondary","unclassified",
        "living_street","primary"}
    lines=[]
    for way in root.findall("way"):
        tags={t.get("k"):t.get("v") for t in way.findall("tag")}
        typ=tags.get("highway","")
        if tags.get("foot") in {"private","no"} or tags.get("access") in {"private","no"}:continue
        category="tagged_pedestrian" if typ in pedestrian_types else (
           "road_centerline_not_proven_sidewalk" if typ in street_types else None)
        if category is None:continue
        points=[frame.local(*nodes[n.get("ref")]) for n in way.findall("nd") if n.get("ref") in nodes]
        for a,b in zip(points,points[1:]):
            if math.dist(a,b)<.001:continue
            lines.append((way.get("id"),typ,category,a,b,bbox((a,b))))
    return lines

def nearest_lines(p, lines, category):
    chosen=(float("inf"),None,None)
    for id,typ,cat,a,b,rectangle in lines:
        if cat!=category:continue
        lower=math.hypot(max(rectangle[0]-p[0],0,p[0]-rectangle[2]),
                         max(rectangle[1]-p[1],0,p[1]-rectangle[3]))
        if lower>chosen[0]:continue
        dist=nearest(p,a,b)
        if dist<chosen[0]:chosen=(dist,id,typ)
    if chosen[1] is None:return None
    return {"distance_m":round(chosen[0],3),"source_way_id":"way/"+chosen[1],
            "highway_type":chosen[2],"line_is_road_center_not_verified_sidewalk":
            category=="road_centerline_not_proven_sidewalk"}

def allocate_option(w,h,roofs,roads,coast,already):
    best=None;free=0
    # Same 25-m grid as source audit; not exhaustive geographic proof.
    sample={"id":"P5","width":w,"depth":h}
    for cx in range(-900,901,25):
        for cy in range(-445,456,25):
            rectangle=(cx-w/2,cy-h/2,cx+w/2,cy+h/2)
            ok,_=parcel_clear(rectangle,roofs,roads,coast,already)
            if not ok:continue
            free+=1
            score=score_point(rectangle,sample,already)
            if best is None or score<best[0]:best=(score,rectangle,(cx,cy))
    return {"width_m":w,"depth_m":h,"area_m2":w*h,
      "free_grid_points":free,
      "candidate_center_xy_m":({"x":best[2][0],"y":best[2][1]} if best else None),
      "candidate_rectangle_xy_m":list(best[1]) if best else None,
      "proposal_only":True,"gameplay_migration_enabled":False}

def build(visual=DEFAULT_VISUAL):
    base=json.loads(PARCEL_REPORT.read_text(encoding="utf8"))
    site=json.loads(SITE.read_text(encoding="utf8"))
    roads,coast,source=read_osm(visual)
    roofs,roofs_meta=building_polygons(visual)
    footlines=extract_access_lines(visual)
    non_p5=[]
    for id,p in base["parcels"].items():
        if id=="P5":continue
        rect=p["provisional_rectangle_xy_m"]
        if rect is not None:non_p5.append(tuple(rect))
    entries={}
    for id,info in sorted(base["parcels"].items()):
        center=info["provisional_center_xy_m"]
        if center is None:
            entries[id]={"status":"UNPLACED","nearest_pedestrian_way":None,
                         "nearest_street_centerline":None,"accessible_in_game":False}
            continue
        p=(center["x"],center["y"])
        foot=nearest_lines(p,footlines,"tagged_pedestrian")
        road=nearest_lines(p,footlines,"road_centerline_not_proven_sidewalk")
        entries[id]={"status":"PLANAR_CANDIDATE_REQUIRES_NATIVE_NAVMESH",
            "candidate_center_xy_m":center,"nearest_pedestrian_way":foot,
            "nearest_street_centerline":road,"accessible_in_game":False,
            "note":"Distances are straight-line to OSM ways, not a walking route or player navmesh."}
    alternatives=[(180,125),(150,125),(120,100),(100,80),(80,60)]
    options=[allocate_option(w,h,roofs,roads,coast,non_p5) for w,h in alternatives]
    result={"schemaVersion":1,"status":"OSM_ACCESS_AND_P5_OPTIONS_ONLY_GAMEPLAY_BLOCKED",
       "source_sha256":{"gis_parcel_report":sha(PARCEL_REPORT),
           "osm_snapshot_gzip":source["osm_gzip_sha256"],
           "buildings":roofs_meta["building_data_sha256"],
           "geometry_frame":source["source_frame_sha256"],
           "legacy_gameplay_site":sha(SITE)},
       "frozen_input_revision":"Resort-Simulator- commit 5217a65751a334f8ea3934ae1e7f0c75f7594a9c",
       "source_way_segments_access":len(footlines),
       "source_tagged_pedestrian_segments":sum(c=="tagged_pedestrian" for _,_,c,_,_,_ in footlines),
       "parcel_access_audit":entries,
       "original_p5":{"width_m":240,"depth_m":190,"area_m2":45600,
                      "status":"NO_CLEAR_PLANAR_CANDIDATE_ON_25M_GRID"},
       "p5_reduced_footprint_options":options,
       "original_plot_geometry_preserved":True,
       "original_gameplay_site_preserved":True,
       "migration_enabled":False,
       "player_spawn_mapped":False,
       "gameplay_routes_validated":False,
       "all_options_unapproved":True,
       "limitations":["OSM pedestrian way tagging is incomplete; absence is not proof of no sidewalk",
           "Straight-line distance does not mean route/navmesh access",
           "Use/reservation of properties is NOT known; candidates may be occupied or inaccessible",
           "P5 reduction changes game design and needs explicit approval before gameplay migration",
           "Unity collision, ground height, NPC and quest tests still required"]}
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--visual",type=Path,default=DEFAULT_VISUAL)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    report=build(args.visual)
    if args.check:
        old=json.loads(OUTPUT.read_text(encoding="utf8"))
        assert old==report,"ACCESS_P5_REPORT_NOT_REPRODUCIBLE"
    else:
        OUTPUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    print("R12_OSM_PEDESTRIAN_AND_P5_OPTIONS_PASS",
          json.dumps({"tagged_foot_segments":report["source_tagged_pedestrian_segments"],
            "p5_alternatives":[(x["width_m"],x["depth_m"],x["free_grid_points"])
                for x in report["p5_reduced_footprint_options"]],
            "gameplay_enabled":False}),flush=True)
if __name__=="__main__":main()
