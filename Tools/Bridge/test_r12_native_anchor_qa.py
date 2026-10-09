"""Validate native Unity anchor QA provenance and fail-closed gameplay switch."""
import hashlib,json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOC=ROOT/"Docs/PROJECT_RESORT_EXECUTION/R12_GAMEPLAY_ANCHOR_NATIVE_QA.json"
SCENE=ROOT/"FacilityOps/Assets/_Game/Scenes/ResortPrologue.unity"
class NativeAnchorQA(unittest.TestCase):
 def test_unity_native_evidence_preserves_gameplay_scene(self):
  q=json.loads(DOC.read_text(encoding="utf-8-sig"))
  self.assertEqual(q["status"],"R12_ANCHORS_UNITY_NATIVE_PASS_MIGRATION_BLOCKED")
  self.assertEqual(q["unity"],"6000.6.2f1")
  self.assertEqual(q["reason"],"MAP_NOT_APPROVED_FOR_PLAYABLE_MIGRATION")
  self.assertEqual(q["anchorCount"],10)
  self.assertEqual(q["verifiedTargetCount"],0)
  self.assertEqual(q["originalParcels"],8)
  self.assertFalse(q["migrationEnabled"])
  self.assertTrue(q["legacyGameplayPreserved"])
  self.assertTrue(q["sourceVisualSceneFound"])
  self.assertRegex(q["originalGameplaySceneSha256"],r"^[a-f0-9]{64}$")
  self.assertEqual(q["originalGameplaySceneSha256"],
    hashlib.sha256(SCENE.read_bytes()).hexdigest())
 def test_runtime_gate_has_no_direct_gameplay_injection(self):
  path=ROOT/"FacilityOps/Assets/_Game/Scripts/Resort/Site/R12GameplayWorldGate.cs"
  s=path.read_text(encoding="utf-8-sig")
  self.assertIn("return false;",s)
  self.assertIn("ANCHOR_BOOKKEEPING_VALID_RUNTIME_INTEGRATION_NOT_IMPLEMENTED",s)
  self.assertIn("LEGACY_SITE_HASH_CHANGED",s)
  self.assertIn("MAP_NOT_APPROVED_FOR_PLAYABLE_MIGRATION",s)
  self.assertNotIn("ResortSite.Build(",s.split("public static class R12GameplayWorldGate",1)[-1])
  self.assertNotIn("PlayerPrefs.DeleteAll",s)
if __name__=="__main__":unittest.main()
