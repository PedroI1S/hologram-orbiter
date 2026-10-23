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

    def test_drive_energy_balance_and_kick_start(self):
        drive = self.result["drive"]
        self.assertAlmostEqual(drive["inertia_g_m2"], 1.55)
        self.assertAlmostEqual(drive["steady"]["input_power_w"], 16.6314054, places=5)
        source = {s["voltage_v"]: s["current_a"] for s in drive["steady"]["source_currents"]}
        self.assertAlmostEqual(source[10], 1.6631405, places=5)
        self.assertAlmostEqual(source[12], 1.3859504, places=5)
        start = drive["startup_kick"]
        # 30 A supply never limits: stalled at 1400 µs, I = duty*V/R.
        stall = {case["source_voltage_v"]: case for case in start["stall_at_kick"]}
        self.assertAlmostEqual(stall[12]["duty"], 252/684)
        self.assertAlmostEqual(stall[10]["phase_current_a"], 16.6706383, places=5)
        self.assertAlmostEqual(stall[12]["phase_current_a"], 20.0047660, places=5)
        self.assertAlmostEqual(stall[12]["torque_nm"], .2076428, places=6)
        self.assertFalse(any(case["supply_limiting"] for case in stall.values()))
        self.assertAlmostEqual(start["phase_ceiling"]["input_power_w"], 32.1012357, places=5)
        runs = {case["source_voltage_v"]: case for case in start["trajectories"]}
        self.assertAlmostEqual(runs[10]["peak_rpm"], 1692, delta=1)
        self.assertAlmostEqual(runs[12]["peak_rpm"], 1964, delta=1)
        self.assertAlmostEqual(runs[10]["target_rpm"], 590.9, delta=.1)
        self.assertAlmostEqual(runs[12]["target_rpm"], 691.0, delta=.1)
        self.assertTrue(runs[12]["exceeds_operating_rpm"])
        self.assertFalse(runs[10]["exceeds_operating_rpm"])
        for v, case in runs.items():
            self.assertAlmostEqual(case["peak_phase_current_a"], stall[v]["phase_current_a"])
            self.assertTrue(case["exceeds_phase_ceiling"] and case["exceeds_start_power_ceiling"])
        clamp = drive["shaft_clamp"]
        self.assertAlmostEqual(clamp["preload_estimate_n"], 500)
        self.assertAlmostEqual(clamp["steady"]["required_clamp_force_n"], 24.4663655, places=5)
        self.assertAlmostEqual(clamp["phase_ceiling"]["required_clamp_force_n"], 39.5416008, places=5)
        self.assertAlmostEqual(drive["stretch"]["steady_motor_temperature_c"],
                               56.3368827, places=5)
        self.assertFalse(drive["stretch"]["released_for_operation"])

    def test_current_limited_supply_sags_the_bus(self):
        parameters = json.loads(json.dumps(self.parameters))
        parameters["physics_assumptions"]["source_current_limit_a"] = 3.
        start = calculate_physics(parameters)["drive"]["startup_kick"]
        # At the limit I = 0.95*3/duty and bus = R*I/duty, whatever the setpoint.
        for stall in start["stall_at_kick"]:
            self.assertTrue(stall["supply_limiting"])
            self.assertAlmostEqual(stall["phase_current_a"], 7.7357143, places=5)
            self.assertAlmostEqual(stall["bus_voltage_v"], 4.6403235, places=5)
        runs = {case["source_voltage_v"]: case for case in start["trajectories"]}
        self.assertAlmostEqual(runs[12]["peak_rpm"], 1624, delta=1)
        # Under the limit the falling duty raises the phase current above 8 A, and
        # leaving the limit the supply passes through V*3 A.
        self.assertAlmostEqual(runs[12]["peak_input_power_w"], 36, delta=.01)
        self.assertTrue(all(c["exceeds_phase_ceiling"] for c in runs.values()))


if __name__ == "__main__":
    unittest.main()
