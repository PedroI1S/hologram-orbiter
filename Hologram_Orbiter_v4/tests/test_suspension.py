"""Checks of the Hologram Orbiter v4 suspension estimates against closed-form solutions."""
import json
import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CAD"))
from physics import arm_root_estimate, section_cut, suspension_estimate


def box(x, y, z):
    """Twelve outward-facing triangles of an axis-aligned box."""
    v = np.array([[i, j, k] for i in x for j in y for k in z], dtype=float)
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return np.array([[v[a], v[b], v[c]] for q in quads for a, b, c in ((q[0], q[1], q[2]), (q[0], q[2], q[3]))])


class SuspensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = json.loads((ROOT / "CAD/parameters.json").read_text())

    def test_section_cut_of_a_box_matches_bh3_over_12(self):
        # 11 wide (y) by 6 tall (z), cut across x.
        s = section_cut(box((40, 60), (-5.5, 5.5), (1, 7)), 0, 50.3)
        self.assertAlmostEqual(s["area_mm2"], 66)
        self.assertAlmostEqual(s["Ixx_mm4"], 11*6**3/12)
        self.assertAlmostEqual(s["Iyy_mm4"], 6*11**3/12)
        self.assertAlmostEqual(s["centroid_y_mm"], 4)

    def test_arm_root_stress_is_moment_over_section_modulus(self):
        p = json.loads(json.dumps(self.p))
        result = arm_root_estimate(p, box((30, 120), (-5.5, 5.5), (0, 6)), 47.5, (10.,))
        self.assertAlmostEqual(result["section_modulus_vertical_mm3"], 11*6**2/6)
        omega = p["operating_point"]["rpm"]*2*math.pi/60
        force = p["panel"]["mass_limit_assembled_g"]/1000*omega**2*0.1
        moment = force*math.sin(math.radians(10))*(100-47.5)
        self.assertAlmostEqual(result["tilt_cases"][0]["max_bending_stress_mpa"], moment/66, places=6)

    def test_translation_frequency_matches_hand_formula(self):
        rod = self.p["base_tower"]["suspension"]["rod"]
        est = suspension_estimate(self.p, 345., 489., 40., 186.)
        side = rod["side"]
        soft = next(v for v in est["variants"] if v["rod_side_mm"] == side)
        mass = est["moving_mass_kg"]
        elastic = 8*12*rod["modulus_mpa"]*(side**4/12)/(rod["free_length"]-rod["blend_length"])**3
        gravity = 1.2*mass*9.80665/rod["free_length"]
        self.assertAlmostEqual(soft["lateral_stiffness_n_per_mm"], elastic+gravity)
        self.assertAlmostEqual(soft["translation_frequency_hz"],
                               math.sqrt((elastic+gravity)*1000/mass)/(2*math.pi))
        self.assertAlmostEqual(soft["rod_bending_stress_at_stop_mpa"],
                               3*rod["modulus_mpa"]*side*3/(rod["free_length"]-rod["blend_length"])**2)

    def test_polar_inertia_of_a_box_matches_closed_form(self):
        from physics import inertia_about_z
        # 20 x 30 x 40 mm block of density 1 g/cm³ centred on the axis: m (a² + b²) / 12.
        mass = 20*30*40/1000/1000
        expected = mass*((0.020)**2+(0.030)**2)/12
        self.assertAlmostEqual(inertia_about_z(box((-10, 10), (-15, 15), (0, 40)), 1.0), expected)

    def test_softer_rod_lowers_translation_but_keeps_rocking_above_running_speed(self):
        est = suspension_estimate(self.p, 345., 489., 40., 186.)
        soft = est["variants"][0]
        low, high = est["operating_rpm_range"]
        self.assertLess(soft["translation_frequency_hz"], low/120)
        self.assertGreater(soft["rocking_frequency_hz"], 1.3*high/60)
        # Compression-side buckling must sit above a 5 g unbalance at top speed.
        self.assertGreater(soft["rotor_side_force_at_first_buckling_n"], 17.8)


if __name__ == "__main__":
    unittest.main()
