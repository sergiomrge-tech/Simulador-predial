"""Regression gates for actual OSM-tagged access and parcel redesign proposals."""
import json, math,unittest
from audit_r12_access_and_p5_options import OUTPUT,nearest
from analyze_r12_geo_anchor_feasibility import REPORT,SITE,sha

class OSMAccessQA(unittest.TestCase):
 def test_metric_point_to_segment_geometry(self):
  self.assertEqual(nearest((5,5),(0,0),(10,0)),5)
  self.assertEqual(nearest((15,0),(0,0),(10,0)),5)
  self.assertEqual(nearest((5,0),(0,0),(10,0)),0)
  self.assertAlmostEqual(nearest((0,4),(0,0),(0,3)),1)
 def test_provenance_unapproved_and_complete(self):
  q=json.loads(OUTPUT.read_text(encoding="utf8"))
  self.assertEqual(q["schemaVersion"],1)
  self.assertFalse(q["migration_enabled"])
  self.assertFalse(q["player_spawn_mapped"])
  self.assertFalse(q["gameplay_routes_validated"])
  self.assertTrue(q["all_options_unapproved"])
  self.assertTrue(q["original_plot_geometry_preserved"])
  self.assertTrue(q["original_gameplay_site_preserved"])
  self.assertEqual(q["source_sha256"]["gis_parcel_report"],sha(REPORT))
  self.assertEqual(q["source_sha256"]["legacy_gameplay_site"],sha(SITE))
  self.assertTrue(q["source_sha256"]["osm_snapshot_gzip"].startswith("8fa230fc41b4"))
  self.assertEqual(len(q["source_sha256"]["osm_snapshot_gzip"]),64)
  self.assertGreater(q["source_tagged_pedestrian_segments"],100)
  self.assertEqual(sorted(q["parcel_access_audit"]),["P0","P1","P2","P3","P4","P5","P6","P7"])
 def test_access_is_straightline_not_native_navmesh(self):
  q=json.loads(OUTPUT.read_text(encoding="utf8"))
  points=0
  for key,v in q["parcel_access_audit"].items():
   self.assertFalse(v["accessible_in_game"])
   if key=="P5":
    self.assertEqual(v["status"],"UNPLACED")
    self.assertIsNone(v["nearest_pedestrian_way"])
    continue
   points+=1
   self.assertIn("not a walking route",v["note"])
   for name in ("nearest_pedestrian_way","nearest_street_centerline"):
    val=v[name]
    if val is None:continue
    self.assertTrue(math.isfinite(val["distance_m"]))
    self.assertGreaterEqual(val["distance_m"],0)
    self.assertTrue(val["source_way_id"].startswith("way/"))
   self.assertEqual(v["status"],"PLANAR_CANDIDATE_REQUIRES_NATIVE_NAVMESH")
  self.assertEqual(points,7)
 def test_p5_options_do_not_modify_game_lot(self):
  q=json.loads(OUTPUT.read_text(encoding="utf8"))
  self.assertEqual(q["original_p5"],{
    "width_m":240,"depth_m":190,"area_m2":45600,
    "status":"NO_CLEAR_PLANAR_CANDIDATE_ON_25M_GRID"})
  original=json.loads(SITE.read_text(encoding="utf8"))
  p5=next(v for v in original["parcels"] if v["id"]=="P5")
  self.assertEqual((p5["width"],p5["depth"]),(240,190))
  self.assertEqual(len(q["p5_reduced_footprint_options"]),5)
  for item in q["p5_reduced_footprint_options"]:
   self.assertTrue(item["proposal_only"])
   self.assertFalse(item["gameplay_migration_enabled"])
   self.assertLess(item["area_m2"],45600)
   self.assertEqual(item["area_m2"],item["width_m"]*item["depth_m"])
   if item["free_grid_points"]:
    self.assertIsNotNone(item["candidate_center_xy_m"])
  self.assertTrue(q["all_options_unapproved"])

if __name__=="__main__":unittest.main()
