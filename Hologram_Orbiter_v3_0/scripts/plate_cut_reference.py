#!/usr/bin/env python3
"""Gera a referência de corte da chapa do motor (R01) em DXF e SVG.

Lê CAD/parameters.json; não depende do Blender. Unidades em mm.
A chapa é alumínio 2 mm e NÃO deve ser impressa.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P = json.loads((ROOT / "CAD" / "parameters.json").read_text(encoding="utf-8"))


def holes() -> list[tuple[float, float, float, str]]:
    q = P["motor_plate"]
    motor = P["unverified_interfaces"]["motor"]
    bt = P["base_tower"]
    out = []
    hx = motor["base_bolt_rectangle_x"] / 2
    hy = motor["base_bolt_rectangle_y"] / 2
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        out.append((sx * hx, sy * hy, motor["base_bolt_hole_diameter"], "motor M3 (retangulo 16 x 19)"))
    for i in range(4):
        a = math.radians(bt["flange_hole_angle_offset_deg"] + i * 90.0)
        r = bt["flange_hole_pcd"] / 2
        out.append((r * math.cos(a), r * math.sin(a), bt["flange_hole_diameter"], "flange da torre M4 (PCD 40)"))
    out.append((0.0, 0.0, q["center_clearance_diameter"], "alivio central (eixo/fios) - NAO VERIFICADO"))
    return out


def write_dxf(path: Path) -> None:
    q = P["motor_plate"]
    w, d = q["width"], q["depth"]
    corners = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]
    lines = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for i in range(4):
        x0, y0 = corners[i]
        x1, y1 = corners[(i + 1) % 4]
        lines += ["0", "LINE", "8", "CONTORNO", "10", f"{x0:.3f}", "20", f"{y0:.3f}", "30", "0", "11", f"{x1:.3f}", "21", f"{y1:.3f}", "31", "0"]
    for x, y, dia, _ in holes():
        lines += ["0", "CIRCLE", "8", "FUROS", "10", f"{x:.3f}", "20", f"{y:.3f}", "30", "0", "40", f"{dia / 2:.3f}"]
    lines += ["0", "ENDSEC", "0", "EOF"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(path: Path) -> None:
    q = P["motor_plate"]
    w, d = q["width"], q["depth"]
    margin = 10.0
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w + 2 * margin}mm" height="{d + 2 * margin + 14}mm" '
        f'viewBox="{-w / 2 - margin} {-d / 2 - margin} {w + 2 * margin} {d + 2 * margin + 14}">',
        f'<rect x="{-w / 2}" y="{-d / 2}" width="{w}" height="{d}" fill="none" stroke="#000" stroke-width="0.3"/>',
    ]
    for x, y, dia, label in holes():
        parts.append(f'<circle cx="{x:.3f}" cy="{-y:.3f}" r="{dia / 2:.3f}" fill="none" stroke="#000" stroke-width="0.3"><title>{label} Ø{dia}</title></circle>')
    parts.append(f'<text x="{-w / 2}" y="{d / 2 + 6}" font-size="3.2" font-family="sans-serif">R01 suporte do motor — alumínio {q["thickness"]} mm — escala 1:1 — NÃO IMPRIMIR EM 3D</text>')
    parts.append(f'<text x="{-w / 2}" y="{d / 2 + 10.5}" font-size="2.6" font-family="sans-serif">4× Ø{P["unverified_interfaces"]["motor"]["base_bolt_hole_diameter"]} motor (16 × 19) · 4× Ø{P["base_tower"]["flange_hole_diameter"]} flange PCD {P["base_tower"]["flange_hole_pcd"]} · centro Ø{q["center_clearance_diameter"]} (verificar)</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    out = ROOT / "fabricacao"
    out.mkdir(exist_ok=True)
    write_dxf(out / "R01_suporte_motor_60x60_aluminio_2mm.dxf")
    write_svg(out / "R01_suporte_motor_60x60_aluminio_2mm.svg")
    print("Referência de corte gerada em", out)


if __name__ == "__main__":
    main()
