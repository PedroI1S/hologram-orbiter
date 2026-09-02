#!/usr/bin/env python3
"""Validação independente dos STL binários exportados.

Verifica envelope, degeneração, fechamento topológico e volume orientado sem
depender do Blender. Requer somente Python + NumPy.
"""

from __future__ import annotations

import argparse
import json
import struct
from collections import Counter, defaultdict, deque
from pathlib import Path

import numpy as np


def read_binary_stl(path: Path) -> np.ndarray:
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError("arquivo curto demais para STL binário")
    triangle_count = struct.unpack_from("<I", raw, 80)[0]
    expected = 84 + triangle_count * 50
    if len(raw) != expected:
        raise ValueError(
            f"STL não binário ou truncado: {len(raw)} bytes; esperado {expected}"
        )
    records = np.frombuffer(raw, dtype=np.uint8, offset=84).reshape(triangle_count, 50)
    triangles = np.empty((triangle_count, 3, 3), dtype=np.float64)
    for i in range(triangle_count):
        triangles[i] = np.frombuffer(records[i, 12:48].tobytes(), dtype="<f4").reshape(3, 3)
    return triangles


def key(vertex: np.ndarray, tolerance: float = 1e-5) -> tuple[int, int, int]:
    return tuple(np.rint(vertex / tolerance).astype(np.int64).tolist())


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

    return {
        "file": path.name,
        "triangle_count": int(len(triangles)),
        "dimensions_mm": [round(float(v), 4) for v in high - low],
        "bounds_min_mm": [round(float(v), 4) for v in low],
        "bounds_max_mm": [round(float(v), 4) for v in high],
        "signed_volume_cm3": round(signed_volume / 1000.0, 4),
        "degenerate_triangles": degenerate,
        "non_two_manifold_edges": int(bad_edges),
        "connected_components": components,
        "watertight": bad_edges == 0 and degenerate == 0,
        "outward_orientation": signed_volume > 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stl_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    files = sorted(args.stl_dir.glob("*.stl"))
    results = []
    failed = False
    for path in files:
        try:
            result = analyse(path)
        except Exception as exc:
            result = {"file": path.name, "error": str(exc), "watertight": False}
        results.append(result)
        if not result.get("watertight") or not result.get("outward_orientation", False):
            failed = True
        state = "OK" if result.get("watertight") and result.get("outward_orientation") else "FALHA"
        print(f"{state:5} {path.name}: {result}")

    payload = {"all_pass": not failed, "files": results}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
