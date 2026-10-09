"""Protect saved gameplay and reject fictional/unverified OSM anchor placement."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from build_r12_anchor_inventory import (
    GAME_SITE,OUTPUT,REPORT,R4,build,promenade_z
)
class R12AnchorInventoryTests(unittest.TestCase):
    def setUp(self):
        self.site=json.loads(GAME_SITE.read_text(encoding="utf-8"))
        self.plan,self.qa=build()
    def test_inventory_exact_gameplay_semantics(self):
        self.assertEqual(len(self.plan["anchors"]),10)
        self.assertEqual(self.qa["parcels_count"],8)
        anchors={a["id"]:a for a in self.plan["anchors"]}
        self.assertEqual(anchors["HOME_DOOR"]["legacy"],{"x":330.0,"z":338.5})
        x=float(self.site["stall"]["x"])
        self.assertAlmostEqual(anchors["STALL_PROMENADE"]["legacy"]["z"],
            promenade_z(self.site,x),places=6)
        self.assertEqual(anchors["STALL_PROMENADE"]["legacy"]["x"],450.0)
        for parcel in self.site["parcels"]:
            v=anchors["PARCEL_"+parcel["id"]]["legacy"]
            self.assertAlmostEqual(v["x"],parcel["x"]+parcel["width"]/2)
            self.assertAlmostEqual(v["z"],parcel["z"]+parcel["depth"]/2)
        self.assertEqual(sorted(anchors),sorted(set(anchors)))
    def test_fail_closed_and_source_integrity(self):
        self.assertFalse(self.plan["approved"])
        self.assertFalse(self.plan["migration_enabled"])
        self.assertEqual(self.plan["status"],
            "NOT_APPROVED_MUST_KEEP_LEGACY_GAMEPLAY_WORLD")
        self.assertEqual(self.plan["transform_policy"],
            "ONE_TO_ONE_METRES_RIGID_ROTATION_TRANSLATION_ONLY_NO_RESIZE")
        self.assertTrue(all(a["target"] is None for a in self.plan["anchors"]))
        self.assertEqual(self.plan["source_site_sha256"],
            hashlib.sha256(GAME_SITE.read_bytes()).hexdigest())
        self.assertEqual(self.plan["source_frame_sha256"],
            hashlib.sha256(R4.read_bytes()).hexdigest())
        self.assertEqual(self.plan["r12_geo"]["crs"],"EPSG:32723")
    def test_manifest_is_reproducible(self):
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")),self.plan)
        self.assertEqual(json.loads(REPORT.read_text(encoding="utf-8")),self.qa)
        self.assertFalse(self.qa["ready_to_switch"])
    def test_site_geometry_drift_is_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            altered=copy.deepcopy(self.site)
            altered["size"]["x"]=2000.0
            p=Path(tmp)/"drift.json"
            p.write_text(json.dumps(altered),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"LEGACY_SITE_FRAME_CHANGED"):
                build(site_path=p)
            altered=self.site.copy()
            altered["parcels"]=self.site["parcels"][:-1]
            p.write_text(json.dumps(altered),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"REQUIRED_10_GAMEPLAY_ANCHORS"):
                build(site_path=p)
    def test_no_made_up_geographic_targets(self):
        for record in self.plan["anchors"]:
            self.assertIn(record["role"],("player_spawn","shop","parcel"))
            self.assertIsNone(record["target"])
            self.assertEqual(record["status"],"GEOGRAPHIC_PLACEMENT_UNVERIFIED")
        self.assertNotIn("estimatedLatLon",self.plan)
if __name__=="__main__":unittest.main()
