"""Regressões de publicação: executam o pipeline real com um Blender simulado.

O Blender simulado só substitui a geração demorada; validação STL, referência
de corte, staging, promoção e hashes usam os scripts de produção.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parents[2]

FAKE_BLENDER = r'''#!/usr/bin/env python3
import json, os, struct, sys
from pathlib import Path
argv=sys.argv[1:]
assert argv[argv.index('--python-exit-code')+1]=='1'
if os.environ.get('BUILD_TEST_FAIL')=='python':
    print('RuntimeError: simulated CAD exception',file=sys.stderr)
    sys.exit(1)
script=Path(argv[argv.index('--python')+1]).name
args=argv[argv.index('--')+1:]
def value(flag): return Path(args[args.index(flag)+1])
out=value('--output-dir'); out.mkdir(parents=True,exist_ok=True)
if script=='render_views.py':
    if os.environ.get('BUILD_TEST_FAIL')=='render': sys.exit(1)
    (out/'aranha_topo.png').write_bytes(b'new-detail-preview')
    sys.exit(0)
reports=value('--report-dir'); reports.mkdir(parents=True,exist_ok=True)
par=json.loads(value('--parameters').read_text())
stl=out/'stl';stl.mkdir()
names=['01_aranha_ABS.stl','02_painel_LED_ABS_1x.stl','02_painel_LED_ABS_3x_mesma_mesa.stl',
       '03_tampa_baia_ABS.stl','04_05_base_torre_ABS_integradas.stl','06_suporte_ima_ABS.stl',
       'C01_cupom_junta.stl','C02_cupom_canal_LED.stl','R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl']
if par['containment_cap']['enabled']:names.append('07_tampa_contencao_ABS.stl')
if os.environ.get('BUILD_TEST_FAIL')=='inventory':names.pop()
v=[(0.,0.,0.),(2.,0.,0.),(0.,2.,0.),(0.,0.,2.)]
faces=[(0,2,1),(0,1,3),(0,3,2),(1,2,3)]
for name in names:
    n=3 if '3x_mesma_mesa' in name else 1
    raw=bytearray(b'audit fixture'.ljust(80,b' ')+struct.pack('<I',4*n))
    for k in range(n):
        for f in faces:
            coords=[c for i in f for c in (v[i][0]+4*k,v[i][1],v[i][2])]
            raw.extend(struct.pack('<12fH',0.,0.,0.,*coords,0))
    (stl/name).write_bytes(raw)
(out/'fonte').mkdir();(out/'fonte'/'Hologram_Orbiter_v3_0.blend').write_bytes(b'new-blend')
if '--no-render' not in args:
    (out/'preview').mkdir();(out/'preview'/'montagem.png').write_bytes(b'new-preview')
passed=os.environ.get('BUILD_TEST_FAIL')!='acceptance'
(reports/'geometry_report.json').write_text(json.dumps({'acceptance':[{'passa':passed}]}))
(reports/'ACEITACAO.md').write_text('generated acceptance')
(reports/'RELATORIO_VALIDACAO.md').write_text('new generated report')
(reports/'FISICA.json').write_text('{"new":true}')
'''


def hashes(directory: Path) -> dict[str, str]:
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orbiter pipeline test ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "package with spaces"
        (self.root / "CAD").mkdir(parents=True)
        shutil.copytree(PACKAGE / "scripts", self.root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("parameters.json", "probe.py"):
            shutil.copyfile(PACKAGE / "CAD" / name, self.root / "CAD" / name)
        (self.root / "CAD" / "generate.py").write_text("# Simulated by fake Blender in this pipeline test.\n")
        self.fake = Path(self.tmp.name) / "fake blender"
        self.fake.write_text(FAKE_BLENDER)
        self.fake.chmod(0o755)
        for name in ("exports", "reports", "fabricacao"):
            (self.root / name).mkdir()
            (self.root / name / "previous.txt").write_text(f"old-{name}")
        (self.root / "reports" / "NOTAS_MANUAIS.md").write_text("manual report must survive\n")
        (self.root / "reports" / "FISICA.json").write_text("{\"old\":true}")
        (self.root / "exports" / "preview").mkdir()
        (self.root / "exports" / "preview" / "montagem.png").write_bytes(b'old-preview')

    def invoke(self, failure: str = "", no_render: bool = True, extra: list[str] | None = None) -> subprocess.CompletedProcess:
        cmd = ["bash", str(self.root / "scripts" / "build.sh"), "--blender", str(self.fake)]
        if no_render:
            cmd.append("--no-render")
        cmd.extend(extra or [])
        return subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "BUILD_TEST_FAIL": failure})

    def assert_previous_survives(self, failure: str, no_render: bool = True) -> None:
        old = {name: hashes(self.root / name) for name in ("exports", "reports", "fabricacao")}
        result = self.invoke(failure, no_render)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(old, {name: hashes(self.root / name) for name in old})
        self.assertFalse(list(self.root.glob(".build-staging-*")))

    def test_python_exception_preserves_all_previous_artifacts(self) -> None:
        self.assert_previous_survives("python")

    def test_failed_acceptance_with_zero_exit_preserves_previous_artifacts(self) -> None:
        self.assert_previous_survives("acceptance")

    def test_missing_stl_preserves_previous_artifacts(self) -> None:
        self.assert_previous_survives("inventory")

    def test_render_failure_preserves_previous_artifacts(self) -> None:
        self.assert_previous_survives("render", no_render=False)

    def test_empty_inventory_is_not_a_success(self) -> None:
        empty = self.root / "empty"
        empty.mkdir()
        report = self.root / "empty-report.json"
        result = subprocess.run([sys.executable, str(self.root / "scripts" / "validate_stl.py"), str(empty),
                                 "--output", str(report)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        data = json.loads(report.read_text())
        self.assertFalse(data["all_pass"])
        self.assertEqual(len(data["inventory"]["missing"]), 9)

    def test_success_propagates_parameters_preserves_manual_and_hashes_outputs(self) -> None:
        p = json.loads((self.root / "CAD" / "parameters.json").read_text())
        p["motor_plate"]["width"] = 62.0
        p["unverified_interfaces"]["motor"]["base_bolt_rectangle_x"] = 18.0
        p["containment_cap"]["enabled"] = True
        custom = Path(self.tmp.name) / "custom parameters.json"
        custom.write_text(json.dumps(p))
        result = self.invoke(extra=["--parameters", str(custom)])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / "reports" / "NOTAS_MANUAIS.md").read_text(), "manual report must survive\n")
        self.assertEqual(json.loads((self.root / "reports" / "FISICA.json").read_text()), {"new": True})
        self.assertEqual((self.root / "reports" / "RELATORIO_VALIDACAO.md").read_text(), "new generated report")
        self.assertFalse((self.root / "exports" / "preview").exists())
        self.assertEqual(len(list((self.root / "exports" / "stl").glob("*.stl"))), 10)
        svg = next((self.root / "fabricacao").glob("*.svg")).read_text()
        self.assertIn('width="62.0"', svg)
        self.assertIn('18 × 19', svg)
        manifest = json.loads((self.root / "reports" / "build_manifest.json").read_text())
        self.assertFalse(manifest["previews_generated"])
        self.assertEqual(manifest["inputs"]["parameters"]["sha256"], hashlib.sha256(custom.read_bytes()).hexdigest())
        for item in manifest["artifacts"]:
            self.assertEqual(item["sha256"], hashlib.sha256((self.root / item["path"]).read_bytes()).hexdigest())

    def test_promotion_rolls_back_if_second_rename_fails(self) -> None:
        spec = importlib.util.spec_from_file_location("orbiter_build_test_module", PACKAGE / "scripts" / "build.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        stage = self.root / "promotion-stage"
        stage.mkdir()
        staged = []
        for name in ("exports", "reports", "fabricacao"):
            source = stage / name
            source.mkdir()
            (source / "new.txt").write_text("new")
            staged.append((source, self.root / name))
        old = {name: hashes(self.root / name) for name in ("exports", "reports", "fabricacao")}
        original_replace = os.replace
        def fail_second(source, destination):
            if Path(source) == stage / "reports":
                raise OSError("simulated publication failure")
            return original_replace(source, destination)
        with patch.object(module.os, "replace", side_effect=fail_second):
            with self.assertRaises(OSError):
                module.promote(staged, stage / "backup")
        self.assertEqual(old, {name: hashes(self.root / name) for name in old})


if __name__ == "__main__":
    unittest.main()
