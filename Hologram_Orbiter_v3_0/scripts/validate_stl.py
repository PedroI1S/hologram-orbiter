#!/usr/bin/env python3
"""Validação independente dos STL binários exportados.

Verifica envelope, degeneração, fechamento topológico, volume orientado e —
desde 03/09/2026 — **enrolamento por traçado de raios** e **faces
coincidentes** (06-PENDENCIAS B8). Não depende do Blender: só Python + NumPy.

Por que o teste de raios existe: uma casca invertida (enrolamento −1) tem
todas as arestas com duas faces, volume total positivo e passa em qualquer
checagem topológica; mas o fatiador a imprime como sólido. Foi o caso dos
furos M3 do painel v3.0.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "CAD"))
from probe import MeshProbe, coincident_opposite_faces, read_binary_stl  # noqa: E402


def key(vertex: np.ndarray, tolerance: float = 1e-5) -> tuple[int, int, int]:
    return tuple(np.rint(vertex / tolerance).astype(np.int64).tolist())


def scan_pitch(dimensions: np.ndarray) -> float:
    """Passo da grade: ~120 raios na maior dimensão, nunca abaixo de 0,5 mm."""
    longest = float(dimensions.max())
    return max(0.5, round(longest / 120.0, 2))


def analyse(path: Path) -> dict:
    triangles = read_binary_stl(path)
    flat = triangles.reshape(-1, 3)
    low = flat.min(axis=0)
    high = flat.max(axis=0)
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    double_area = np.linalg.norm(cross, axis=1)
    degenerate = int(np.count_nonzero(double_area < 1e-8))
    signed_volume = float(
        np.einsum(
            "ij,ij->i",
            triangles[:, 0],
            np.cross(triangles[:, 1], triangles[:, 2]),
        ).sum()
        / 6.0
    )

    edge_counts: Counter[tuple[tuple[int, int, int], tuple[int, int, int]]] = Counter()
    vertex_ids: dict[tuple[int, int, int], int] = {}
    adjacency: dict[int, set[int]] = defaultdict(set)
    next_id = 0
    for triangle in triangles:
        keys = [key(v) for v in triangle]
        ids = []
        for vertex_key in keys:
            if vertex_key not in vertex_ids:
                vertex_ids[vertex_key] = next_id
                next_id += 1
            ids.append(vertex_ids[vertex_key])
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edge = tuple(sorted((keys[a], keys[b])))
            edge_counts[edge] += 1
            adjacency[ids[a]].add(ids[b])
            adjacency[ids[b]].add(ids[a])

    bad_edges = sum(1 for count in edge_counts.values() if count != 2)
    unseen = set(range(next_id))
    components = 0
    while unseen:
        components += 1
        start = unseen.pop()
        queue = deque([start])
        while queue:
            current = queue.popleft()
            for neighbour in adjacency[current]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    queue.append(neighbour)

    dims = high - low
    pitch = scan_pitch(dims)
    winding = MeshProbe(triangles).full_scan(pitch)
    coincident = coincident_opposite_faces(triangles)

    return {
        "file": path.name,
        "triangle_count": int(len(triangles)),
        "dimensions_mm": [round(float(v), 4) for v in dims],
        "bounds_min_mm": [round(float(v), 4) for v in low],
        "bounds_max_mm": [round(float(v), 4) for v in high],
        "signed_volume_cm3": round(signed_volume / 1000.0, 4),
        "degenerate_triangles": degenerate,
        "non_two_manifold_edges": int(bad_edges),
        "connected_components": components,
        "watertight": bad_edges == 0 and degenerate == 0,
        "outward_orientation": signed_volume > 0,
        "ray_winding": {
            "pitch_mm": winding["pitch_mm"],
            "rays": winding["rays"],
            "bad_winding_segments": winding["bad_winding_segments"],
            "thin_solid_segments": winding["thin_solid_segments"],
            "examples": winding["examples"],
        },
        "coincident_opposite_face_pairs": int(coincident),
        "winding_clean": winding["bad_winding_segments"] == 0 and winding["thin_solid_segments"] == 0 and coincident == 0,
    }


def passes(result: dict) -> bool:
    return bool(result.get("watertight")) and bool(result.get("outward_orientation", False)) and bool(result.get("winding_clean", False))


def expected_stl_files(parameters: dict) -> set[str]:
    names = {
        "01_aranha_ABS.stl", "02_painel_LED_ABS_1x.stl",
        "02_painel_LED_ABS_3x_mesma_mesa.stl", "03_tampa_baia_ABS.stl",
        "04_05_base_torre_ABS_integradas.stl", "06_suporte_ima_ABS.stl",
        "C01_cupom_junta.stl", "C02_cupom_canal_LED.stl",
        "R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl",
    }
    if parameters["containment_cap"]["enabled"]:
        names.add("07_tampa_contencao_ABS.stl")
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stl_dir", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--parameters", type=Path, default=HERE.parent / "CAD" / "parameters.json")
    args = parser.parse_args()
    parameters = json.loads(args.parameters.read_text(encoding="utf-8"))
    files = sorted(args.stl_dir.glob("*.stl"))
    expected = expected_stl_files(parameters)
    actual = {path.name for path in files}
    missing, unexpected = sorted(expected - actual), sorted(actual - expected)
    results = []
    failed = bool(missing or unexpected)
    if missing:
        print("FALHA Inventário: STL ausentes: " + ", ".join(missing), file=sys.stderr)
    if unexpected:
        print("FALHA Inventário: STL inesperados: " + ", ".join(unexpected), file=sys.stderr)
    for path in files:
        try:
            result = analyse(path)
        except Exception as exc:
            result = {"file": path.name, "error": str(exc), "watertight": False}
        results.append(result)
        expected_components = 3 if path.name == "02_painel_LED_ABS_3x_mesma_mesa.stl" else 1
        result["expected_connected_components"] = expected_components
        result["component_count_ok"] = result.get("connected_components") == expected_components
        ok = passes(result) and result["component_count_ok"]
        if not ok:
            failed = True
        state = "OK" if ok else "FALHA"
        rw = result.get("ray_winding", {})
        print(
            f"{state:5} {path.name}: tri {result.get('triangle_count')}, vol {result.get('signed_volume_cm3')} cm³, "
            f"comp {result.get('connected_components')}, arestas ruins {result.get('non_two_manifold_edges')}, "
            f"enrolamento ruim {rw.get('bad_winding_segments')}, lâminas {rw.get('thin_solid_segments')}, "
            f"faces coincidentes {result.get('coincident_opposite_face_pairs')} ({rw.get('rays')} raios @ {rw.get('pitch_mm')} mm)"
        )
        for example in rw.get("examples", [])[:4]:
            print("      ", example)

    payload = {
        "all_pass": not failed,
        "inventory": {"expected": sorted(expected), "missing": missing, "unexpected": unexpected},
        "files": results,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
