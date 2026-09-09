"""Numerical checks of independent engineering calculations and STL cuts."""
import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CAD"))
from physics import calculate_physics, polygon_integrals, _centroidal
from probe import read_binary_stl


class PhysicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parameters = json.loads((ROOT / "CAD/parameters.json").read_text())
        cls.result = calculate_physics(cls.parameters)

    def test_rectangle_known_analytical_solution(self):
        # 8 by 30 rectangle translated to (10, 20); centroidal values invariant.
        p = [[6, 5], [14, 5], [14, 35], [6, 35]]
        s = _centroidal(polygon_integrals(p))
        self.assertAlmostEqual(s["area_mm2"], 240)
        self.assertAlmostEqual(s["centroid_x_mm"], 10)
        self.assertAlmostEqual(s["centroid_y_mm"], 20)
        self.assertAlmostEqual(s["Iyy_mm4"], 30*8**3/12)
        self.assertAlmostEqual(s["Ixx_mm4"], 8*30**3/12)
        self.assertAlmostEqual(s["Ixy_mm4"], 0)
        np.testing.assert_allclose(polygon_integrals(p), polygon_integrals(p[::-1]))

    def test_parameter_section_matches_independent_exported_geometry(self):
        triangles = read_binary_stl(ROOT / "exports/stl/02_painel_LED_ABS_1x.stl")
        # Export y=90° and normalize to bed: (x', y', z')=(z, y, 4-x).
        local = np.stack([4-triangles[:, :, 2], triangles[:, :, 1],
                          triangles[:, :, 0]], axis=-1)
        result = calculate_physics(self.parameters, local)
        self.assertTrue(all(c["matches_parameters"] for c in result["stl_section_checks"]))
        section = result["section"]
        self.assertAlmostEqual(section["Iyy_mm4"], 589.884623, places=5)
        self.assertAlmostEqual(section["I_effective_radial_mm4"], 589.696667, places=5)
        self.assertAlmostEqual(section["centroid_x_mm"], -.530949748, places=7)

    def test_flexure_envelope_and_actual_load_estimate_are_separate(self):
        flex = self.result["flexure"]
        self.assertAlmostEqual(flex["design_centrifugal_force_n"], 158.1110625, places=5)
        cases = flex["envelope_cases"]
        self.assertAlmostEqual(cases[0]["tip_deflection_mm"], 3.8321829, places=5)
        self.assertAlmostEqual(cases[2]["tip_deflection_mm"], 7.7391105, places=5)
        self.assertAlmostEqual(cases[2]["max_bending_stress_mpa"], 28.7879212, places=5)
        self.assertLess(flex["distributed_load_estimate"]["load_n_per_mm"],
                        cases[0]["distributed_load_n_per_mm"])
        self.assertTrue(all(not case["strength_certified"] for case in cases))
        self.assertFalse(self.result["operation_released"])

    def test_drive_energy_balance_and_ramp(self):
        drive = self.result["drive"]
        self.assertAlmostEqual(drive["inertia_g_m2"], 1.55)
        self.assertAlmostEqual(drive["steady"]["input_power_w"], 16.6314054, places=5)
        self.assertAlmostEqual(drive["steady"]["source_current_a"], 2.3759151, places=5)
        ramps = {case["ramp_s"]: case for case in drive["startup"]}
        self.assertAlmostEqual(ramps[12]["phase_current_a"], 7.2956760, places=5)
        self.assertGreater(ramps[8]["phase_current_a"], 8)
        self.assertLess(ramps[12]["phase_current_a"], 8)
        self.assertAlmostEqual(drive["stretch"]["steady_motor_temperature_c"],
                               56.3368827, places=5)
        self.assertFalse(drive["stretch"]["released_for_operation"])


if __name__ == "__main__":
    unittest.main()
