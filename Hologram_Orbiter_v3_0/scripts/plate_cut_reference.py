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


def washer_blank() -> tuple[float, float, float, float] | None:
    """Disco da arruela do eixo (Ø externo, furo), ao lado da chapa, na mesma folha."""
    q = P["motor_plate"]
    wb = q.get("washer_blank", {})
    if not wb.get("enabled", False):
        return None
    cx = q["width"] / 2 + 10.0 + wb["outer_diameter"] / 2
    return (cx, 0.0, wb["outer_diameter"], wb["hole_diameter"])


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
    wb = washer_blank()
    if wb:
        cx, cy, od, hole = wb
        lines += ["0", "CIRCLE", "8", "CONTORNO", "10", f"{cx:.3f}", "20", f"{cy:.3f}", "30", "0", "40", f"{od / 2:.3f}"]
        lines += ["0", "CIRCLE", "8", "FUROS", "10", f"{cx:.3f}", "20", f"{cy:.3f}", "30", "0", "40", f"{hole / 2:.3f}"]
    lines += ["0", "ENDSEC", "0", "EOF"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(path: Path) -> None:
    q = P["motor_plate"]
    w, d = q["width"], q["depth"]
    margin = 10.0
    wb = washer_blank()
    extra = (10.0 + wb[2] + 5.0) if wb else 0.0
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w + 2 * margin + extra}mm" height="{d + 2 * margin + 18}mm" '
        f'viewBox="{-w / 2 - margin} {-d / 2 - margin} {w + 2 * margin + extra} {d + 2 * margin + 18}">',
        f'<rect x="{-w / 2}" y="{-d / 2}" width="{w}" height="{d}" fill="none" stroke="#000" stroke-width="0.3"/>',
    ]
    for x, y, dia, label in holes():
        parts.append(f'<circle cx="{x:.3f}" cy="{-y:.3f}" r="{dia / 2:.3f}" fill="none" stroke="#000" stroke-width="0.3"><title>{label} Ø{dia}</title></circle>')
    if wb:
        cx, cy, od, hole = wb
        parts.append(f'<circle cx="{cx:.3f}" cy="{-cy:.3f}" r="{od / 2:.3f}" fill="none" stroke="#000" stroke-width="0.3"><title>arruela do eixo Ø{od}</title></circle>')
        parts.append(f'<circle cx="{cx:.3f}" cy="{-cy:.3f}" r="{hole / 2:.3f}" fill="none" stroke="#000" stroke-width="0.3"><title>furo Ø{hole} (passa pelo colar Ø8 do eixo)</title></circle>')
        parts.append(f'<text x="{cx - od / 2:.3f}" y="{od / 2 + 5:.3f}" font-size="2.4" font-family="sans-serif">arruela Ø{od} × Ø{hole}</text>')
    parts.append(f'<text x="{-w / 2}" y="{d / 2 + 6}" font-size="3.2" font-family="sans-serif">R01 suporte do motor — alumínio {q["thickness"]} mm — escala 1:1 — NÃO IMPRIMIR EM 3D</text>')
    parts.append(f'<text x="{-w / 2}" y="{d / 2 + 10.5}" font-size="2.6" font-family="sans-serif">4× Ø{P["unverified_interfaces"]["motor"]["base_bolt_hole_diameter"]} motor (16 × 19) · 4× Ø{P["base_tower"]["flange_hole_diameter"]} flange PCD {P["base_tower"]["flange_hole_pcd"]} · centro Ø{q["center_clearance_diameter"]} (verificar)</text>')
    if wb:
        parts.append(f'<text x="{-w / 2}" y="{d / 2 + 14.5}" font-size="2.6" font-family="sans-serif">Disco à direita: arruela do eixo na mesma chapa — o furo Ø{wb[3]} passa pelo colar Ø8; uma arruela M6 não passa.</text>')
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
