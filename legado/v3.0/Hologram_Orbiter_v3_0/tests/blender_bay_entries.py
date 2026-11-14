"""Run with: blender -b --python-exit-code 1 --python tests/blender_bay_entries.py

Rebuilds the spider with each old defect independently to prove the functional
mesh checks fail, even when the other half of the correction is present.
"""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "CAD"))
import generate as cad
from spider_checks import measure_bay_entries


class BayEntryGeometryTests(unittest.TestCase):
    def test_fixed_and_regressed_geometry(self):
        original = deepcopy(cad.P)
        try:
            for root, cut, roots_clear, windows_clear in (
                (39.0, 37.0, True, True),
                (38.0, 37.0, False, True),
                (39.0, 38.5, True, False),
                (38.0, 38.5, False, False),
            ):
                with self.subTest(root=root, cut=cut):
                    cad.clear_scene()
                    # Deliberately bypass parameter guards to test actual solids.
                    cad.P = deepcopy(original)
                    cad.P["spider"]["arm"]["root_radius"] = root
                    cad.P["spider"]["wire_route"]["bay_window_radial"][0] = cut
                    spider = cad.build_spider()
                    cad.apply_location(spider)
                    cad.cleanup_mesh(spider)
                    measured = measure_bay_entries(cad.triangles_of(spider), cad.P)
                    self.assertEqual(measured["roots_clear"], roots_clear, measured)
                    self.assertEqual(measured["windows_clear"], windows_clear, measured)
                    for arm in measured["arms"]:
                        self.assertEqual(arm["root_blocked_rays"] == 0, roots_clear)
                        self.assertEqual(arm["window_blocked_rays"] == 0, windows_clear)
        finally:
            cad.P = original


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BayEntryGeometryTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("Regressão na geometria das entradas de fios")
