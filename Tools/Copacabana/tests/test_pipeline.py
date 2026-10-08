import json
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import pipeline


class RealCopacabanaTests(unittest.TestCase):
    def setUp(self):
        self.frame = pipeline.Frame()

    def test_exact_playable_area(self):
        self.assertEqual(self.frame.roi.area, 2_000_000)
        self.assertEqual(self.frame.roi.bounds, (-1000, -500, 1000, 500))

    def test_avenue_reference_is_inside_roi(self):
        lon, lat = self.frame.config["avenue_reference_lonlat"]
        local = self.frame.to_local(lon, lat)
        self.assertAlmostEqual(local[0], 0, delta=1)
        self.assertAlmostEqual(local[1], -300, delta=1)
        self.assertTrue(self.frame.roi.contains(pipeline.Point(local)))

    def test_geographic_roundtrip(self):
        for x, y in ((-950, -450), (0, 0), (999, 499)):
            lon, lat = self.frame.to_lonlat(x, y)
            actual_x, actual_y = self.frame.to_local(lon, lat)
            self.assertAlmostEqual(actual_x, x, delta=0.002)
            self.assertAlmostEqual(actual_y, y, delta=0.002)

    def test_height_is_identified_as_osm_or_estimate(self):
        self.assertEqual(pipeline.height_info({"height": "28 m"}),
                         (28., "OSM_height"))
        self.assertEqual(pipeline.height_info({"building:levels": "10"}),
                         (30., "OSM_levels_estimated_3m_each"))
        self.assertEqual(pipeline.height_info({}),
                         (18., "visualization_estimate_NOT_actual"))

    def test_fake_data_not_substituted_when_osm_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                pipeline.build(Path(tmp), require_real_density=False)

    def test_real_geometries_clipped_to_roi_and_keep_original_id(self):
        root = ET.Element("osm", version="0.6")
        coords = [(-50, -50), (50, -50), (50, 50), (-50, 50)]
        for i, (x, y) in enumerate(coords, 1):
            lon, lat = self.frame.to_lonlat(x, y)
            ET.SubElement(root, "node", id=str(i), lon=str(lon), lat=str(lat))
        building = ET.SubElement(root, "way", id="991")
        for i in (1, 2, 3, 4, 1):
            ET.SubElement(building, "nd", ref=str(i))
        ET.SubElement(building, "tag", k="building", v="apartments")
        street = ET.SubElement(root, "way", id="992")
        for i in (1, 2):
            ET.SubElement(street, "nd", ref=str(i))
        ET.SubElement(street, "tag", k="highway", v="residential")
        ET.SubElement(street, "tag", k="name", v="Rua de Teste")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.osm"
            path.write_bytes(ET.tostring(root))
            features, dropped = pipeline.parse_osm(path, self.frame)
            self.assertEqual(len(features), 2)
            self.assertEqual({f["source_id"] for f in features},
                             {"way/991", "way/992"})
            self.assertTrue(all(self.frame.roi.covers(f["geometry"])
                                for f in features))
            self.assertAlmostEqual(features[0]["geometry"].area, 10_000,
                                   delta=0.1)
            self.assertEqual(sum(dropped.values()), 0)


if __name__ == "__main__":
    unittest.main()
