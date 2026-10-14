#!/usr/bin/env python3
"""Plaquinha impressa que simula a chapa R01 (alumínio 2 mm) para testes em baixa rotação.

    python3 scripts/r01_placa_teste.py            # G-code + STL (chama o Blender para o STL)
    python3 scripts/r01_placa_teste.py --no-stl   # só o G-code
    python3 scripts/r01_placa_teste.py --furo-central 7   # outro alívio central

Lê CAD/parameters.json (chapa, flange, arruela). Diferenças em relação à R01 de alumínio:

- Mesma furação da R01: motor em cruz (diagonais 16 e 19, furos em (±8, 0) e (0, ±9,5)),
  flange M4 em PCD 40 e alívio central Ø8 (lido de `motor_plate.center_clearance_diameter`).
- Furos com folga de impressão em ABS: M3 Ø3,4, M4 Ø4,3, arruela Ø8,7.

O G-code é fatiado aqui mesmo (a peça é uma chapa com furos): ABS 250/100 °C, bico 0,4,
camada 0,2, 100 % maciço, 3 paredes, brim de 5 mm, comandos padrão (Klipper/K1 e Marlin).
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = ROOT / "teste_impresso"  # fora de fabricacao/: o build republica aquela pasta inteira
NAME = "R01T_placa_teste_ABS_2mm"

# Folgas de impressão (ABS, furo vertical encolhe ~0,2 mm)
M3_HOLE = 3.4
M4_HOLE = 4.3
CENTER_HOLE: float | None = None  # None: usa o Ø do parameters.json
WASHER_HOLE = 8.7
WASHER_X = 55.0  # centro da arruela, à direita da placa, na mesma mesa

# Posição na mesa (cabe em mesa de 220 mm ou maior)
BED_X0, BED_Y0 = 100.0, 100.0

# Processo
NOZZLE_T, BED_T = 250, 100
FIL_D = 1.75
H = 0.2
W = 0.45
S = W - H * (1 - math.pi / 4)  # espaçamento entre filetes vizinhos (modelo Slic3r)
WALLS = 3
BRIM_LOOPS = 12  # ~5 mm
FLOW = 0.95  # maciço 100 %: leve sub-extrusão evita acúmulo
FLOW_L1 = 1.0
RETRACT, RETRACT_F = 0.8, 2400
MIN_RETRACT_TRAVEL = 1.5
V_L1, V_OUTER, V_INNER, V_INFILL, V_TRAVEL = 20, 40, 60, 80, 150  # mm/s


def set_center_hole(d: float | None) -> None:
    global CENTER_HOLE
    CENTER_HOLE = d


def load_geometry() -> dict:
    p = json.loads((ROOT / "CAD" / "parameters.json").read_text(encoding="utf-8"))
    q, motor, bt = p["motor_plate"], p["unverified_interfaces"]["motor"], p["base_tower"]
    holes = []
    dx, dy = motor["base_bolt_diagonal_x"] / 2, motor["base_bolt_diagonal_y"] / 2  # cruz
    for x, y in ((dx, 0.0), (-dx, 0.0), (0.0, dy), (0.0, -dy)):
        holes.append((x, y, M3_HOLE / 2, "M3 motor"))
    r = bt["flange_hole_pcd"] / 2
    for i in range(4):
        a = math.radians(bt["flange_hole_angle_offset_deg"] + 90.0 * i)
        holes.append((r * math.cos(a), r * math.sin(a), M4_HOLE / 2, "M4 flange"))
    holes.append((0.0, 0.0, (CENTER_HOLE or q["center_clearance_diameter"]) / 2, "alivio central"))
    wb = q["washer_blank"]
    return {
        "half": q["width"] / 2,
        "half_y": q["depth"] / 2,
        "thickness": q["thickness"],
        "holes": holes,
        "washer": (WASHER_X, 0.0, wb["outer_diameter"] / 2, WASHER_HOLE / 2),
    }


# --------------------------------------------------------------------------- STL (Blender)

def build_stl_in_blender(out: Path) -> None:
    import bpy  # noqa: PLC0415

    g = load_geometry()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    t = g["thickness"]

    def cyl(x, y, r, depth, name):
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=r, depth=depth, location=(x, y, t / 2))
        o = bpy.context.active_object
        o.name = name
        return o

    def cut(target, cutter):
        m = target.modifiers.new("cut", "BOOLEAN")
        m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", cutter
        bpy.context.view_layer.objects.active = target
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(cutter, do_unlink=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, t / 2))
    plate = bpy.context.active_object
    plate.scale = (2 * g["half"], 2 * g["half_y"], t)
    bpy.ops.object.transform_apply(scale=True)
    for i, (x, y, r, _) in enumerate(g["holes"]):
        cut(plate, cyl(x, y, r, t + 2, f"furo{i}"))

    wx, wy, ro, ri = g["washer"]
    washer = cyl(wx, wy, ro, t, "arruela")
    cut(washer, cyl(wx, wy, ri, t + 2, "furo_arruela"))

    for o in bpy.data.objects:
        o.select_set(True)
    bpy.ops.wm.stl_export(filepath=str(out), export_selected_objects=True, apply_modifiers=True)


# --------------------------------------------------------------------------- G-code

class GCode:
    def __init__(self):
        self.lines: list[str] = []
        self.x = self.y = self.z = 0.0
        self.e_total = 0.0
        self.time = 0.0
        self.extrusions: list[tuple[float, float, float, float, float]] = []  # para a verificação
        self.e_per_mm = H * S / (math.pi * (FIL_D / 2) ** 2)

    def emit(self, s: str) -> None:
        self.lines.append(s)

    def travel(self, x: float, y: float) -> None:
        d = math.hypot(x - self.x, y - self.y)
        if d < 1e-6:
            return
        retract = d > MIN_RETRACT_TRAVEL
        if retract:
            self.emit(f"G1 E-{RETRACT:.2f} F{RETRACT_F}")
        self.emit(f"G0 X{x + BED_X0:.3f} Y{y + BED_Y0:.3f} F{V_TRAVEL * 60}")
        if retract:
            self.emit(f"G1 E{RETRACT:.2f} F{RETRACT_F}")
            self.time += 2 * RETRACT / (RETRACT_F / 60)
        self.time += d / V_TRAVEL
        self.x, self.y = x, y

    def extrude(self, x: float, y: float, v: float, flow: float) -> None:
        d = math.hypot(x - self.x, y - self.y)
        if d < 1e-6:
            return
        e = d * self.e_per_mm * flow
        self.emit(f"G1 X{x + BED_X0:.3f} Y{y + BED_Y0:.3f} E{e:.5f} F{v * 60}")
        self.extrusions.append((self.x, self.y, x, y, self.z))
        self.e_total += e
        self.time += d / v
        self.x, self.y = x, y

    def path(self, pts, v, flow, closed=True):
        self.travel(*pts[0])
        for p in pts[1:]:
            self.extrude(*p, v, flow)
        if closed:
            self.extrude(*pts[0], v, flow)


def circle_pts(cx, cy, r, start=0.0):
    n = max(24, int(2 * math.pi * r / 0.4))
    return [(cx + r * math.cos(start + 2 * math.pi * k / n), cy + r * math.sin(start + 2 * math.pi * k / n)) for k in range(n)]


def rect_pts(a, b):
    return [(-a, -b), (a, -b), (a, b), (-a, b)]


def hole_wall_counts(g) -> list[int]:
    """Paredes por furo: cada furo usa no máximo metade da alma até o vizinho mais próximo."""
    out = []
    holes = g["holes"]
    for i, (xi, yi, ri, _) in enumerate(holes):
        web = min(
            [math.hypot(xi - xj, yi - yj) - ri - rj for j, (xj, yj, rj, _) in enumerate(holes) if j != i]
            + [2 * (g["half"] - max(abs(xi), abs(yi)) - ri)]
        )
        n = 1 if web / 2 < W else int((web / 2 - W) / S) + 1
        out.append(max(1, min(WALLS, n)))
    return out


def infill_segments(g, walls, angle):
    """Linhas retilíneas (maciço) recortadas pelo contorno e pelos furos, em ângulo `angle`."""
    ca, sa = math.cos(angle), math.sin(angle)
    rot = lambda x, y: (x * ca + y * sa, -x * sa + y * ca)  # noqa: E731  mundo -> linha horizontal
    unrot = lambda u, v: (u * ca - v * sa, u * sa + v * ca)  # noqa: E731
    overlap = 0.15 * W
    inset = W / 2 + WALLS * S - overlap
    a, b = g["half"] - inset, g["half_y"] - inset
    poly = [rot(x, y) for x, y in rect_pts(a, b)]
    circles = []
    for (x, y, r, _), n in zip(g["holes"], walls):
        u, v = rot(x, y)
        circles.append((u, v, r + W / 2 + n * S - overlap))
    vs = [p[1] for p in poly]
    segs = []
    c = math.floor(min(vs) / S) * S + S / 2
    while c < max(vs):
        xs = []
        for k in range(4):
            (u0, v0), (u1, v1) = poly[k], poly[(k + 1) % 4]
            if (v0 - c) * (v1 - c) < 0:
                xs.append(u0 + (c - v0) * (u1 - u0) / (v1 - v0))
        if len(xs) == 2:
            pieces = [(min(xs), max(xs))]
            for u, v, r in circles:
                if abs(c - v) >= r:
                    continue
                h = math.sqrt(r * r - (c - v) ** 2)
                lo, hi = u - h, u + h
                nxt = []
                for p0, p1 in pieces:
                    if hi <= p0 or lo >= p1:
                        nxt.append((p0, p1))
                        continue
                    if lo > p0:
                        nxt.append((p0, lo))
                    if hi < p1:
                        nxt.append((hi, p1))
                pieces = nxt
            for p0, p1 in pieces:
                if p1 - p0 >= 0.3:
                    segs.append((unrot(p0, c), unrot(p1, c)))
        c += S
    return segs


def order_segments(segs, start):
    out, pos, left = [], start, list(segs)
    while left:
        best, bi, flip = None, 0, False
        for i, (p, q) in enumerate(left):
            for f, pt in ((False, p), (True, q)):
                d = (pt[0] - pos[0]) ** 2 + (pt[1] - pos[1]) ** 2
                if best is None or d < best:
                    best, bi, flip = d, i, f
        p, q = left.pop(bi)
        if flip:
            p, q = q, p
        out.append((p, q))
        pos = q
    return out


def build_gcode(g) -> GCode:
    gc = GCode()
    walls = hole_wall_counts(g)
    wx, wy, wro, wri = g["washer"]
    n_layers = round(g["thickness"] / H)

    gc.emit(f"; {NAME} — simula a chapa R01 (alumínio 2 mm) para testes em baixa rotação")
    gc.emit("; Gerado por Hologram_Orbiter_v3_0/scripts/r01_placa_teste.py")
    gc.emit(f"; ABS {NOZZLE_T}/{BED_T} C, bico 0.4, camada {H}, largura {W}, {WALLS} paredes, 100% macico, brim 5 mm")
    gc.emit(f"; Furos do motor em cruz: 16 e 19 mm nas diagonais. Peca em X{BED_X0 - 35:.0f}-{BED_X0 + WASHER_X + 15:.0f} Y{BED_Y0 - 35:.0f}-{BED_Y0 + 35:.0f}")
    gc.emit("; G-code padrao (Klipper/Creality K1 e Marlin). Feche a camara: ABS.")
    gc.emit("G90")
    gc.emit("M83")
    gc.emit(f"M140 S{BED_T}")
    gc.emit("M104 S170")
    gc.emit("G28")
    gc.emit(f"M190 S{BED_T}")
    gc.emit(f"M109 S{NOZZLE_T}")
    gc.emit("M107")
    gc.emit("G92 E0")
    gc.emit("; linha de purga")
    gc.emit("G0 Z5 F600")
    gc.emit(f"G0 X20 Y30 F{V_TRAVEL * 60}")
    gc.emit("G0 Z0.3 F600")
    gc.emit("G1 X20 Y130 E8 F1200")
    gc.emit("G1 X20.5 Y130 F1200")
    gc.emit("G1 X20.5 Y40 E7 F1200")
    gc.x, gc.y = 20.5 - BED_X0, 40 - BED_Y0
    gc.time += 100 / 20 + 90 / 20

    for layer in range(n_layers):
        z = H * (layer + 1)
        first = layer == 0
        flow = FLOW_L1 if first else FLOW
        v_out, v_in, v_inf = (V_L1,) * 3 if first else (V_OUTER, V_INNER, V_INFILL)
        gc.emit(f";LAYER:{layer}")
        gc.emit(f"G0 Z{z:.3f} F600")
        gc.z = z
        if first:
            gc.emit(";TYPE:SKIRT")
            for k in reversed(range(BRIM_LOOPS)):
                off = W / 2 + k * S
                gc.path(rect_pts(g["half"] + off, g["half_y"] + off), V_L1, flow)
            for k in reversed(range(BRIM_LOOPS)):
                gc.path(circle_pts(wx, wy, wro + W / 2 + k * S, math.pi), V_L1, flow)

        # Placa: paredes do contorno (de dentro para fora), paredes dos furos, depois o maciço
        gc.emit(";TYPE:WALL-OUTER")
        for k in reversed(range(WALLS)):
            off = W / 2 + k * S
            gc.path(rect_pts(g["half"] - off, g["half_y"] - off), v_out if k == 0 else v_in, flow)
        for (x, y, r, _), n in zip(g["holes"], walls):
            ang = math.atan2(y, x) if (x or y) else 0.0
            for k in reversed(range(n)):
                gc.path(circle_pts(x, y, r + W / 2 + k * S, ang), v_out if k == 0 else v_in, flow)
        gc.emit(";TYPE:FILL")
        angle = math.radians(45 if layer % 2 == 0 else -45)
        for p, q in order_segments(infill_segments(g, walls, angle), (gc.x, gc.y)):
            gc.travel(*p)
            gc.extrude(*q, v_inf, flow)

        # Arruela: anéis concêntricos, maciça
        gc.emit(";TYPE:WALL-INNER")
        span = (wro - W / 2) - (wri + W / 2)
        n_rings = max(2, round(span / S) + 1)
        step = span / (n_rings - 1)
        for k in range(n_rings):
            r = wri + W / 2 + k * step
            v = v_out if k in (0, n_rings - 1) else v_in
            gc.path(circle_pts(wx, wy, r, math.pi), v, flow)

        if layer == 1:
            gc.emit("M106 S38")  # ABS: ventilação mínima (15 %) a partir da 2a camada

    gc.emit("; fim")
    gc.emit(f"G1 E-{RETRACT:.2f} F{RETRACT_F}")
    gc.emit("M107")
    gc.emit(f"G0 Z{gc.z + 10:.1f} F600")
    gc.emit(f"G0 X{BED_X0:.0f} Y200 F{V_TRAVEL * 60}")
    gc.emit("M104 S0")
    gc.emit("M140 S0")
    gc.emit("M84")
    return gc


def verify(g, gc: GCode) -> list[str]:
    """Todo ponto extrudido (com meia largura) dentro do sólido; nenhum dentro de furo."""
    errs = []
    wx, wy, wro, wri = g["washer"]
    tol = W / 2 - 0.02
    for x0, y0, x1, y1, z in gc.extrusions:
        for t in (0.0, 0.5, 1.0):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            in_plate = abs(x) <= g["half"] + 0.01 and abs(y) <= g["half_y"] + 0.01
            in_washer = math.hypot(x - wx, y - wy) <= wro + 0.01
            if z <= H + 1e-6 and not (in_plate or in_washer):
                continue  # brim
            if in_plate:
                if abs(x) > g["half"] - tol or abs(y) > g["half_y"] - tol:
                    errs.append(f"fora do contorno em ({x:.2f},{y:.2f}) z={z}")
                for hx, hy, r, label in g["holes"]:
                    if math.hypot(x - hx, y - hy) < r + tol:
                        errs.append(f"dentro do furo {label} em ({x:.2f},{y:.2f}) z={z}")
            elif in_washer:
                d = math.hypot(x - wx, y - wy)
                if d < wri + tol or d > wro - tol:
                    errs.append(f"arruela fora da coroa em ({x:.2f},{y:.2f}) z={z}")
            else:
                errs.append(f"extrusão solta em ({x:.2f},{y:.2f}) z={z}")
    return errs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    ap.add_argument("--no-stl", action="store_true")
    ap.add_argument("--furo-central", type=float, default=CENTER_HOLE, help="Ø do alívio central, mm (padrão: parameters.json)")
    ap.add_argument("--blender", default="/Applications/Blender.app/Contents/MacOS/Blender")
    args = ap.parse_args()
    set_center_hole(args.furo_central)
    args.out.mkdir(parents=True, exist_ok=True)

    g = load_geometry()
    gc = build_gcode(g)
    errs = verify(g, gc)
    if errs:
        print("\n".join(errs[:20]), file=sys.stderr)
        sys.exit(f"{len(errs)} extrusões fora da peça")
    mass = gc.e_total * math.pi * (FIL_D / 2) ** 2 * 1.04e-3
    gc.lines.insert(5, f"; filamento ~{gc.e_total / 1000:.2f} m ({mass:.1f} g ABS), tempo estimado ~{gc.time / 60:.0f} min")
    gcode_path = args.out / f"{NAME}_Creality.gcode"
    gcode_path.write_text("\n".join(gc.lines) + "\n", encoding="utf-8")
    print(f"G-code: {gcode_path} — {len(gc.lines)} linhas, {gc.e_total / 1000:.2f} m, {mass:.1f} g, ~{gc.time / 60:.0f} min")
    print("paredes por furo:", {h[3] + f"@({h[0]:.1f},{h[1]:.1f})": n for h, n in zip(g["holes"], hole_wall_counts(g))})

    if not args.no_stl:
        stl = args.out / f"{NAME}.stl"
        subprocess.run([args.blender, "-b", "--python-exit-code", "1", "--python", __file__, "--", "--stl", str(stl)] + (["--furo-central", str(args.furo_central)] if args.furo_central else []),
                       check=True, capture_output=True)
        print(f"STL: {stl}")


if __name__ == "__main__":
    if "--stl" in sys.argv:
        if "--furo-central" in sys.argv:
            set_center_hole(float(sys.argv[sys.argv.index("--furo-central") + 1]))
        build_stl_in_blender(Path(sys.argv[sys.argv.index("--stl") + 1]))
    else:
        main()
