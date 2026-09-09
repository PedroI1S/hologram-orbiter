#!/usr/bin/env python3
"""Build do pacote em staging, com validação e promoção após o aceite.

--no-render omite todas as prévias; a nova pasta exports não conserva renders
de uma execução anterior. Os relatórios manuais existentes são preservados.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
AUTOMATIC_REPORTS = {"geometry_report.json", "ACEITACAO.md", "stl_validation.json", "build_manifest.json", "FISICA.json", "RELATORIO_VALIDACAO.md"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_hashes(parameters: Path) -> dict:
    paths = [ROOT / "scripts" / "build.sh", *sorted((ROOT / "scripts").glob("*.py")), *sorted((ROOT / "CAD").glob("*.py"))]
    return {
        "parameters": {"path": str(parameters), "sha256": digest(parameters)},
        "code": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in paths],
    }


def resolve_blender(value: str | None) -> str:
    if value:
        found = shutil.which(value)
        if found:
            return str(Path(found).resolve())
        raise ValueError(f"Blender não encontrado ou não executável: {value}")
    found = shutil.which("blender")
    if found:
        return str(Path(found).resolve())
    mac = Path("/Applications/Blender.app/Contents/MacOS/Blender")
    if mac.is_file() and os.access(mac, os.X_OK):
        return str(mac)
    raise ValueError("Blender 5.x não encontrado. Configure BLENDER com o caminho do executável.")


def check_targets(targets: list[Path]) -> None:
    """A promoção usa rename; todos os destinos precisam do mesmo filesystem."""
    for i, target in enumerate(targets):
        if target == ROOT or ROOT.is_relative_to(target):
            raise ValueError(f"O destino não pode substituir o projeto: {target}")
        if target.exists() and not target.is_dir():
            raise ValueError(f"O destino precisa ser um diretório: {target}")
        for other in targets[:i]:
            if target == other or target.is_relative_to(other) or other.is_relative_to(target):
                raise ValueError("Os destinos exports, reports e fabricacao devem ser diretórios distintos, sem aninhamento.")
        ancestor = target.parent
        while not ancestor.exists():
            ancestor = ancestor.parent
        if ancestor.stat().st_dev != ROOT.stat().st_dev:
            raise ValueError(f"O destino precisa estar no mesmo filesystem do projeto: {target}")


def promote(staged: list[tuple[Path, Path]], backup: Path) -> None:
    """Troca diretórios com rollback se uma operação de promoção falhar."""
    backup.mkdir()
    saved: list[tuple[Path, Path]] = []
    published: list[Path] = []
    try:
        for i, (source, target) in enumerate(staged):
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                old = backup / str(i)
                os.replace(target, old)
                saved.append((old, target))
            os.replace(source, target)
            published.append(target)
    except BaseException:
        for target in reversed(published):
            shutil.rmtree(target)
        for old, target in reversed(saved):
            os.replace(old, target)
        raise


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, cwd=ROOT)


def require_reports(report_dir: Path, stl_dir: Path, parameters: dict) -> None:
    """Defesa adicional: um processo que saiu zero ainda precisa ter gerado aceite."""
    from validate_stl import expected_stl_files

    geometry = json.loads((report_dir / "geometry_report.json").read_text(encoding="utf-8"))
    checks = geometry.get("acceptance")
    if not isinstance(checks, list) or not checks or any(c.get("passa") is not True for c in checks):
        raise ValueError("Critérios de aceitação ausentes ou reprovados; artefatos anteriores preservados.")
    validation = json.loads((report_dir / "stl_validation.json").read_text(encoding="utf-8"))
    expected = expected_stl_files(parameters)
    actual = {p.name for p in stl_dir.glob("*.stl")}
    reported = [item["file"] for item in validation.get("files", [])]
    if validation.get("all_pass") is not True or actual != expected or set(reported) != expected or len(reported) != len(expected):
        raise ValueError("Validação STL incompleta ou reprovada; artefatos anteriores preservados.")
    if not (report_dir / "ACEITACAO.md").is_file():
        raise ValueError("O gerador não produziu ACEITACAO.md.")


def build(args: argparse.Namespace) -> None:
    parameters_path = args.parameters.resolve()
    parameters = json.loads(parameters_path.read_text(encoding="utf-8"))
    blender = resolve_blender(args.blender)
    targets = [args.output_dir.resolve(), args.report_dir.resolve(), args.fabrication_dir.resolve()]
    check_targets(targets)
    initial_hashes = input_hashes(parameters_path)
    # Evita builds concorrentes promovendo combinações de execuções distintas.
    import fcntl

    project_key = hashlib.sha256(str(ROOT).encode()).hexdigest()[:20]
    lock_path = Path(tempfile.gettempdir()) / f"hologram-orbiter-build-{project_key}.lock"
    with lock_path.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Já existe um build em execução neste pacote.") from exc
        with tempfile.TemporaryDirectory(prefix=".build-staging-", dir=ROOT) as tmp:
            stage = Path(tmp)
            exports, reports, fabrication = stage / "exports", stage / "reports", stage / "fabricacao"
            for path in (exports, reports, fabrication):
                path.mkdir()
            # Todos os programas recebem a mesma cópia dos parâmetros.
            snapshot = stage / "parameters.json"
            shutil.copyfile(parameters_path, snapshot)
            command = [blender, "-b", "--python-exit-code", "1", "--python", str(ROOT / "CAD" / "generate.py"), "--",
                       "--parameters", str(snapshot), "--output-dir", str(exports), "--report-dir", str(reports)]
            if args.no_render:
                command.append("--no-render")
            run(command)
            run([sys.executable, str(ROOT / "scripts" / "validate_stl.py"), str(exports / "stl"),
                 "--parameters", str(snapshot), "--output", str(reports / "stl_validation.json")])
            require_reports(reports, exports / "stl", parameters)
            run([sys.executable, str(ROOT / "scripts" / "plate_cut_reference.py"), "--parameters", str(snapshot),
                 "--output-dir", str(fabrication)])
            if not args.no_render:
                run([blender, "-b", "--python-exit-code", "1", "--python", str(ROOT / "scripts" / "render_views.py"), "--",
                     "--stl-dir", str(exports / "stl"), "--output-dir", str(exports / "preview")])
            elif (exports / "preview").exists():
                shutil.rmtree(exports / "preview")
            if not (exports / "fonte" / "Hologram_Orbiter_v3_0.blend").is_file():
                raise ValueError("O gerador não produziu a montagem .blend.")
            if not any(fabrication.glob("*.dxf")) or not any(fabrication.glob("*.svg")):
                raise ValueError("Referências de corte DXF/SVG ausentes.")
            if not args.no_render and not (exports / "preview" / "montagem.png").is_file():
                raise ValueError("Prévia da montagem ausente.")
            if input_hashes(parameters_path) != initial_hashes or digest(snapshot) != initial_hashes["parameters"]["sha256"]:
                raise ValueError("Parâmetros ou código mudaram durante o build; execute novamente.")
            preserved = []
            if targets[1].exists():
                for source in targets[1].iterdir():
                    if source.name in AUTOMATIC_REPORTS or (reports / source.name).exists():
                        continue
                    destination = reports / source.name
                    if source.is_dir():
                        shutil.copytree(source, destination)
                    else:
                        shutil.copy2(source, destination)
                    preserved.append(source.name)
            artifacts = []
            for name, directory in (("exports", exports), ("reports", reports), ("fabricacao", fabrication)):
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        artifacts.append({"path": f"{name}/{path.relative_to(directory)}", "sha256": digest(path), "bytes": path.stat().st_size,
                                          "preserved": name == "reports" and path.relative_to(reports).parts[0] in preserved})
            manifest = {
                "schema_version": 1, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "inputs": initial_hashes, "blender_executable": blender,
                "previews_generated": not args.no_render, "artifacts": artifacts,
                "note": "Hashes dos artefatos desta execução, exceto o próprio manifesto; relatórios manuais preservados são identificados.",
            }
            (reports / "build_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            promote(list(zip((exports, reports, fabrication), targets)), stage / "backup")
    print("Build validado e publicado: " + ", ".join(map(str, targets)))
    if args.no_render:
        print("Sem renders nesta execução; prévias anteriores removidas do pacote publicado.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=ROOT / "CAD" / "parameters.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "exports")
    parser.add_argument("--report-dir", type=Path, default=ROOT / "reports")
    parser.add_argument("--fabrication-dir", type=Path, default=ROOT / "fabricacao")
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--blender", default=os.environ.get("BLENDER"))
    args = parser.parse_args()
    try:
        build(args)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"Build falhou: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
