"""Native Unity proof that unapproved GIS plot outlines are EDITOR-ONLY."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/"Docs/PROJECT_RESORT_EXECUTION/R12_GEO_CANDIDATE_PREVIEW_NATIVE_QA.json"
SOURCE=ROOT/"FacilityOps/Assets/_Game/Scripts/Resort/Editor/ResortR12GeoCandidatePreview.cs"

class EditorOnlyNativeGate(unittest.TestCase):
 def test_native_report_reports_no_gameplay_modifications(self):
  q=json.loads(DOC.read_text(encoding="utf-8-sig"))
  self.assertEqual(q["status"],"R12_EDITOR_GIS_CANDIDATES_NATIVE_PASS_NOT_GAMEPLAY")
  self.assertEqual(q["unity_version"],"6000.6.2f1")
  self.assertEqual(q["candidates"],7)
  self.assertEqual(q["outline_segments"],28)
  self.assertEqual(q["visible_labels"],7)
  self.assertTrue(q["source_scene_bytes_preserved"])
  self.assertTrue(q["game_scene_unmodified"])
  self.assertFalse(q["world_y_verified"])
  self.assertFalse(q["playable_migration_enabled"])
  self.assertFalse(q["native_navmesh_tested"])
  self.assertFalse(q["colliders_validated"])
  self.assertRegex(q["source_scene_sha256"],r"^[0-9a-f]{64}$")
  self.assertNotEqual(q["source_scene"],q["preview_scene"])
  self.assertIn("GeometricCandidates_Review.unity",q["preview_scene"])
 def test_native_builder_is_editor_only_and_never_changes_legacy_scene(self):
  s=SOURCE.read_text(encoding="utf-8-sig")
  self.assertIn('overlay.tag = "EditorOnly"',s)
  self.assertIn('line.tag = "EditorOnly"',s)
  self.assertIn("DestroyImmediate(col)",s)
  self.assertIn("SaveScene(scene,Output,true)",s)
  self.assertIn("source_scene_bytes_preserved",s)
  self.assertIn("!plan.gameplay_spawn_enabled",s)
  self.assertIn("R12GameplayWorldGate.Sha256",s)
  self.assertIn('x.id!="P5"',s)
  self.assertNotIn("PlayerPrefs.DeleteAll",s)
  self.assertNotIn("ResortSite.Build(",s)
if __name__=="__main__":unittest.main()
