"""Guard native-frame mapping before any Editor-only map review."""
import json
import math
import unittest
from prepare_r12_unity_review_markers import OUTPUT,FRAME,build,world_xz,local_xy
class UnityMarkerTests(unittest.TestCase):
 def test_blender_unity_exact_cardinal_basis(self):
  p=world_xz((100,0),0)
  self.assertEqual(p,{"x":100.0,"z":-0.0})
  self.assertEqual(world_xz((0,100),0),{"x":0.0,"z":-100.0})
  for a in (0,27,46,90,180):
   for p in [(-1000,-500),(0,0),(225,-340),(1000,500)]:
    v=world_xz(p,a)
    t=local_xy(v,a)
    self.assertAlmostEqual(t[0],p[0],places=5)
    self.assertAlmostEqual(t[1],p[1],places=5)
 def test_footprints_and_gameplay_unmodified(self):
  r=json.loads(OUTPUT.read_text(encoding="utf8"))
  self.assertFalse(r["world_y_verified"])
  self.assertFalse(r["scene_alignment_verified_natively"])
  self.assertFalse(r["gameplay_spawn_enabled"])
  self.assertFalse(r["playmode_navmesh_pass"])
  self.assertTrue(r["user_original_gameplay_files_untouched"])
  self.assertEqual(len(r["candidates"]),7)
  self.assertNotIn("P5",[x["id"] for x in r["candidates"]])
  for p in r["candidates"]:
   self.assertIsNone(p["world_height_y"])
   self.assertTrue(p["planar_only"])
   self.assertEqual(len(p["outline_world_xz"]),4)
   area=0.
   for a,b in zip(p["outline_world_xz"],p["outline_world_xz"][1:]+p["outline_world_xz"][:1]):
    area+=a["x"]*b["z"]-b["x"]*a["z"]
   rect=p["local_rectangle_xy"]
   self.assertAlmostEqual(abs(area)/2,(rect[2]-rect[0])*(rect[3]-rect[1]),places=2)
 def test_report_is_generated_from_source(self):
  self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf8")),build())
if __name__=="__main__":unittest.main()
