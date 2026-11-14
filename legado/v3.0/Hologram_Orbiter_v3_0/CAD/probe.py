#!/usr/bin/env python3
"""Sondagem geométrica de malhas trianguladas por traçado de raios.

Independe do Blender: só NumPy. É usado pelo gerador (dentro do Blender, que
traz NumPy) para medir critérios de aceitação direto na malha, e por
``scripts/validate_stl.py`` para o teste de enrolamento por raios.

Conceito. Um raio que atravessa um sólido bem formado alterna entre fora
(enrolamento 0) e dentro (enrolamento +1). Enrolamento −1 é uma casca
invertida; +2 é material duplicado. Nenhum dos dois aparece em checagem de
arestas (watertight), mas os dois imprimem errado. Foi assim que os furos M3
do painel v3.0 passaram por três validadores com um pino sólido dentro.

Cuidado numérico. Um raio que passa exatamente sobre uma aresta compartilhada
por dois triângulos é contado duas vezes. Duas defesas: as grades de varredura
usam deslocamentos irracionais (razão de ouro) para não cair em arestas de
caixas alinhadas, e interseções no mesmo t vindas de triângulos adjacentes
são fundidas numa só.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

import numpy as np

EPS = 1e-9
SAME_T = 1e-6
PHI_A = 0.3819660112501051  # 2 - φ
PHI_B = 0.6180339887498949  # φ - 1


def read_binary_stl(path: Path) -> np.ndarray:
    raw = Path(path).read_bytes()
    if len(raw) < 84:
        raise ValueError("arquivo curto demais para STL binário")
    count = struct.unpack_from("<I", raw, 80)[0]
    if len(raw) != 84 + count * 50:
        raise ValueError(f"STL não binário ou truncado: {len(raw)} bytes")
    records = np.frombuffer(raw, dtype=np.uint8, offset=84).reshape(count, 50)
    return records[:, 12:48].copy().view("<f4").reshape(count, 3, 3).astype(np.float64)


@dataclass
class Segment:
    """Trecho de um raio entre duas interseções consecutivas."""

    t0: float
    t1: float
    winding: int

    @property
    def length(self) -> float:
        return self.t1 - self.t0


def _vertex_keys(triangles: np.ndarray, tolerance: float = 1e-5) -> np.ndarray:
    return np.rint(triangles / tolerance).astype(np.int64)


class MeshProbe:
    """Traçador de raios sobre uma sopa de triângulos (N, 3, 3), em mm."""

    def __init__(self, triangles: np.ndarray):
        self.tri = np.asarray(triangles, dtype=np.float64)
        self.v0 = self.tri[:, 0]
        self.e1 = self.tri[:, 1] - self.v0
        self.e2 = self.tri[:, 2] - self.v0
        self.normals = np.cross(self.e1, self.e2)
        self.lo = self.tri.min(axis=(0, 1))
        self.hi = self.tri.max(axis=(0, 1))
        self._keys = _vertex_keys(self.tri)

    # -- interseções -------------------------------------------------------
    def hits(self, origin, direction) -> list[tuple[float, int, int]]:
        """Interseções (t, sinal, índice do triângulo) do raio, ordenadas em t.

        sinal = +1 ao entrar no sólido (normal contra o raio), −1 ao sair.
        Möller–Trumbore vetorizado sobre todos os triângulos.
        """
        o = np.asarray(origin, dtype=np.float64)
        d = np.asarray(direction, dtype=np.float64)
        d = d / np.linalg.norm(d)
        pvec = np.cross(d, self.e2)
        det = np.einsum("ij,ij->i", self.e1, pvec)
        ok = np.abs(det) > EPS
        inv = np.zeros_like(det)
        inv[ok] = 1.0 / det[ok]
        tvec = o - self.v0
        u = np.einsum("ij,ij->i", tvec, pvec) * inv
        qvec = np.cross(tvec, self.e1)
        v = np.einsum("j,ij->i", d, qvec) * inv
        t = np.einsum("ij,ij->i", self.e2, qvec) * inv
        mask = ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1.0 + 1e-9) & (t > 1e-7)
        if not mask.any():
            return []
        idx = np.nonzero(mask)[0]
        signs = np.where(np.einsum("j,ij->i", d, self.normals[idx]) < 0.0, 1, -1)
        order = np.argsort(t[idx])
        return [(float(t[idx][k]), int(signs[k]), int(idx[k])) for k in order]

    def _adjacent(self, a: int, b: int) -> bool:
        ka = {tuple(k) for k in self._keys[a]}
        kb = {tuple(k) for k in self._keys[b]}
        return len(ka & kb) >= 2

    def segments(self, origin, direction, t_max: float) -> list[Segment]:
        """Divide o raio [0, t_max] em trechos com enrolamento constante."""
        return [s for s, _, _ in self._segments_with_faces(origin, direction, t_max)]

    def _segments_with_faces(self, origin, direction, t_max: float) -> list[tuple[Segment, int | None, int | None]]:
        """Como ``segments``, devolvendo também os triângulos de entrada e saída."""
        out: list[tuple[Segment, int | None, int | None]] = []
        winding = 0
        t_prev = 0.0
        tri_prev: int | None = None
        for t, sign, tri in self._dedupe_with_faces(self.hits(origin, direction)):
            if t > t_max:
                break
            if t - t_prev > EPS:
                out.append((Segment(t_prev, t, winding), tri_prev, tri))
            winding += sign
            t_prev = t
            tri_prev = tri
        if t_max - t_prev > EPS:
            out.append((Segment(t_prev, t_max, winding), tri_prev, None))
        return out

    def _dedupe_with_faces(self, hits: list[tuple[float, int, int]]) -> list[tuple[float, int, int]]:
        out: list[tuple[float, int, int]] = []
        for t, s, i in hits:
            merged = False
            for k in range(len(out) - 1, -1, -1):
                t2, s2, i2 = out[k]
                if t - t2 > SAME_T:
                    break
                if s2 == s and self._adjacent(i, i2):
                    merged = True
                    break
            if not merged:
                out.append((t, s, i))
        return out

    def _is_membrane(self, tri_in: int | None, tri_out: int | None) -> bool:
        """Trecho fino é membrana só se as faces de entrada e saída forem
        (anti)paralelas. Um raio que roça uma aresta viva (bordo de fuga do
        aerofólio, canto da cunha) também dá um trecho fino, mas com faces em
        ângulo — isso é geometria legítima, não defeito."""
        if tri_in is None or tri_out is None:
            return False
        n1 = self.normals[tri_in]
        n2 = self.normals[tri_out]
        denom = np.linalg.norm(n1) * np.linalg.norm(n2)
        if denom < EPS:
            return False
        return abs(float(np.dot(n1, n2)) / denom) > 0.98

    # -- medições de conveniência -----------------------------------------
    def solid_runs(self, origin, direction, t_max: float) -> list[tuple[float, float]]:
        """Intervalos [t0, t1] em que o raio está dentro de material (enrolamento ≥ 1)."""
        runs: list[tuple[float, float]] = []
        for s in self.segments(origin, direction, t_max):
            if s.winding >= 1:
                if runs and abs(runs[-1][1] - s.t0) < EPS:
                    runs[-1] = (runs[-1][0], s.t1)
                else:
                    runs.append((s.t0, s.t1))
        return runs

    def is_void(self, origin, direction, t_max: float) -> bool:
        return all(s.winding == 0 for s in self.segments(origin, direction, t_max))

    def grid_scan(self, axis: int, pitch: float, min_thickness: float = 0.02, margin: float = 0.5) -> dict:
        """Varre a malha com raios paralelos a um eixo numa grade regular.

        Devolve contagens e exemplos de trechos com enrolamento fora de {0, 1}
        ou com espessura de material menor que ``min_thickness`` (membrana).
        """
        axes = [a for a in range(3) if a != axis]
        lo = self.lo - margin
        hi = self.hi + margin
        starts_a = np.arange(lo[axes[0]] + pitch * PHI_A, hi[axes[0]], pitch)
        starts_b = np.arange(lo[axes[1]] + pitch * PHI_B, hi[axes[1]], pitch)
        direction = np.zeros(3)
        direction[axis] = 1.0
        t_max = float(hi[axis] - lo[axis])
        bad = 0
        thin = 0
        rays = 0
        examples: list[dict] = []
        for a in starts_a:
            for b in starts_b:
                origin = np.zeros(3)
                origin[axes[0]] = a
                origin[axes[1]] = b
                origin[axis] = lo[axis]
                rays += 1
                for s, tri_in, tri_out in self._segments_with_faces(origin, direction, t_max):
                    fault = None
                    if s.winding not in (0, 1):
                        bad += 1
                        fault = f"enrolamento {s.winding}"
                    elif s.winding == 1 and s.length < min_thickness and self._is_membrane(tri_in, tri_out):
                        thin += 1
                        fault = f"lâmina de {s.length:.4f} mm"
                    if fault and len(examples) < 12:
                        p0 = origin + direction * s.t0
                        p1 = origin + direction * s.t1
                        examples.append(
                            {
                                "fault": fault,
                                "from": [round(float(v), 3) for v in p0],
                                "to": [round(float(v), 3) for v in p1],
                            }
                        )
        return {
            "axis": "xyz"[axis],
            "pitch_mm": pitch,
            "rays": rays,
            "bad_winding_segments": bad,
            "thin_solid_segments": thin,
            "examples": examples,
        }

    def full_scan(self, pitch: float, min_thickness: float = 0.02) -> dict:
        """Varredura nos três eixos; resumo pronto para relatório."""
        per_axis = [self.grid_scan(axis, pitch, min_thickness) for axis in range(3)]
        return {
            "pitch_mm": pitch,
            "rays": sum(r["rays"] for r in per_axis),
            "bad_winding_segments": sum(r["bad_winding_segments"] for r in per_axis),
            "thin_solid_segments": sum(r["thin_solid_segments"] for r in per_axis),
            "examples": [e for r in per_axis for e in r["examples"]][:12],
        }


def coincident_opposite_faces(triangles: np.ndarray, tolerance: float = 1e-5) -> int:
    """Pares de triângulos com os mesmos três vértices e orientação oposta.

    É a assinatura de uma membrana de espessura zero deixada por dois
    cortadores tangentes. Só apanha coincidência exata de vértices; lâminas
    finas com triangulação diferente são apanhadas pelo ``grid_scan``.
    """
    keys: dict[tuple, list[int]] = {}
    quant = _vertex_keys(np.asarray(triangles), tolerance)
    for i in range(len(quant)):
        k = tuple(sorted(tuple(v) for v in quant[i]))
        keys.setdefault(k, []).append(i)
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    pairs = 0
    for ids in keys.values():
        if len(ids) < 2:
            continue
        for a in range(len(ids)):
            for b in range(a + 1, len(ids)):
                if np.dot(normals[ids[a]], normals[ids[b]]) < 0:
                    pairs += 1
    return pairs


def probe_from_stl(path: Path) -> MeshProbe:
    return MeshProbe(read_binary_stl(path))
