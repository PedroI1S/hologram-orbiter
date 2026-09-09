"""Regressions for ineffective clearance settings and ignored acceptance limits."""
import ast
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'CAD'))
from parameters import resolve_parameters


class ParameterTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads((ROOT / 'CAD/parameters.json').read_text())

    def test_clearance_changes_socket_width_and_height(self):
        original = resolve_parameters(self.raw)['panel']['boss']
        self.raw['quality']['joint_xy_clearance_each_side'] = .5
        changed = resolve_parameters(self.raw)['panel']['boss']
        self.assertAlmostEqual(changed['socket_width'] - original['socket_width'], .8)
        self.assertAlmostEqual(changed['socket_height'] - original['socket_height'], .8)

    def test_bottom_clearance_tracks_tenon_and_conflicting_legacy_values_fail(self):
        self.raw['quality']['joint_bottom_clearance'] = 1.0
        self.assertEqual(resolve_parameters(self.raw)['panel']['boss']['socket_depth'], 23.0)
        self.raw['panel']['boss']['socket_depth'] = 22.5
        with self.assertRaises(ValueError):
            resolve_parameters(self.raw)

    def test_invalid_dimensions_and_relaxed_safety_limit_are_rejected(self):
        for path, key, value in [('quality', 'joint_xy_clearance_each_side', -1),
                                 ('fdm_rules', 'printer_bed_mm', [300, 0]),
                                 ('panel', 'mass_limit_assembled_g', 60)]:
            p = deepcopy(self.raw)
            p[path][key] = value
            with self.assertRaises(ValueError):
                resolve_parameters(p)

    def acceptance(self, p):
        # Execute the actual function without importing bpy/model construction.
        tree = ast.parse((ROOT / 'CAD/generate.py').read_text())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'acceptance')
        namespace = {'P': resolve_parameters(p)}
        exec(compile(ast.Module(body=[function], type_ignores=[]), 'generate.py', 'exec'), namespace)
        report = json.loads((ROOT / 'reports/geometry_report.json').read_text())
        return namespace['acceptance'](report['derived'], report['geometry'], {})

    def test_smaller_bed_rejects_current_geometry(self):
        self.assertTrue(all(c['passa'] for c in self.acceptance(self.raw)))
        self.raw['fdm_rules']['printer_bed_mm'] = [250, 300]
        failed = [c['criterio'] for c in self.acceptance(self.raw) if not c['passa']]
        self.assertIn('Base + brim cabe na mesa', failed)

    def test_stricter_panel_mass_limit_rejects_current_geometry(self):
        self.raw['panel']['mass_limit_assembled_g'] = 40
        failed = [c['criterio'] for c in self.acceptance(self.raw) if not c['passa']]
        self.assertIn('Subtotal nominal por painel', failed)


if __name__ == '__main__':
    unittest.main()
