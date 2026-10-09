"""R12 source-OSM geometric candidate safety; does not enable gameplay."""
from pathlib import Path
import json
import math
import unittest
from analyze_r12_geo_anchor_feasibility import (
    REPORT,SITE,BASE,point_rect,polygon_contains,polygon_rect,
    segment_rect,rect_intersection,bbox,sha
)
class Geometry(unittest.TestCase):
 def test_segment_rectangle_intersection(self):
  rectangle=(0,0,10,10)
  self.assertTrue(segment_rect((-10,5),(20,5),rectangle))
  self.assertTrue(segment_rect((5,-10),(5,20),rectangle))
  self.assertTrue(segment_rect((-10,-10),(0,0),rectangle))
  self.assertFalse(segment_rect((-10,-10),(-3,-3),rectangle))
  self.assertFalse(segment_rect((-10,15),(20,15),rectangle))
 def test_polygon_rectangle_collision(self):
  rect=(10,10,20,20)
  self.assertTrue(polygon_rect([(8,8),(22,8),(22,22),(8,22)],rect))
  self.assertTrue(polygon_rect([(13,13),(14,13),(14,14),(13,14)],rect))
  self.assertTrue(polygon_rect([(8,15),(22,15),(22,17),(8,17)],rect))
  self.assertFalse(polygon_rect([(2,2),(7,2),(7,7),(2,7)],rect))
  self.assertFalse(rect_intersection(rect,(30,30,40,40)))
 def test_report_against_frozen_source_hash_and_no_auto_migration(self):
  report=json.loads(REPORT.read_text(encoding="utf-8-sig"))
  base=json.loads(BASE.read_text(encoding="utf-8-sig"))
  self.assertEqual(report["status"],"OSM_GEOMETRIC_ONLY_CANDIDATES_NOT_GAMEPLAY_PLACEMENTS")
  self.assertFalse(report["migration_enabled"])
  self.assertTrue(report["original_gameplay_unchanged"])
  self.assertTrue(report["source_road_geometry_unchanged"])
  self.assertTrue(report["source_footprints_unchanged"])
  self.assertEqual(report["source_hashes"]["legacy_site_sha256"],sha(SITE))
  self.assertEqual(report["source_hashes"]["legacy_anchor_inventory_sha256"],sha(BASE))
  self.assertEqual(len(report["parcels"]),8)
  self.assertEqual(report["grid_step_m"],25)
  self.assertEqual(report["source_hashes"]["osm_buildings"],1468)
  self.assertEqual(report["source_hashes"]["geo_frame"]["along_coast_length_m"],2000)
  self.assertEqual(report["source_hashes"]["geo_frame"]["inland_width_m"],1000)
  self.assertFalse(base["migration_enabled"])
  self.assertTrue(all(a["target"] is None for a in base["anchors"]))
 def test_rectangles_nonoverlap_and_size_matches_legacy(self):
  report=json.loads(REPORT.read_text(encoding="utf-8-sig"))
  site=json.loads(SITE.read_text(encoding="utf-8-sig"))
  ids={p["id"]:p for p in site["parcels"]}
  entries=report["parcels"]
  rectangles=[]
  for name,item in entries.items():
   self.assertTrue(item["never_approved"])
   self.assertEqual(item["size_m"],{"width":ids[name]["width"],"depth":ids[name]["depth"]})
   center=item["provisional_center_xy_m"]
   if center is None:
    self.assertEqual(item["status"],"NO_FREE_CANDIDATE_ON_25M_GRID")
    self.assertIsNone(item["provisional_rectangle_xy_m"])
    continue
   self.assertEqual(item["status"],"GEOMETRY_CANDIDATE_UNVERIFIED")
   rect=item["provisional_rectangle_xy_m"]
   self.assertAlmostEqual(rect[2]-rect[0],ids[name]["width"])
   self.assertAlmostEqual(rect[3]-rect[1],ids[name]["depth"])
   self.assertAlmostEqual((rect[0]+rect[2])/2,center["x"])
   self.assertAlmostEqual((rect[1]+rect[3])/2,center["y"])
   self.assertTrue(-1000<rect[0]<rect[2]<1000)
   self.assertTrue(-500<rect[1]<rect[3]<500)
   for other in rectangles:self.assertFalse(rect_intersection(rect,other))
   rectangles.append(rect)
  self.assertEqual(sum(v["status"]=="GEOMETRY_CANDIDATE_UNVERIFIED" for v in entries.values()),7)
  self.assertEqual(entries["P5"]["status"],"NO_FREE_CANDIDATE_ON_25M_GRID")
  self.assertEqual(entries["P5"]["size_m"],{"width":240,"depth":190})
  self.assertEqual(entries["P5"]["free_candidates_before_reserving"],0)
if __name__=="__main__":unittest.main()
