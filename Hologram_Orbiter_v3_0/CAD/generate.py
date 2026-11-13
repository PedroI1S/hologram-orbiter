#!/usr/bin/env python3
"""Gerador CAD paramétrico do Hologram Orbiter v3.0.

Execute dentro do Blender 5.x (headless):

    blender -b --python CAD/generate.py -- --output-dir exports [--no-render]

Toda cota vem de CAD/parameters.json. Unidade: milímetro. O STL não guarda
unidade; os arquivos exportados devem ser lidos como mm.

Convenções (spec §3): origem no eixo do rotor, Z para cima, giro anti-horário
visto de +Z, bordo de ataque em +y.

Referenciais locais usados aqui:
  * painel: x radial (para fora), y corda (+y = bordo de ataque), z vertical,
    origem no centro da junta (Datum D = 104 mm acima da base do painel);
  * aranha: origem no eixo, z = 0 na face superior do cubo (Datum B);
  * base/torre, chapa e suporte do ímã: z = 0 na face de apoio da base;
  * tampa: z = 0 na face inferior da pele.

Regra booleana (06-PENDENCIAS A1): cada cortador é subtraído sozinho. Nunca
concatenar cortadores com object.join antes da diferença — onde dois se
sobrepõem o operando fica com enrolamento 2 e o resultado 1 − 2 = −1, uma
casca invertida que passa em toda checagem de arestas e imprime como sólido.
Os critérios de aceitação são medidos na malha final por traçado de raios
(CAD/probe.py), não lidos de volta dos parâmetros.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from probe import MeshProbe  # noqa: E402
from parameters import load_parameters  # noqa: E402
from physics import arm_root_estimate, calculate_physics, inertia_about_z, suspension_estimate  # noqa: E402
from spider_checks import measure_bay_entries  # noqa: E402


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=HERE / "parameters.json")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "exports")
    parser.add_argument("--report-dir", type=Path, default=PROJECT_ROOT / "reports")
    parser.add_argument("--no-render", action="store_true")
    return parser.parse_args(argv)


ARGS = parse_args()
P = load_parameters(ARGS.parameters)

SEGMENTS = int(P["quality"]["curve_segments"])
BOOL_SOLVER = P["quality"]["boolean_solver"]
# Variante 3.1-P: base suspensa em paralelogramo (parameters_paralelogramo.json).
SUSP = P["base_tower"].get("suspension") or {}
SUSPENDED = bool(SUSP.get("enabled"))

DEFAULT_EXPORT_NAMES = {
    "spider": "01_aranha_ABS.stl",
    "lid": "03_tampa_baia_ABS.stl",
    "base_tower": "04_05_base_torre_ABS_integradas.stl",
    "magnet_bracket": "06_suporte_ima_ABS.stl",
}


def export_name(key: str, **fmt) -> str:
    name = {**DEFAULT_EXPORT_NAMES, **P.get("export_names", {})}[key]
    return name.format(**fmt) if fmt else name


def density_for(part: str) -> float:
    """Densidade por peça; sem mapa na parametrização, tudo é ABS (pacote 3.0.5)."""
    return P["material"].get("part_density_g_cm3", {}).get(part, P["material"]["abs_density_g_cm3"])


def tower_base_z() -> float:
    """Z em que a torre nasce: piso da baia (3.0.5) ou topo do palco suspenso."""
    return SUSP["stage_top_z"] if SUSPENDED else P["base_tower"]["central_floor_thickness"]


def tower_top_z() -> float:
    return tower_base_z() + P["base_tower"]["tower_total_height_from_floor"]


# --------------------------------------------------------------------------
# Infraestrutura de modelagem
# --------------------------------------------------------------------------

def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        if block.users == 0:
            bpy.data.meshes.remove(block)


def activate(obj: bpy.types.Object) -> None:
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transform(obj: bpy.types.Object) -> bpy.types.Object:
    activate(obj)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return obj


def apply_location(obj: bpy.types.Object) -> bpy.types.Object:
    activate(obj)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return obj


def recalc_normals(obj: bpy.types.Object) -> None:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()


def cleanup_mesh(obj: bpy.types.Object) -> None:
    """Remove resíduos numéricos de CSG e triangula preservando cavidades."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-4)
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-4)
    bm.normal_update()
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()


def cube(
    name: str,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation_z_deg: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    obj.rotation_euler[2] = math.radians(rotation_z_deg)
    return apply_transform(obj)


def box_xyz(name: str, x: tuple[float, float], y: tuple[float, float], z: tuple[float, float]) -> bpy.types.Object:
    """Caixa alinhada aos eixos definida por intervalos."""
    return cube(
        name,
        (x[1] - x[0], y[1] - y[0], z[1] - z[0]),
        ((x[0] + x[1]) / 2.0, (y[0] + y[1]) / 2.0, (z[0] + z[1]) / 2.0),
    )


def frustum(name: str, r_bottom: float, r_top: float, z0: float, z1: float) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cone_add(vertices=SEGMENTS, radius1=r_bottom, radius2=r_top, depth=z1 - z0,
                                    end_fill_type="NGON", location=(0.0, 0.0, (z0 + z1) / 2))
    obj = bpy.context.object
    obj.name = name
    return apply_transform(obj)


def cylinder(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    vertices: int | None = None,
    rotation_z_deg: float = 0.0,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices or SEGMENTS,
        radius=radius,
        depth=depth,
        end_fill_type="NGON",
        location=location,
        rotation=(0.0, 0.0, math.radians(rotation_z_deg)),
    )
    obj = bpy.context.object
    obj.name = name
    return apply_transform(obj)


def _prism(name: str, vertices: list[tuple[float, float, float]], count: int, flip: bool) -> bpy.types.Object:
    if flip:
        faces = [list(range(count)), list(reversed(range(count, count * 2)))]
        for i in range(count):
            j = (i + 1) % count
            faces.append([i, i + count, j + count, j])
    else:
        faces = [list(reversed(range(count))), list(range(count, count * 2))]
        for i in range(count):
            j = (i + 1) % count
            faces.append([i, j, j + count, i + count])
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    recalc_normals(obj)
    return obj


def mesh_prism_z(name: str, points_xy: list[tuple[float, float]], z0: float, z1: float) -> bpy.types.Object:
    count = len(points_xy)
    vertices = [(x, y, z0) for x, y in points_xy] + [(x, y, z1) for x, y in points_xy]
    return _prism(name, vertices, count, flip=False)


def mesh_prism_x(name: str, points_yz: list[tuple[float, float]], x0: float, x1: float) -> bpy.types.Object:
    count = len(points_yz)
    vertices = [(x0, y, z) for y, z in points_yz] + [(x1, y, z) for y, z in points_yz]
    return _prism(name, vertices, count, flip=False)


def mesh_loft_x(name: str, prof0: list[tuple[float, float]], prof1: list[tuple[float, float]], x0: float, x1: float) -> bpy.types.Object:
    """Sólido regrado entre dois perfis (y, z) de mesma contagem de vértices, em x0 e x1."""
    if len(prof0) != len(prof1):
        raise ValueError(f"{name}: perfis com contagens diferentes")
    count = len(prof0)
    vertices = [(x0, y, z) for y, z in prof0] + [(x1, y, z) for y, z in prof1]
    return _prism(name, vertices, count, flip=False)


def mesh_prism_y(name: str, points_xz: list[tuple[float, float]], y0: float, y1: float) -> bpy.types.Object:
    count = len(points_xz)
    vertices = [(x, y0, z) for x, z in points_xz] + [(x, y1, z) for x, z in points_xz]
    return _prism(name, vertices, count, flip=True)


def annular_sector(
    name: str, r_inner: float, r_outer: float, a0_deg: float, a1_deg: float, z0: float, z1: float, steps: int = 24
) -> bpy.types.Object:
    a0 = math.radians(a0_deg)
    a1 = math.radians(a1_deg)
    inner = [(r_inner * math.cos(a0 + (a1 - a0) * i / steps), r_inner * math.sin(a0 + (a1 - a0) * i / steps)) for i in range(steps + 1)]
    outer = [(r_outer * math.cos(a1 - (a1 - a0) * i / steps), r_outer * math.sin(a1 - (a1 - a0) * i / steps)) for i in range(steps + 1)]
    return mesh_prism_z(name, inner + outer, z0, z1)


def duplicate(obj: bpy.types.Object, name: str) -> bpy.types.Object:
    clone = obj.copy()
    clone.data = obj.data.copy()
    clone.name = name
    clone.hide_render = False
    clone.hide_viewport = False
    bpy.context.collection.objects.link(clone)
    return clone


def delete_object(obj: bpy.types.Object | None) -> None:
    if obj is None or obj.name not in bpy.data.objects:
        return
    bpy.data.objects.remove(obj, do_unlink=True)


def boolean(target: bpy.types.Object, operand: bpy.types.Object, operation: str, label: str) -> bpy.types.Object:
    activate(target)
    modifier = target.modifiers.new(name=label, type="BOOLEAN")
    modifier.operation = operation
    modifier.solver = BOOL_SOLVER
    modifier.object = operand
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except Exception as exc:  # pragma: no cover - diagnóstico
        raise RuntimeError(f"Falha booleana {operation} em {target.name} usando {operand.name}: {exc}") from exc
    delete_object(operand)
    # Não recalcular normais após CSG: em corpos ocos isso inverteria a
    # orientação da cavidade interna e corromperia volume/massa no STL.
    return target


def union_all(parts: list[bpy.types.Object], name: str) -> bpy.types.Object:
    if not parts:
        raise ValueError("union_all requer ao menos uma peça")
    result = parts[0]
    result.name = name
    for index, part in enumerate(parts[1:], 1):
        result = boolean(result, part, "UNION", f"union_{index:03d}")
    result.name = name
    return result


def subtract_each(target: bpy.types.Object, cutters: list[bpy.types.Object], label: str) -> bpy.types.Object:
    """Subtrai os cortadores UM A UM.

    A versão anterior concatenava os cortadores (object.join) e fazia uma só
    diferença; cortadores sobrepostos (furo do parafuso × bolso da porca,
    furo × socket) viravam cascas invertidas no resultado. Com uma diferença
    por cortador cada operando é uma variedade fechada simples.
    """
    for index, cutter in enumerate(cutters):
        target = boolean(target, cutter, "DIFFERENCE", f"{label}_{index:03d}")
    return target


def intersect(target: bpy.types.Object, operand: bpy.types.Object, label: str) -> bpy.types.Object:
    return boolean(target, operand, "INTERSECT", label)


def rotate_about_z(obj: bpy.types.Object, angle_deg: float) -> bpy.types.Object:
    """Gira em torno do eixo Z do MUNDO (a origem do objeto é levada a zero antes)."""
    apply_location(obj)
    obj.rotation_euler[2] += math.radians(angle_deg)
    return apply_transform(obj)


def cube_polar(
    name: str,
    dimensions: tuple[float, float, float],
    radius: float,
    angle_deg: float,
    z_center: float,
) -> bpy.types.Object:
    """Caixa centrada em (radius, angle) com o eixo local x apontando na direção radial."""
    x, y = polar(radius, angle_deg)
    return cube(name, dimensions, (x, y, z_center), rotation_z_deg=angle_deg)


def translate(obj: bpy.types.Object, dx: float, dy: float, dz: float) -> bpy.types.Object:
    obj.location.x += dx
    obj.location.y += dy
    obj.location.z += dz
    return apply_location(obj)


def ring(name: str, outer_radius: float, inner_radius: float, z0: float, z1: float) -> bpy.types.Object:
    outer = cylinder(f"{name}_outer", outer_radius, z1 - z0, (0.0, 0.0, (z0 + z1) / 2))
    inner = cylinder(f"{name}_inner_cut", inner_radius, z1 - z0 + 0.2, (0.0, 0.0, (z0 + z1) / 2))
    return boolean(outer, inner, "DIFFERENCE", f"{name}_hollow")


def polar(r: float, angle_deg: float) -> tuple[float, float]:
    a = math.radians(angle_deg)
    return (r * math.cos(a), r * math.sin(a))


def rot_xy(x: float, y: float, angle_deg: float) -> tuple[float, float]:
    a = math.radians(angle_deg)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))


def line_intersect(p1, d1, p2, d2) -> tuple[float, float]:
    """Interseção de duas retas p + t·d no plano."""
    det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
    if abs(det) < 1e-12:
        raise ValueError("retas paralelas")
    rx, ry = p2[0] - p1[0], p2[1] - p1[1]
    t = (rx * (-d2[1]) - ry * (-d2[0])) / det
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def unit(v) -> tuple[float, float]:
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n)


# --------------------------------------------------------------------------
# 02 — Painel LED
# --------------------------------------------------------------------------

def fairing_polygons() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Contornos externo e interno (cavidade) da carenagem em planta (x, y)."""
    f = P["panel"]["fairing"]
    t = f["wall"]
    xf = f["flat_flank_x"]
    yh = f["flat_flank_y_half"]
    cx, cy = f["nose_center_xy"]
    a, b = f["nose_semi_axes"]
    ov = f["blade_overlap"]
    xb = f["blade_flat_face_x"]
    y_flat0, _ = f["blade_flat_y_range"]
    taper_end = tuple(f["blade_taper_end_xy"])
    tail = tuple(f["tail_xy"])
    steps = 24

    def ellipse(ax: float, by: float) -> list[tuple[float, float]]:
        pts = []
        for i in range(steps + 1):
            ang = math.pi * (1.0 - i / steps)  # 180° → 0°
            pts.append((cx + ax * math.cos(ang), cy + by * math.sin(ang)))
        return pts

    outer = ellipse(a, b)  # de (xf, yh) até (xb+ov, yh)
    outer[0] = (xf, yh)
    outer[-1] = (xb + ov, yh)
    outer += [
        (xb + ov, y_flat0),
        (taper_end[0] + ov, taper_end[1]),
        tail,
        (xf, -yh),
    ]

    o4 = (taper_end[0] + ov, taper_end[1])
    d_out = unit((tail[0] - o4[0], tail[1] - o4[1]))
    n_out = (-d_out[1], d_out[0])
    if n_out[0] > 0:
        n_out = (-n_out[0], -n_out[1])
    o6 = (xf, -yh)
    d_in = unit((o6[0] - tail[0], o6[1] - tail[1]))
    n_in = (-d_in[1], d_in[0])
    if n_in[0] < 0:
        n_in = (-n_in[0], -n_in[1])
    p_out = (o4[0] + t * n_out[0], o4[1] + t * n_out[1])
    p_in = (tail[0] + t * n_in[0], tail[1] + t * n_in[1])
    taper_dir = unit((taper_end[0] - xb, taper_end[1] - y_flat0))
    x1 = line_intersect((xb, y_flat0), taper_dir, p_out, d_out)
    x_tail = line_intersect(p_out, d_out, p_in, d_in)
    x2 = line_intersect(p_in, d_in, (xf + t, 0.0), (0.0, 1.0))

    inner = ellipse(a - t, b - t)
    inner[0] = (xf + t, yh)
    inner[-1] = (xb - 0.6, yh)
    inner += [
        (xb, yh),
        (xb, y_flat0),
        x1,
        x_tail,
        x2,
    ]
    return outer, inner


def panel_channel_x() -> dict:
    """Cotas em x (radial) do canal do LED, derivadas dos parâmetros."""
    q = P["panel"]
    ch = q["led_channel"]
    x_out = q["max_thickness"] / 2.0
    return {
        "x_out": x_out,
        "x_shell_inner": x_out - q["shell_wall"],
        "x_channel_floor": x_out - ch["depth"],
        "x_local_wall_inner": x_out - ch["local_wall"],
        "floor_thickness": ch["local_wall"] - ch["depth"],
    }


def local_wall_band_half_width() -> float:
    """Meia largura da faixa em que a parede externa engrossa para local_wall.

    A faixa transborda o canal em local_wall_band_margin de cada lado: é o que
    liga o piso de 0,8 mm à parede de 2,0 por uma área, e não por uma linha.
    """
    ch = P["panel"]["led_channel"]
    return ch["width"] / 2.0 + ch["local_wall_band_margin"]


def build_panel() -> bpy.types.Object:
    q = P["panel"]
    b = q["boss"]
    f = q["fairing"]
    ch = q["led_channel"]
    rb = q["ribs"]
    cx = panel_channel_x()
    height = q["height"]
    hh = height / 2.0
    skin = q["end_skin"]

    outer_profile = [tuple(p) for p in q["profile_outer_xy"]]
    cavity_profile = [tuple(p) for p in q["profile_cavity_xy"]]

    shell = mesh_prism_z("panel_shell_outer", outer_profile, -hh, hh)
    cavity = mesh_prism_z("panel_shell_cavity", cavity_profile, -hh + skin, hh - skin)
    # Parede local do canal: na faixa do canal mais a margem, a cavidade recua
    # até x = 1,2 (parede de 2,8) — inclusive onde o perfil já afila para a
    # fuga —, deixando 0,8 mm de piso sob o canal de 2,0 mm.
    half = local_wall_band_half_width()
    band = box_xyz(
        "cavity_local_wall_band",
        (cx["x_local_wall_inner"], cx["x_shell_inner"] + 1.0),
        (-half, half),
        (-hh, hh),
    )
    cavity = boolean(cavity, band, "DIFFERENCE", "cavity_local_wall")
    shell = boolean(shell, cavity, "DIFFERENCE", "hollow_panel")

    # Diafragmas cravados 0,2 mm na parede, cada um partido em duas metades
    # para deixar passar o feixe de fios.
    sx, sy = rb["scale_xy"]
    rib_points = [(x * sx, y * sy) for x, y in cavity_profile]
    gy0, gy1 = rb["wire_gap_y"]
    t_rib = rb["thickness"]
    ribs = []
    for index, z in enumerate(rb["z_positions"]):
        rib = mesh_prism_z(f"panel_rib_{index}", rib_points, z - t_rib / 2, z + t_rib / 2)
        gap = box_xyz(f"panel_rib_gap_{index}", (-3.0, 3.0), (gy0, gy1), (z - t_rib, z + t_rib))
        rib = boolean(rib, gap, "DIFFERENCE", f"rib_gap_{index}")
        ribs.append(rib)

    # Boss: luva do socket, torres Ø10 e alma central.
    x_contact = b["contact_face_x"]
    sleeve = box_xyz(
        "boss_sleeve",
        (x_contact, x_contact + b["sleeve_length"]),
        (-b["sleeve_width_y"] / 2, b["sleeve_width_y"] / 2),
        (-b["sleeve_height_z"] / 2, b["sleeve_height_z"] / 2),
    )
    towers = [
        cylinder(f"boss_tower_{i}", b["tower_diameter"] / 2, b["tower_height"], (x, 0.0, 0.0))
        for i, x in enumerate(b["screw_x_positions"])
    ]
    web = box_xyz(
        "boss_web",
        tuple(b["web_x_range"]),
        (-b["web_thickness"] / 2, b["web_thickness"] / 2),
        (-b["tower_height"] / 2, b["tower_height"] / 2),
    )

    # Carenagem em gota: casca extrudada em Z, aberta em cima e embaixo.
    outer_poly, inner_poly = fairing_polygons()
    zh = f["half_height"]
    fairing = mesh_prism_z("fairing_outer", outer_poly, -zh, zh)
    fairing_cavity = mesh_prism_z("fairing_cavity", inner_poly, -zh - 0.5, zh + 0.5)
    fairing = boolean(fairing, fairing_cavity, "DIFFERENCE", "fairing_shell")

    panel = union_all([shell, *ribs, sleeve, *towers, web, fairing], "painel_led")

    # ---- Cortes (um a um) ----
    cutters: list[bpy.types.Object] = []
    x_out = cx["x_out"]
    channel_z0 = -hh + ch["bottom_skin"] + ch["wire_pocket_height"]
    # Canal do LED: 12,4 x 2,0, do batente da fita ao topo (aberto).
    cutters.append(
        box_xyz(
            "led_channel_cut",
            (cx["x_channel_floor"], x_out + 0.5),
            (-ch["width"] / 2, ch["width"] / 2),
            (channel_z0, hh + 0.2),
        )
    )
    # Bolso passante 8 x 3,5 sob a ponta da fita, invadindo o canal em 0,2.
    pocket_z0 = -hh + skin + 0.2
    cutters.append(
        box_xyz(
            "led_wire_pocket",
            (cx["x_local_wall_inner"] - 0.2, x_out + 0.5),
            (-ch["wire_pocket_width"] / 2, ch["wire_pocket_width"] / 2),
            (pocket_z0, channel_z0 + ch["wire_pocket_overlap"]),
        )
    )
    socket_x1 = x_contact + b["socket_depth"]
    cutters.append(
        box_xyz(
            "socket_cut",
            (x_contact - 0.2, socket_x1),
            (-b["socket_width"] / 2, b["socket_width"] / 2),
            (-b["socket_height"] / 2, b["socket_height"] / 2),
        )
    )
    for i, x in enumerate(b["screw_x_positions"]):
        cutters.append(cylinder(f"panel_screw_hole_{i}", b["screw_hole_diameter"] / 2, b["tower_height"] + 2.4, (x, 0.0, 0.0)))
        cutters.append(
            cylinder(
                f"panel_nut_pocket_{i}",
                b["nut_hex_circumradius"],
                b["nut_pocket_depth"] + 0.2,
                (x, 0.0, -b["tower_height"] / 2 + b["nut_pocket_depth"] / 2 - 0.1),
                vertices=6,
                rotation_z_deg=30.0,
            )
        )
    cutters.append(
        box_xyz(
            "fairing_wire_window",
            (f["flat_flank_x"] - 0.6, f["flat_flank_x"] + f["wall"] + 0.3),
            tuple(f["wire_window_y"]),
            tuple(f["wire_window_z"]),
        )
    )
    cutters.append(
        box_xyz(
            "blade_wire_hole",
            (f["blade_flat_face_x"] - 0.6, f["blade_flat_face_x"] + q["shell_wall"] + 0.4),
            tuple(f["blade_wire_hole_y"]),
            tuple(f["blade_wire_hole_z"]),
        )
    )
    panel = subtract_each(panel, cutters, "panel_feature")
    panel.name = "02_painel_led"
    return panel


# --------------------------------------------------------------------------
# 01 — Aranha
# --------------------------------------------------------------------------

def build_arm(index: int) -> bpy.types.Object:
    a = P["spider"]["arm"]
    q = P["spider"]
    airfoil = [tuple(p) for p in a["airfoil_yz"]]
    # A raiz começa na parede da baia, sem avançar no seu espaço interno.
    # O aerofólio termina EXATAMENTE no ombro (r = 74,0): é a face em que o
    # painel encosta. A espiga entra 0,2 no aerofólio para fundir (B1).
    beam = mesh_prism_x(f"arm_{index}_airfoil", airfoil, a["root_radius"], a["shoulder_radius"])
    tenon = box_xyz(
        f"arm_{index}_tenon",
        (a["shoulder_radius"] - a["tenon_overlap_into_beam"], a["tenon_tip_radius"]),
        (-a["tenon_width"] / 2, a["tenon_width"] / 2),
        (0.0, a["tenon_height"]),
    )
    root = mesh_prism_z(f"arm_{index}_root_blend", [tuple(p) for p in a["root_blend_xy"]], -0.1, a["height"])
    parts = [beam, tenon, root]
    g = a.get("root_gusset", {})
    if g.get("enabled", False):
        # Cunha a 45° sob o braço, da borda inferior do disco até a face
        # inferior do braço: fillet cubo→braço (B11). Topo em z = 1,8 para
        # entrar no aerofólio em toda a largura da cunha (|y| ≤ 5,5).
        r_hub = q["hub_diameter"] / 2
        z_top = 1.8
        x0 = r_hub - 0.5
        z0 = -q["hub_thickness"]
        x1 = x0 + (z_top - z0) * (g["radial_run"] / g["drop"])
        gusset = mesh_prism_y(
            f"arm_{index}_root_gusset",
            [(x0, z0), (x1, z_top), (x0, z_top)],
            -g["width"] / 2,
            g["width"] / 2,
        )
        parts.append(gusset)
    rf = a.get("reinforcement", {})
    if rf.get("enabled"):
        # Aleta sobre o braço (lado +y, fora do sulco dos fios) e alma por baixo.
        # Ambas terminam antes do ombro: a face de contato do painel não muda.
        fin = rf["fin"]
        web = rf["web"]
        fr = rf.get("fairing", {})
        if fr.get("enabled"):
            # Reforço carenado (pedido de 13/11/2026): a aleta retangular tinha a face larga
            # contra o vento (Cd ≈ 2). Aleta em "D": costas retas em y0 (o sulco dos fios em
            # y < 0 continua livre), nariz em quarto de elipse até o bordo de ataque (+y).
            # Alma: perfil de asa invertido em toda a corda, nariz arredondado e cauda afilada.
            n = int(fr.get("arc_points", 10))
            y0, y_nose, z_floor = fin["y_range"][0], fr["fin_nose_y"], fr["fin_floor_z"]

            def fin_profile(top_z: float) -> list[tuple[float, float]]:
                a_, b_ = y_nose - y0, top_z - z_floor
                e = 2.0 / fr.get("fin_superellipse_exponent", 2.0)  # > 2: perfil mais cheio no topo
                arc = []
                for k in range(n + 1):
                    t = math.radians(90.0 - 90.0 * k / n)
                    arc.append((y0 + a_ * math.cos(t) ** e, z_floor + b_ * math.sin(t) ** e))
                return [(y0, z_floor)] + arc

            parts.append(mesh_loft_x(f"arm_{index}_fin", fin_profile(fin["root_top_z"]), fin_profile(fin["end_top_z"]),
                                     fin["root_radius"], fin["end_radius"]))
            y_tail, z_tail = fr["web_tail_yz"]
            y_flat0, y_flat1 = fr["web_flat_y"]
            z_top_nose = fr["web_nose_top_z"]

            def web_profile(bottom_z: float) -> list[tuple[float, float]]:
                a_, b_ = y_nose - y_flat1, z_top_nose - bottom_z
                pts = [(y_tail, z_tail), (y_flat0, bottom_z)]
                pts += [(y_flat1 + a_ * math.sin(math.radians(90.0 * k / n)), z_top_nose - b_ * math.cos(math.radians(90.0 * k / n))) for k in range(n + 1)]
                return pts

            parts.append(mesh_loft_x(f"arm_{index}_web", web_profile(web["root_bottom_z"]), web_profile(web.get("end_bottom_z", 0.3)),
                                     web["root_radius"], web["end_radius"]))
        else:
            parts.append(mesh_prism_y(
                f"arm_{index}_fin",
                [(fin["root_radius"], a["height"] - 0.3), (fin["end_radius"], a["height"] - 0.3),
                 (fin["end_radius"], fin["end_top_z"]), (fin["root_radius"], fin["root_top_z"])],
                fin["y_range"][0], fin["y_range"][1]))
            parts.append(mesh_prism_y(
                f"arm_{index}_web",
                [(web["root_radius"], web["root_bottom_z"]), (web["end_radius"], web.get("end_bottom_z", 0.3)),
                 (web["end_radius"], 0.3), (web["root_radius"], 0.3)],
                -web["width"] / 2, web["width"] / 2))
    arm = union_all(parts, f"arm_{index}")
    return rotate_about_z(arm, index * 120.0)


# --------------------------------------------------------------------------
# Layout da baia de eletrônica (06-PENDENCIAS D2)
# --------------------------------------------------------------------------

def rotated_rect(cx: float, cy: float, dx: float, dy: float, angle_deg: float) -> list[tuple[float, float]]:
    """Cantos de um retângulo dx (ao longo do azimute) × dy, centrado em (cx, cy)."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    out = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        out.append((cx + sx * dx / 2 * ux + sy * dy / 2 * vx, cy + sx * dx / 2 * uy + sy * dy / 2 * vy))
    return out


def circle_rect(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    return rotated_rect(cx, cy, 2 * r, 2 * r, 0.0)


def polys_overlap(a: list[tuple[float, float]], b: list[tuple[float, float]], margin: float = 0.0) -> bool:
    """Teste de eixos separadores para dois polígonos convexos em planta."""
    for poly in (a, b):
        n = len(poly)
        for i in range(n):
            x0, y0 = poly[i]
            x1, y1 = poly[(i + 1) % n]
            nx, ny = -(y1 - y0), (x1 - x0)
            length = math.hypot(nx, ny)
            if length < 1e-12:
                continue
            nx, ny = nx / length, ny / length
            pa = [px * nx + py * ny for px, py in a]
            pb = [px * nx + py * ny for px, py in b]
            if max(pa) + margin <= min(pb) or max(pb) + margin <= min(pa):
                return False
    return True


def z_overlap(z1, z2) -> bool:
    return z1[0] < z2[1] - 1e-9 and z2[0] < z1[1] - 1e-9


def wall_slot_geometry(c: dict) -> dict:
    """Placa em pé contra a parede curva: a face traseira encosta nas bordas."""
    sp = P["spider"]
    ws = sp["bay_layout"]["wall_slot"]
    r_in = sp["electronics_bay_id"] / 2
    depth, width, height = c["size_xyz"]
    r_back = math.sqrt(r_in ** 2 - (width / 2) ** 2) - ws["wall_gap"]
    return {
        "r_back": r_back,
        "r_center": r_back - depth / 2,
        "guide_a0": r_back - ws["guide_depth"],
        "guide_a1": r_in + 0.5,
        "guide_offset": width / 2 + ws["board_clearance"] + ws["guide_thickness"] / 2,
    }


def bay_layout_components() -> list[dict]:
    """Envelopes dos componentes da baia em coordenadas do rotor (topo do cubo em Z = 0)."""
    sp = P["spider"]
    out = []
    for c in sp["bay_layout"]["components"]:
        comp = dict(c)
        mount = c.get("mount", "none")
        zb = float(c.get("z_bottom", 0.0))
        if mount == "wall_slot":
            depth, width, height = c["size_xyz"]
            az = c["wall_azimuth_deg"]
            g = wall_slot_geometry(c)
            cx, cy = polar(g["r_center"], az)
            comp["center_xy"] = [round(cx, 3), round(cy, 3)]
            comp["plan"] = rotated_rect(cx, cy, depth, width, az)
            comp["z_range"] = [zb, zb + height]
        elif "polygon_xy" in c:
            comp["plan"] = [tuple(pt) for pt in c["polygon_xy"]]
            comp["z_range"] = [zb, zb + c["height"]]
        elif "diameter" in c:
            cx, cy = c["center_xy"]
            comp["plan"] = circle_rect(cx, cy, c["diameter"] / 2)
            comp["z_range"] = [zb, zb + c["height"]]
        elif "size_xyz" in c:
            cx, cy = c["center_xy"]
            dx, dy, dz = c["size_xyz"]
            comp["plan"] = rotated_rect(cx, cy, dx, dy, 0.0)
            comp["z_range"] = [zb, zb + dz]
        else:
            comp["plan"] = None
            comp["z_range"] = None
        out.append(comp)
    return out


def bay_obstacles() -> list[dict]:
    """Volumes já ocupados na baia: berço, bateria, postes, pilha da porca, rasgo do hall."""
    sp = P["spider"]
    c = sp["battery_cradle"]
    ui = P["unverified_interfaces"]
    bat = ui["battery"]
    nut = ui["m6_nut"]
    obs = []
    half_w = c["pack_width_x"] / 2 + c["clearance"]
    half_l = c["pack_length_y"] / 2 + c["clearance"]
    obs.append({"id": "bateria", "plan": rotated_rect(0, 0, 2 * half_w, 2 * half_l, 0), "z_range": [c["rail_height"], c["rail_height"] + bat["height"]]})
    for sign in (-1, 1):
        x0 = sign * half_w
        x1 = sign * (half_w + c["side_wall_thickness"])
        obs.append({"id": "parede lateral do berço", "plan": rotated_rect((x0 + x1) / 2, 0, c["side_wall_thickness"], c["side_wall_length_y"], 0), "z_range": [0.0, c["side_wall_height"]]})
        y0 = sign * half_l
        y1 = sign * (half_l + c["end_tab_thickness"])
        obs.append({"id": "aba de topo do berço", "plan": rotated_rect(0, (y0 + y1) / 2, c["end_tab_width_x"], c["end_tab_thickness"], 0), "z_range": [0.0, c["end_tab_height"]]})
    for xr in c["rail_x_positions"]:
        obs.append({"id": "trilho", "plan": rotated_rect(xr, 0, c["rail_width"], c["rail_length_y"], 0), "z_range": [0.0, c["rail_height"]]})
    for px, py in lid_post_positions():
        obs.append({"id": "poste da tampa", "plan": circle_rect(px, py, sp["lid_post_diameter"] / 2 + sp["lid_post_ring_overlap"]), "z_range": [0.0, sp["electronics_bay_height"]]})
    nut_top = -sp["counterbore_depth"] + nut["washer_thickness"] + nut["height"]
    obs.append({"id": "arruela e porca do eixo", "plan": circle_rect(0, 0, nut["washer_od"] / 2), "z_range": [-sp["counterbore_depth"], nut_top]})
    hs = sp["hall_sensor"]
    slot_r = hs["radius"] - hs["pocket_radial"] / 2 + hs["lead_slot_radial"] / 2 + 0.3
    hx, hy = polar(slot_r, hs["azimuth_deg"])
    obs.append({"id": "rasgo dos terminais do hall", "plan": rotated_rect(hx, hy, hs["lead_slot_radial"] + 1.0, hs["lead_slot_tangential"] + 1.0, hs["azimuth_deg"]), "z_range": [0.0, 1.0], "floor_only": True})
    return obs


def bay_wire_lanes() -> list[dict]:
    """Faixas do piso, do centro à janela de cada braço, que os feixes ocupam."""
    sp = P["spider"]
    wr = sp["wire_route"]
    wl = sp["bay_layout"]["wire_lane"]
    y0 = wr["bay_window_y"][0] - wl["y_margin"]
    y1 = wr["bay_window_y"][1] + wl["y_margin"]
    r0 = wl["radial_from"]
    r1 = sp["electronics_bay_id"] / 2 + 0.5
    lanes = []
    for i in range(3):
        ang = i * 120.0
        pts = [rot_xy(r0, y0, ang), rot_xy(r1, y0, ang), rot_xy(r1, y1, ang), rot_xy(r0, y1, ang)]
        lanes.append({"id": f"feixe do braço {i + 1}", "plan": pts, "z_range": [0.0, wl["z_top"]]})
    return lanes


def standoff_points(comp: dict) -> list[tuple[float, float]]:
    st = P["spider"]["bay_layout"]["standoff"]
    cx, cy = comp["center_xy"]
    dx, dy, _ = comp["size_xyz"]
    inset = st["corner_inset"]
    return [(cx + sx * (dx / 2 - inset), cy + sy * (dy / 2 - inset)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def bay_layout_checks(components: list[dict]) -> dict:
    """Envelope, interferências e faixas dos feixes, em planta e em Z."""
    sp = P["spider"]
    bl = sp["bay_layout"]
    r_in = sp["electronics_bay_id"] / 2
    h_bay = sp["electronics_bay_height"]
    st = bl["standoff"]
    problems: list[str] = []
    obstacles = bay_obstacles()
    lanes = bay_wire_lanes()
    solids = [c for c in components if c.get("plan")]
    for c in solids:
        limit = r_in + 0.05 if c.get("mount") == "wall_slot" else r_in - 0.5
        if "diameter" in c:
            extra = bl["ring_fence"]["clearance"] + bl["ring_fence"]["wall"] if c.get("mount") == "ring_fence" else 0.0
            rmax = math.hypot(*c["center_xy"]) + c["diameter"] / 2 + extra
        else:
            rmax = max(math.hypot(x, y) for x, y in c["plan"])
        if rmax > limit + 1e-6:
            problems.append(f"{c['id']}: canto em r = {rmax:.1f} > {limit:.1f}")
        if c["z_range"][1] > h_bay - 1.0:
            problems.append(f"{c['id']}: topo em Z = {c['z_range'][1]:.1f} > {h_bay - 1.0:.1f}")
        for o in obstacles:
            if o.get("floor_only") and c["z_range"][0] >= 1.0:
                continue
            if z_overlap(c["z_range"], o["z_range"]) and polys_overlap(c["plan"], o["plan"]):
                problems.append(f"{c['id']} interfere com {o['id']}")
        if c["z_range"][0] < bl["wire_lane"]["z_top"]:
            for lane in lanes:
                if polys_overlap(c["plan"], lane["plan"]):
                    problems.append(f"{c['id']} ocupa a {lane['id']} no piso")
    for i in range(len(solids)):
        for j in range(i + 1, len(solids)):
            a, b = solids[i], solids[j]
            if z_overlap(a["z_range"], b["z_range"]) and polys_overlap(a["plan"], b["plan"], margin=1.0):
                problems.append(f"{a['id']} e {b['id']} a menos de 1 mm")
    pillars = []
    for c in solids:
        if c.get("mount") != "standoffs":
            continue
        for k, (px, py) in enumerate(standoff_points(c)):
            plan = circle_rect(px, py, st["diameter"] / 2)
            if math.hypot(px, py) + st["diameter"] / 2 > r_in + 0.3:
                problems.append(f"pilar {k} de {c['id']} fora da parede")
            for o in obstacles:
                if o["id"].startswith("parede lateral"):
                    continue  # fundir com a parede do berço é aceitável
                if o["z_range"][0] < c["z_range"][0] and polys_overlap(plan, o["plan"]):
                    problems.append(f"pilar {k} de {c['id']} interfere com {o['id']}")
            for lane in lanes:
                if polys_overlap(plan, lane["plan"]):
                    problems.append(f"pilar {k} de {c['id']} ocupa a {lane['id']}")
            pillars.append([round(px, 2), round(py, 2)])
    return {"ok": not problems, "problems": problems, "standoffs": pillars}


def measure_bay_intersections(spider: bpy.types.Object) -> dict:
    """Intersect component envelopes with the FINAL mesh, including arm roots.

    Touching the support plane is allowed; positive overlap above numerical
    tolerance is not. This complements, rather than replaces, envelope checks.
    """
    results = []
    for c in bay_layout_components():
        if not c.get("plan"):
            continue
        cx, cy = c["center_xy"]
        z0, z1 = c["z_range"]
        if "polygon_xy" in c:
            envelope = mesh_prism_z("audit_envelope", [tuple(pt) for pt in c["polygon_xy"]], z0, z1)
        elif "diameter" in c:
            envelope = cylinder("audit_envelope", c["diameter"] / 2, z1 - z0,
                                (cx, cy, (z0 + z1) / 2), vertices=32)
        else:
            envelope = cube("audit_envelope", tuple(c["size_xyz"]),
                            (cx, cy, (z0 + z1) / 2),
                            rotation_z_deg=c.get("wall_azimuth_deg", 0.0))
        sample = duplicate(spider, "audit_intersection")
        activate(sample)
        modifier = sample.modifiers.new("audit_exact", "BOOLEAN")
        modifier.operation = "INTERSECT"
        modifier.solver = "EXACT"
        modifier.object = envelope
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        volume = mesh_volume_centroid(sample)[0] if sample.data.polygons else 0.0
        results.append({"component": c["id"], "intersection_mm3": round(abs(volume), 6)})
        delete_object(sample)
        delete_object(envelope)
    tolerance = 0.001
    return {"ok": all(r["intersection_mm3"] <= tolerance for r in results),
            "tolerance_mm3": tolerance, "components": results,
            "method": "Boolean INTERSECT EXACT, final spider mesh versus component envelopes"}


def bay_balance(components: list[dict], stats: dict | None = None) -> dict:
    """Desbalanceamento estático nominal do rotor e contrapeso que o corrige.

    Revisão 08, item 11: a versão anterior somava só os cinco itens da baia e
    ignorava tudo o que o próprio CAD já mede. As peças impressas não são
    axissimétricas — a aranha tem pilares, ranhura do buck, cerca, rasgo do
    hall; a tampa tem a janela de acesso — e o `geometry_report` publica os
    centróides. Aranha e tampa passam individualmente de 8,4 g·mm;
    o hall soma 5,8 g·mm e também precisa entrar no vetor:

        aranha  (−0,125, 0,085) × 67,5 g = 10,2 g·mm
        tampa   (−0,947, 0)     × 10,1 g =  9,6 g·mm
        hall    r = 29, 20°     ×  0,2 g =  5,8 g·mm

    O bloqueador C corrige tudo no fim com o rotor real, mas o "contrapeso
    planejado" é vendido como correção grossa e não pode nascer de um vetor
    incompleto. `sources` mostra a decomposição.

    Estimativa, não medição: os centróides são de sólido maciço e a peça sai
    com infill. Serve para dimensionar o contrapeso, não para dispensar C.
    """
    sp = P["spider"]
    lp = sp["lightening_pockets"]
    cw = sp["bay_layout"]["counterweight"]

    sources: list[dict] = []
    ux = uy = 0.0
    total = 0.0
    for c in components:
        m = c["mass_g"]
        total += m
        ux += m * c["center_xy"][0]
        uy += m * c["center_xy"][1]
    sources.append({
        "id": "eletrônica da baia",
        "mass_g": round(total, 2),
        "u_g_mm": round(math.hypot(ux, uy), 1),
        "azimuth_deg": round(math.degrees(math.atan2(uy, ux)) % 360.0, 1),
    })
    electronics_mass = total

    # Peças impressas: centróide medido na malha pelo próprio gerador.
    if stats:
        for key, label in (("spider", "aranha (malha)"), ("lid", "tampa (malha)")):
            st = stats.get(key)
            if not st:
                continue
            m = st["estimated_mass_g"]
            cxp, cyp = st["centroid_mm"][0], st["centroid_mm"][1]
            ux += m * cxp
            uy += m * cyp
            sources.append({
                "id": label,
                "mass_g": round(m, 2),
                "centroid_xy_mm": [round(cxp, 3), round(cyp, 3)],
                "u_g_mm": round(m * math.hypot(cxp, cyp), 1),
                "azimuth_deg": round(math.degrees(math.atan2(cyp, cxp)) % 360.0, 1),
            })

    # Sensor hall nu, colado no bolso da face inferior do cubo.
    hs = sp["hall_sensor"]
    hall_mass = P["non_cad_masses_g"].get("hall_sensor_bare", 0.2)
    hx, hy = polar(hs["radius"], hs["azimuth_deg"])
    ux += hall_mass * hx
    uy += hall_mass * hy
    sources.append({
        "id": "sensor hall nu",
        "mass_g": hall_mass,
        "u_g_mm": round(hall_mass * hs["radius"], 1),
        "azimuth_deg": float(hs["azimuth_deg"]),
    })

    u = math.hypot(ux, uy)
    az_u = math.degrees(math.atan2(uy, ux)) % 360.0
    az_cw = (az_u + 180.0) % 360.0
    r_cw = lp["outer_radius"] - cw["pocket_radius_offset_mm"]

    centers = [(lp["first_center_deg"] + i * 360.0 / lp["count"]) % 360.0 for i in range(lp["count"])]
    def sep(a: float, b: float) -> float:
        return abs((a - b + 180.0) % 360.0 - 180.0)
    order = sorted(centers, key=lambda c: sep(az_cw, c))
    nearest, second = order[0], order[1]

    # O contrapeso vai onde há bolso. Com os alívios a 120° o vetor pedido cai
    # sempre entre dois deles: resolver as duas massas em vez de arredondar para
    # o bolso mais próximo, que é o que deixava resíduo (revisão de 03/09, §3.5).
    target = (-ux, -uy)
    split_needed = sep(az_cw, nearest) > 1e-6
    if split_needed:
        a1 = math.radians(nearest)
        a2 = math.radians(second)
        det = math.cos(a1) * math.sin(a2) - math.cos(a2) * math.sin(a1)
        m1 = (target[0] * math.sin(a2) - target[1] * math.cos(a2)) / det / r_cw
        m2 = (target[1] * math.cos(a1) - target[0] * math.sin(a1)) / det / r_cw
    else:
        m1, m2 = u / r_cw, 0.0
    placement = [
        {"pocket_center_deg": nearest, "mass_g": round(m1, 2), "radius_mm": r_cw},
        {"pocket_center_deg": second, "mass_g": round(m2, 2), "radius_mm": r_cw},
    ]
    placement = [q for q in placement if q["mass_g"] > 0.005]
    total_cw = sum(q["mass_g"] for q in placement)

    # Resíduo real do arranjo proposto, medido de volta a partir das massas.
    rx = ux + sum(q["mass_g"] * r_cw * math.cos(math.radians(q["pocket_center_deg"])) for q in placement)
    ry = uy + sum(q["mass_g"] * r_cw * math.sin(math.radians(q["pocket_center_deg"])) for q in placement)

    sector_area = math.radians(2 * lp["half_angle_deg"]) * (lp["outer_radius"] ** 2 - lp["inner_radius"] ** 2) / 2.0
    capacity = round(sector_area * lp["depth"] * cw["putty_density_g_cm3"] / 1000.0, 1)
    return {
        "electronics_mass_g": round(electronics_mass, 2),
        "allowance_g": P["non_cad_masses_g"]["onboard_electronics_allowance"],
        "sources": sources,
        "unbalance_vector_g_mm": [round(ux, 1), round(uy, 1)],
        "unbalance_g_mm": round(u, 1),
        "unbalance_azimuth_deg": round(az_u, 1),
        "admissible_g_mm": P["loads_from_spec"]["admissible_unbalance_g_mm"],
        "counterweight_azimuth_deg": round(az_cw, 1),
        "counterweight_placement": placement,
        "counterweight_mass_g": round(total_cw, 2),
        "counterweight_split": len(placement) > 1,
        "counterweight_radius_mm": r_cw,
        "residual_g_mm": round(math.hypot(rx, ry), 2),
        "residual_within_admissible": math.hypot(rx, ry) <= P["loads_from_spec"]["admissible_unbalance_g_mm"],
        "pocket_capacity_g": capacity,
        "counterweight_fits_pockets": all(q["mass_g"] <= capacity for q in placement),
        "note": "Estimativa: centróides de sólido maciço, massas de eletrônica de catálogo. Dimensiona o contrapeso do plano 1; não substitui o bloqueador C com o rotor real.",
    }


def build_bay_mounts() -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    """Pilares, guias e cercas impressos no piso da baia; devolve (sólidos, cortadores)."""
    sp = P["spider"]
    bl = sp["bay_layout"]
    st = bl["standoff"]
    ws = bl["wall_slot"]
    rf = bl["ring_fence"]
    solids: list[bpy.types.Object] = []
    cutters: list[bpy.types.Object] = []
    for c in bay_layout_components():
        mount = c.get("mount", "none")
        if mount == "standoffs":
            h = c["z_range"][0]
            for k, (px, py) in enumerate(standoff_points(c)):
                solids.append(cylinder(f"standoff_{c['id']}_{k}", st["diameter"] / 2, h + 0.1, (px, py, h / 2 - 0.05), vertices=24))
                cutters.append(cylinder(f"standoff_pilot_{c['id']}_{k}", st["pilot_hole_diameter"] / 2, st["pilot_hole_depth"] + 0.2, (px, py, h - st["pilot_hole_depth"] / 2 + 0.1), vertices=16))
        elif mount == "wall_slot":
            az = c["wall_azimuth_deg"]
            g = wall_slot_geometry(c)
            length = g["guide_a1"] - g["guide_a0"]
            a_center = (g["guide_a0"] + g["guide_a1"]) / 2
            tx, ty = -math.sin(math.radians(az)), math.cos(math.radians(az))
            for k, sign in enumerate((-1.0, 1.0)):
                gx, gy = polar(a_center, az)
                gx += sign * g["guide_offset"] * tx
                gy += sign * g["guide_offset"] * ty
                solids.append(cube(f"wall_guide_{c['id']}_{k}", (length, ws["guide_thickness"], ws["guide_height"] + 0.1), (gx, gy, ws["guide_height"] / 2 - 0.05), rotation_z_deg=az))
        elif mount == "ring_fence":
            cx, cy = c["center_xy"]
            r_id = c["diameter"] / 2 + rf["clearance"]
            fence = ring(f"ring_fence_{c['id']}", r_id + rf["wall"], r_id, -0.1, rf["height"])
            solids.append(translate(fence, cx, cy, 0.0))
    bs = sp.get("board_shelf", {})
    if bs.get("enabled"):
        # Mísulas a 45° na parede da baia: apoio da placa própria acima da bateria.
        r_wall = sp["electronics_bay_id"] / 2 + 0.5
        r_in = sp["electronics_bay_id"] / 2 - bs["radial_depth"]
        for k, az in enumerate(bs["azimuths_deg"]):
            corbel = mesh_prism_y(
                f"board_corbel_{k}",
                [(r_wall, bs["z"] - (r_wall - r_in) - 0.5), (r_wall, bs["z"]), (r_in, bs["z"]), (r_in, bs["z"] - 0.5)],
                -bs["width"] / 2, bs["width"] / 2)
            solids.append(rotate_about_z(corbel, az))
            px, py = polar(bs["screw_radius"], az)
            cutters.append(cylinder(f"board_corbel_pilot_{k}", bs["pilot_hole_diameter"] / 2, bs["pilot_hole_depth"] + 0.2,
                                    (px, py, bs["z"] - bs["pilot_hole_depth"] / 2 + 0.1), vertices=16))
    return solids, cutters


def lid_post_positions() -> list[tuple[float, float]]:
    """Centros dos dois postes da tampa, encostados na parede da baia."""
    q = P["spider"]
    half = q["lid_post_spacing"] / 2
    if q.get("lid_post_axis", "x") == "y":
        return [(0.0, -half), (0.0, half)]
    return [(-half, 0.0), (half, 0.0)]


def build_spider() -> bpy.types.Object:
    q = P["spider"]
    a = q["arm"]
    ui = P["unverified_interfaces"]
    hub_t = q["hub_thickness"]
    hub = cylinder("hub_disk", q["hub_diameter"] / 2, hub_t, (0.0, 0.0, -hub_t / 2))

    bay = ring("electronics_bay_wall", q["electronics_bay_od"] / 2, q["electronics_bay_id"] / 2, -0.1, q["electronics_bay_height"])
    post_positions = lid_post_positions()
    lid_posts = [
        cylinder(f"lid_post_{i}", q["lid_post_diameter"] / 2 + q["lid_post_ring_overlap"], q["electronics_bay_height"] + 0.1, (x, y, q["electronics_bay_height"] / 2 - 0.05))
        for i, (x, y) in enumerate(post_positions)
    ]

    # Berço da bateria (pack deitado ao longo de y).
    c = q["battery_cradle"]
    cradle: list[bpy.types.Object] = []
    for i, xr in enumerate(c["rail_x_positions"]):
        cradle.append(
            box_xyz(
                f"battery_rail_{i}",
                (xr - c["rail_width"] / 2, xr + c["rail_width"] / 2),
                (-c["rail_length_y"] / 2, c["rail_length_y"] / 2),
                (-0.1, c["rail_height"]),
            )
        )
    half_w = c["pack_width_x"] / 2 + c["clearance"]
    for i, sign in enumerate((-1.0, 1.0)):
        x0 = sign * half_w
        x1 = sign * (half_w + c["side_wall_thickness"])
        cradle.append(
            box_xyz(
                f"battery_side_wall_{i}",
                (min(x0, x1), max(x0, x1)),
                (-c["side_wall_length_y"] / 2, c["side_wall_length_y"] / 2),
                (-0.1, c["side_wall_height"]),
            )
        )
    half_l = c["pack_length_y"] / 2 + c["clearance"]
    for i, sign in enumerate((-1.0, 1.0)):
        y0 = sign * half_l
        y1 = sign * (half_l + c["end_tab_thickness"])
        cradle.append(
            box_xyz(
                f"battery_end_tab_{i}",
                (-c["end_tab_width_x"] / 2, c["end_tab_width_x"] / 2),
                (min(y0, y1), max(y0, y1)),
                (-0.1, c["end_tab_height"]),
            )
        )

    arms = [build_arm(i) for i in range(3)]
    mounts, mount_cutters = build_bay_mounts()
    spider = union_all([hub, bay, *lid_posts, *cradle, *mounts, *arms], "aranha")

    cutters: list[bpy.types.Object] = []
    bore_r = (q["bore_diameter"] + P["quality"]["fdm_bore_compensation_mm"]) / 2
    cutters.append(cylinder("hub_bore", bore_r, hub_t + 2.0, (0.0, 0.0, -hub_t / 2)))
    if q["counterbore_depth"] > 0.0:
        # Só existe se o colar do eixo ficar abaixo do fundo; hoje é zero (ver parameters).
        cutters.append(
            cylinder(
                "hub_counterbore",
                q["counterbore_diameter"] / 2,
                q["counterbore_depth"] + 0.2,
                (0.0, 0.0, -q["counterbore_depth"] / 2 + 0.1),
            )
        )
    cutters.extend(mount_cutters)
    adapter = ui["adapter_bolt_pattern"]
    if adapter["enabled"]:
        for i in range(adapter["count"]):
            x, y = polar(adapter["pcd"] / 2, adapter["angle_offset_deg"] + i * 360.0 / adapter["count"])
            cutters.append(cylinder(f"adapter_bolt_hole_{i}", adapter["hole_diameter"] / 2, hub_t + 2.0, (x, y, -hub_t / 2)))

    cs = q["cooling_slots"]
    for i in range(cs["count"]):
        center = cs["first_center_deg"] + i * 360.0 / cs["count"]
        cutters.append(
            annular_sector(
                f"cooling_slot_{i}",
                cs["inner_radius"],
                cs["outer_radius"],
                center - cs["arc_deg"] / 2,
                center + cs["arc_deg"] / 2,
                -hub_t - 0.5,
                0.5,
            )
        )

    lp = q["lightening_pockets"]
    for i in range(lp["count"]):
        center = lp["first_center_deg"] + i * 360.0 / lp["count"]
        cutters.append(
            annular_sector(
                f"lightening_pocket_{i}",
                lp["inner_radius"],
                lp["outer_radius"],
                center - lp["half_angle_deg"],
                center + lp["half_angle_deg"],
                -hub_t - 0.5,
                -hub_t + lp["depth"],
            )
        )

    hs = q["hall_sensor"]
    cutters.append(
        cube_polar(
            "hall_pocket",
            (hs["pocket_radial"], hs["pocket_tangential"], hs["pocket_depth"] + 0.5),
            hs["radius"],
            hs["azimuth_deg"],
            -hub_t + hs["pocket_depth"] / 2 - 0.25,
        )
    )
    slot_r = hs["radius"] - hs["pocket_radial"] / 2 + hs["lead_slot_radial"] / 2 + 0.3
    cutters.append(
        cube_polar(
            "hall_lead_slot",
            (hs["lead_slot_radial"], hs["lead_slot_tangential"], hub_t + 1.0),
            slot_r,
            hs["azimuth_deg"],
            -hub_t / 2,
        )
    )

    wr = q["wire_route"]
    for arm_i in range(3):
        angle = arm_i * 120.0
        for hole_i, radius in enumerate(a["screw_radii"]):
            x, y = polar(radius, angle)
            cutters.append(cylinder(f"arm_screw_{arm_i}_{hole_i}", a["screw_hole_diameter"] / 2, a["tenon_height"] + 3.0, (x, y, a["tenon_height"] / 2)))
        window = box_xyz(f"bay_wire_window_{arm_i}", tuple(wr["bay_window_radial"]), tuple(wr["bay_window_y"]), tuple(wr["bay_window_z"]))
        root_pocket = box_xyz(
            f"root_wire_pocket_{arm_i}",
            (wr["root_pocket_radial"][0], wr["root_pocket_radial"][1] + 0.2),
            tuple(wr["root_pocket_y"]),
            (wr["groove_floor_z"], a["height"] + 1.5),
        )
        groove = box_xyz(
            f"arm_wire_groove_{arm_i}",
            tuple(wr["groove_radial"]),
            tuple(wr["groove_y"]),
            (wr["groove_floor_z"], a["height"] + 1.5),
        )
        cutters.append(rotate_about_z(window, angle))
        cutters.append(rotate_about_z(root_pocket, angle))
        cutters.append(rotate_about_z(groove, angle))

    for i, (x, y) in enumerate(post_positions):
        depth = q["lid_post_hole_depth"]
        cutters.append(
            cylinder(
                f"lid_post_hole_{i}",
                q["lid_post_hole_diameter"] / 2,
                depth + 0.2,
                (x, y, q["electronics_bay_height"] - depth / 2 + 0.1),
            )
        )

    spider = subtract_each(spider, cutters, "spider_feature")
    spider.name = "01_aranha"
    return spider


# --------------------------------------------------------------------------
# 03 — Tampa da baia
# --------------------------------------------------------------------------

def build_lid() -> bpy.types.Object:
    q = P["lid"]
    skin = cylinder("lid_skin", q["diameter"] / 2, q["skin_thickness"], (0.0, 0.0, q["skin_thickness"] / 2))
    rim = ring("lid_rim", q["diameter"] / 2, q["diameter"] / 2 - q["rim_wall"], q["skin_thickness"] - 0.1, q["height"])
    parts = [skin, rim]
    bc = q["balance_cups"]
    for i in range(bc["count"]):
        x, y = polar(bc["radius"], bc["first_center_deg"] + i * 360.0 / bc["count"])
        cup = ring(f"lid_balance_cup_{i}", bc["outer_diameter"] / 2, bc["inner_diameter"] / 2, q["skin_thickness"] - 0.1, q["skin_thickness"] + bc["height"])
        parts.append(translate(cup, x, y, 0.0))
    lid = union_all(parts, "tampa")

    cutters = [
        cylinder(f"lid_screw_hole_{i}", q["screw_hole_diameter"] / 2, q["height"] + 0.4, (x, y, q["height"] / 2))
        for i, (x, y) in enumerate(lid_post_positions())
    ]
    if P["unverified_interfaces"]["lid_access_window"]["enabled"]:
        w = q["access_window"]
        cutters.append(box_xyz("lid_access_window", tuple(w["x_range"]), tuple(w["y_range"]), (-0.3, q["height"] + 0.3)))
    lid = subtract_each(lid, cutters, "lid_feature")
    lid.name = "03_tampa_baia"
    return lid


# --------------------------------------------------------------------------
# 04/05 — Base e torre integradas
# --------------------------------------------------------------------------

def containment_geometry() -> dict:
    """Canaleta de assento na pista externa e posição do cilindro de contenção (provisão)."""
    bt = P["base_tower"]
    seat = bt["containment_seat"]
    cont = P["unverified_interfaces"]["containment"]
    ring_r_in = bt["outer_ring_inner_diameter"] / 2
    ring_r_out = bt["footprint_diameter"] / 2
    r_cyl_in = cont["inner_diameter"] / 2
    r_cyl_out = r_cyl_in + cont["wall"]
    g_in = seat["groove_center_radius"] - seat["groove_width"] / 2
    g_out = seat["groove_center_radius"] + seat["groove_width"] / 2
    enabled = bool(seat["enabled"])
    floor_z = bt["outer_ring_height"] - seat["groove_depth"]
    rest_z = floor_z if enabled else bt["outer_ring_height"]
    clearance_in = r_cyl_in - g_in
    clearance_out = g_out - r_cyl_out
    return {
        "enabled": enabled,
        "in_scope": bool(cont.get("in_scope", False)),
        "cylinder_inner_diameter_mm": cont["inner_diameter"],
        "cylinder_outer_diameter_mm": 2 * r_cyl_out,
        "cylinder_wall_mm": cont["wall"],
        "cylinder_height_mm": cont["height"],
        "cylinder_has_floor": bool(cont["has_floor"]),
        "cylinder_has_top_cap": bool(cont.get("has_top_cap", False)),
        "cylinder_source": cont.get("source", ""),
        "cylinder_inner_radius": r_cyl_in,
        "groove_inner_radius_mm": round(g_in, 3),
        "groove_outer_radius_mm": round(g_out, 3),
        "groove_width_mm": seat["groove_width"],
        "groove_depth_mm": seat["groove_depth"],
        "groove_floor_z_mm": floor_z,
        "clearance_inner_mm": round(clearance_in, 3),
        "clearance_outer_mm": round(clearance_out, 3),
        "cylinder_fits_groove": bool(clearance_in >= 0.0 and clearance_out >= 0.0),
        "inner_lip_mm": round(g_in - ring_r_in, 3),
        "outer_lip_mm": round(ring_r_out - g_out, 3),
        "fits_track": bool(g_in - ring_r_in >= seat["min_lip"] and ring_r_out - g_out >= seat["min_lip"]),
        "rest_z_mm": rest_z,
        "top_z_mm": rest_z + cont["height"],
        "measured": bool(cont["verified"]),
    }


def build_base_tower() -> bpy.types.Object:
    q = P["base_tower"]
    bay_r = q["central_bay_od"] / 2
    bay_h = q["central_bay_height"]
    floor_z = q["central_floor_thickness"]
    central_outer = cylinder("central_bay_outer", bay_r, bay_h, (0.0, 0.0, bay_h / 2))
    # O interior da baia começa EXATAMENTE no topo do piso (Z = 4). A versão
    # anterior descia 0,05 mm e deixava a flange inferior (Z = 4…12) flutuando
    # sobre uma lâmina de ar de 0,05 mm — defeito apanhado pelo traçado de raios.
    central_inner = cylinder(
        "central_bay_inner",
        bay_r - q["central_bay_wall"],
        bay_h - floor_z + 0.2,
        (0.0, 0.0, (bay_h + floor_z) / 2 + 0.1),
    )
    central_bay = boolean(central_outer, central_inner, "DIFFERENCE", "central_bay_hollow")

    ring_r_out = q["footprint_diameter"] / 2
    outer_ring = ring("base_outer_ring", ring_r_out, q["outer_ring_inner_diameter"] / 2, 0.0, q["outer_ring_height"])
    rib_start = bay_r - 1.0
    rib_end = q["outer_ring_inner_diameter"] / 2 + 1.0
    ribs = [
        cube_polar(
            f"base_radial_rib_{i}",
            (rib_end - rib_start, q["radial_rib_width"], q["radial_rib_height"] + 0.2),
            (rib_start + rib_end) / 2,
            i * 360.0 / q["radial_rib_count"],
            q["radial_rib_height"] / 2,
        )
        for i in range(q["radial_rib_count"])
    ]

    # Abas de grampo na face externa do anel (B5), altura da pista.
    tabs: list[bpy.types.Object] = []
    ct = q["clamp_tabs"]
    if ct["enabled"]:
        r0 = ring_r_out - 1.0
        r1 = ring_r_out + ct["radial_length"]
        for i in range(ct["count"]):
            angle = ct["angle_offset_deg"] + i * 360.0 / ct["count"]
            tabs.append(
                cube_polar(
                    f"clamp_tab_{i}",
                    (r1 - r0, ct["width"], q["outer_ring_height"] + 0.2),
                    (r0 + r1) / 2,
                    angle,
                    q["outer_ring_height"] / 2,
                )
            )

    tower_top = floor_z + q["tower_total_height_from_floor"]
    # Torre e flange inferior entram 0,2 mm no piso para fundir com folga.
    tower = cylinder("tower_outer", q["tower_od"] / 2, tower_top - floor_z + 0.2, (0.0, 0.0, (floor_z + tower_top) / 2 - 0.1))
    bore_z0 = q["tower_bore_start_z"]
    lower_flange = cylinder("tower_lower_flange", q["flange_diameter"] / 2, q["flange_thickness"] + 0.2, (0.0, 0.0, floor_z + q["flange_thickness"] / 2 - 0.1))
    upper_flange = cylinder("tower_upper_flange", q["flange_diameter"] / 2, q["flange_thickness"], (0.0, 0.0, tower_top - q["flange_thickness"] / 2))
    base = union_all([central_bay, outer_ring, *ribs, *tabs, tower, lower_flange, upper_flange], "base_torre")
    # As nervuras e abas cruzam as peças adjacentes 0,1 mm em Z para evitar
    # faces coplanares internas. Este corte devolve uma única face de apoio plana.
    bottom_trim = cube("base_bottom_trim", (q["footprint_diameter"] + 80.0, q["footprint_diameter"] + 80.0, 20.0), (0.0, 0.0, -9.9999))
    base = boolean(base, bottom_trim, "DIFFERENCE", "base_flatten_bottom")

    cutters: list[bpy.types.Object] = []
    # Furo central da torre a partir de tower_bore_start_z; a janela lateral
    # liga a baia ao interior do tubo.
    cutters.append(cylinder("tower_bore", q["tower_od"] / 2 - q["tower_wall"], tower_top - bore_z0 + 1.0, (0.0, 0.0, (bore_z0 + tower_top) / 2 + 0.5)))
    ww = q["wire_window"]
    cutters.append(cube("tower_wire_window", tuple(ww["size_xyz"]), tuple(ww["center_xyz"])))

    # Furos M4 da chapa do motor: só na flange superior (B3). Antes o cortador
    # descia até z = -1 e abria quatro furos inúteis no piso sob a torre.
    flange_r = q["flange_hole_pcd"] / 2
    if q.get("flange_holes_upper_only", True):
        h_z0 = tower_top - q["flange_thickness"] - 1.0
        h_z1 = tower_top + 1.0
    else:
        h_z0 = -1.0
        h_z1 = tower_top + 1.0
    for i in range(4):
        x, y = polar(flange_r, q["flange_hole_angle_offset_deg"] + i * 90.0)
        cutters.append(cylinder(f"flange_hole_{i}", q["flange_hole_diameter"] / 2, h_z1 - h_z0, (x, y, (h_z0 + h_z1) / 2)))

    # Rebaixo para as cabeças dos 4 × M3 do motor (revisão de 03/09, item 3). Os M3
    # entram por baixo da chapa R01 e as cabeças ficam entre a chapa e a flange,
    # em r = 8 e 9,5 (cruz de diagonais 16 e 19). Sem este rebaixo a chapa apoia nas quatro cabeças e não na
    # flange, e o Datum B sai 2–3 mm alto. O piso do rebaixo olha para cima:
    # não acrescenta balanço à impressão.
    fmr = q.get("flange_motor_recess", {"enabled": False})
    if fmr.get("enabled"):
        cutters.append(
            cylinder(
                "flange_motor_head_recess",
                fmr["diameter"] / 2,
                fmr["depth"] + 1.0,
                (0.0, 0.0, tower_top - fmr["depth"] / 2 + 0.5),
            )
        )

    ph = q["peripheral_holes"]
    if ph["enabled"]:
        for i in range(ph["count"]):
            x, y = polar(ph["pcd"] / 2, ph["angle_offset_deg"] + i * 360.0 / ph["count"])
            cutters.append(cylinder(f"peripheral_hole_{i}", ph["diameter"] / 2, q["outer_ring_height"] + 0.4, (x, y, q["outer_ring_height"] / 2)))

    if ct["enabled"]:
        for i in range(ct["count"]):
            angle = ct["angle_offset_deg"] + i * 360.0 / ct["count"]
            x, y = polar(ct["hole_radius"], angle)
            cutters.append(cylinder(f"clamp_tab_hole_{i}", ct["hole_diameter"] / 2, q["outer_ring_height"] + 0.4, (x, y, q["outer_ring_height"] / 2)))

    lv = q["lateral_vents"]
    for i in range(lv["count"]):
        angle = lv["angle_offset_deg"] + i * 360.0 / lv["count"]
        cutters.append(
            cube_polar(
                f"bay_lateral_vent_{i}",
                (q["central_bay_wall"] + 3.0, lv["width"], lv["height"]),
                bay_r - q["central_bay_wall"] / 2,
                angle,
                lv["z_bottom"] + lv["height"] / 2,
            )
        )

    cg = containment_geometry()
    if cg["enabled"]:
        cutters.append(
            ring(
                "containment_seat_groove",
                cg["groove_outer_radius_mm"],
                cg["groove_inner_radius_mm"],
                cg["groove_floor_z_mm"],
                q["outer_ring_height"] + 0.5,
            )
        )

    base = subtract_each(base, cutters, "base_tower_opening")
    base.name = "04_05_base_torre_integradas"
    return base


# --------------------------------------------------------------------------
# Variante 3.1-P — base suspensa em paralelogramo
# --------------------------------------------------------------------------

def cylinder_radial(name: str, radius: float, r0: float, r1: float, az_deg: float, z: float) -> bpy.types.Object:
    """Cilindro com o eixo na direção radial `az_deg`, de r0 a r1, na cota z."""
    x, y = polar((r0 + r1) / 2, az_deg)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=r1 - r0, end_fill_type="NGON",
                                        location=(x, y, z), rotation=(0.0, math.pi / 2, math.radians(az_deg)))
    obj = bpy.context.object
    obj.name = name
    return apply_transform(obj)


def suspension_layout() -> dict:
    """Cotas derivadas da suspensão: blocos de baixo no aro do palco, de cima no anel fixo."""
    rod, blk, rim, hr = SUSP["rod"], SUSP["block"], SUSP["rim"], SUSP["hanger_ring"]
    z_bot0 = rim["z_range"][0]
    z_bot1 = z_bot0 + blk["height"]
    z_top0 = z_bot1 + rod["free_length"]
    z_top1 = z_top0 + blk["height"]
    if abs(z_top1 - hr["top_z"]) > 1e-6 or abs(z_bot1 - rim["z_range"][1]) > 1e-6:
        raise ValueError("Suspensão: blocos, haste e anéis não fecham em Z")
    st = SUSP["stops"]
    eva = st["eva"]
    hard_r = st["lug_tip_radius"] + st["travel"]
    return {
        "azimuths": [rod["first_azimuth_deg"] + i * 360.0 / rod["count"] for i in range(rod["count"])],
        "z_bot": (z_bot0, z_bot1), "z_top": (z_top0, z_top1),
        "face_r": rod["seat_face_radius"],
        "hard_stop_radius": hard_r,
        "pocket_depth": eva["pad_thickness"] - (st["travel"] - eva["engage_gap"]),
        "slot_width": st["lug_width"] + 2 * st["side_gap"],
    }


def seat_features(prefix: str, az: float, z_range: tuple[float, float], top_z: float, face: float | None = None, rails: bool = True) -> tuple[list[bpy.types.Object], list[bpy.types.Object]]:
    """Assento plano de um bloco: calço, guias laterais, furo radial M3 e rasgo da porca aberto para cima."""
    seat = SUSP["seat"]
    face = suspension_layout()["face_r"] if face is None else face
    zc = (z_range[0] + z_range[1]) / 2
    height = z_range[1] - z_range[0]
    solids = [cube_polar(f"{prefix}_pad", (4.0, seat["width"], height), face - 2.0, az, zc)]
    if rails:
        # Guias: o bloco entra num canal e não gira em torno do parafuso único.
        channel = SUSP["block"]["width"] + 2 * seat["block_side_clearance"]
        rail_w = (seat["width"] - channel) / 2
        cx, cy = polar(face + seat["rail_proud"] / 2 - 0.25, az)
        tx, ty = polar(1.0, az + 90.0)
        for k, sign in enumerate((-1.0, 1.0)):
            off = sign * (channel / 2 + rail_w / 2)
            solids.append(cube(f"{prefix}_rail_{k}", (seat["rail_proud"] + 0.5, rail_w, height), (cx + off * tx, cy + off * ty, zc), rotation_z_deg=az))
    # Furo passante: terminar o furo rente à face interna do anel deixaria uma película.
    bore = cylinder_radial(f"{prefix}_bore", seat["bore_diameter"] / 2, SUSP["rim"]["inner_radius"] - 1.5, face + 0.5, az, zc)
    n0, n1 = seat["nut_slot_radial"]
    z0 = zc - seat["nut_slot_below_axis"]
    slot = cube_polar(f"{prefix}_nut_slot", (n1 - n0, seat["nut_slot_width"], top_z + 0.2 - z0), face - (n0 + n1) / 2, az, (z0 + top_z + 0.2) / 2)
    return solids, [bore, slot]


def cable_hook_layout(hk: dict, tower_r: float) -> dict:
    """Cotas dos ganchos dos fios do motor no referencial local (x radial, y tangencial)."""
    d = hk["wire_od"]
    depth = d + hk["radial_clearance"]           # bolso: uma camada de fios encostada na torre
    width = hk["wire_count"] * d + hk["side_clearance"]
    x_in = tower_r - 2.5                          # raiz enterrada na torre
    x_pocket = tower_r + depth                    # face interna do dedo
    x_out = x_pocket + hk["finger_thickness"]
    y_tip = width / 2
    # Entrada sob o farpão, medida até a superfície REAL da torre no ponto da ponta (cilindro).
    tower_x_at_tip = math.sqrt(tower_r ** 2 - y_tip ** 2)
    barb = max(0.0, x_pocket - tower_x_at_tip - (d - hk["barb_interference"]))
    entry = x_pocket - barb - tower_x_at_tip
    span = width + hk["post_thickness"]
    height = span + hk["finger_min_height"]       # base a 45° nas duas direções: sem suporte
    count = int((hk["z_last"] - hk["z_first"]) // hk["pitch"]) + 1
    return {"depth": depth, "width": width, "x_in": x_in, "x_pocket": x_pocket, "x_out": x_out,
            "barb": barb, "entry": entry, "height": height, "count": count,
            "z0": [hk["z_first"] + i * hk["pitch"] for i in range(count)]}


def build_cable_hooks(hk: dict, tower_r: float) -> list[bpy.types.Object]:
    """Ganchos alternados para os três fios de fase, ao longo da torre (pedido de 13/11/2026).

    Cada gancho é um L em planta (poste radial + dedo tangencial) com farpão na ponta.
    Os ganchos abrem para lados alternados: o fio entra de lado e não tem por onde sair.
    A face de baixo sobe a 45° a partir da raiz, em x e em y: imprime em pé sem suporte.
    """
    lay = cable_hook_layout(hk, tower_r)
    w, tp = lay["width"], hk["post_thickness"]
    out = []
    for i, z0 in enumerate(lay["z0"]):
        s = 1.0 if i % 2 == 0 else -1.0           # +1: poste em -y, abre para +y
        z1 = z0 + lay["height"]
        y_post = (-w / 2 - tp, -w / 2) if s > 0 else (w / 2, w / 2 + tp)
        y_fing = (-w / 2 - tp, w / 2) if s > 0 else (-w / 2, w / 2 + tp)
        pieces = [
            box_xyz(f"hook_{i}_post", (lay["x_in"], lay["x_out"]), y_post, (z0, z1)),
            box_xyz(f"hook_{i}_finger", (lay["x_pocket"] - 0.05, lay["x_out"]), y_fing, (z0, z1)),
        ]
        if lay["barb"] > 0.05:
            yb = (w / 2 - hk["barb_length"], w / 2) if s > 0 else (-w / 2, -w / 2 + hk["barb_length"])
            pieces.append(box_xyz(f"hook_{i}_barb", (lay["x_pocket"] - lay["barb"], lay["x_pocket"] + 0.05), yb, (z0, z1)))
        hook = union_all(pieces, f"cable_hook_{i}")
        # Corte a 45° em x (balanço radial a partir da torre) e em y (dedo a partir do poste).
        xr = tower_r - 1.0
        cut_x = mesh_prism_y(f"hook_{i}_cut_x", [(xr - 10.0, z0 - 1.0), (lay["x_out"] + 1.0, z0 - 1.0), (lay["x_out"] + 1.0, z0 + lay["x_out"] + 1.0 - xr), (xr - 10.0, z0 - 10.0)], -w - tp - 2.0, w + tp + 2.0)
        yr = y_post[0] if s > 0 else y_post[1]
        far = yr + s * (w + tp + 2.0)
        cut_y = mesh_prism_x(f"hook_{i}_cut_y", [(yr - s * 1.0, z0 - 1.0), (far, z0 - 1.0), (far, z0 + abs(far - yr))], lay["x_in"] - 1.0, lay["x_out"] + 1.0)
        hook = boolean(hook, cut_x, "DIFFERENCE", f"hook_{i}_45x")
        hook = boolean(hook, cut_y, "DIFFERENCE", f"hook_{i}_45y")
        out.append(rotate_about_z(hook, hk["azimuth_deg"]))
    return out


def build_suspended_stage() -> bpy.types.Object:
    """Palco móvel: disco, 8 aletas que contraventam a torre, aro com assentos e orelhas, torre e flange."""
    q = P["base_tower"]
    lay = suspension_layout()
    zb, zt = SUSP["stage_bottom_z"], SUSP["stage_top_z"]
    top = tower_top_z()
    fin, rim, st = SUSP["fin"], SUSP["rim"], SUSP["stops"]
    hub = cylinder("stage_hub", SUSP["stage_hub_radius"], zt - zb, (0.0, 0.0, (zb + zt) / 2))
    tower = cylinder("tower_outer", q["tower_od"] / 2, top - zb - 0.2, (0.0, 0.0, (zb + top) / 2 + 0.1))
    upper_flange = cylinder("tower_upper_flange", q["flange_diameter"] / 2, q["flange_thickness"], (0.0, 0.0, top - q["flange_thickness"] / 2))
    parts = [hub, tower, upper_flange]
    cone_h = SUSP.get("flange_cone_height", 0.0)
    if cone_h > 0:
        # Cone a 45° sob a flange: sem ele a face inferior é um balanço plano de 10 mm.
        zf = top - q["flange_thickness"]
        parts.append(frustum("tower_flange_cone", q["tower_od"] / 2 - 0.5, q["tower_od"] / 2 - 0.5 + cone_h + 0.5, zf - cone_h - 0.5, zf + 0.1))
    for i in range(fin["count"]):
        blade = mesh_prism_y(
            f"stage_fin_{i}",
            [(fin["inner_radius"], zb), (fin["tip_radius"], zb), (fin["tip_radius"], fin["tip_z"]), (fin["inner_radius"], fin["top_z_at_tower"])],
            -fin["thickness"] / 2, fin["thickness"] / 2)
        parts.append(rotate_about_z(blade, fin["first_azimuth_deg"] + i * 360.0 / fin["count"]))
    parts.append(ring("stage_rim", rim["outer_radius"], rim["inner_radius"], rim["z_range"][0], rim["z_range"][1]))
    cutters: list[bpy.types.Object] = []
    for i, az in enumerate(lay["azimuths"]):
        solids, cut = seat_features(f"stage_seat_{i}", az, lay["z_bot"], rim["z_range"][1])
        parts.extend(solids)
        cutters.extend(cut)
    lock = SUSP.get("lock", {})
    if lock.get("enabled"):
        # Ressaltos da trava: mesmo assento com porca, sem guias, para o parafuso radial que vem da pista.
        for i, az in enumerate(lock["azimuths_deg"]):
            solids, cut = seat_features(f"stage_lock_{i}", az, lay["z_bot"], rim["z_range"][1], face=lock["boss_face_radius"], rails=False)
            parts.extend(solids)
            cutters.extend(cut)
    zc = (rim["z_range"][0] + rim["z_range"][1]) / 2
    for i, az in enumerate(st["azimuths_deg"]):
        r0 = rim["outer_radius"] - 1.0
        parts.append(cube_polar(f"stage_lug_{i}", (st["lug_tip_radius"] - r0, st["lug_width"], rim["z_range"][1] - rim["z_range"][0]), (r0 + st["lug_tip_radius"]) / 2, az, zc))
    cc = SUSP.get("cable_channel", {})
    z_flange = top - q["flange_thickness"]
    if cc.get("enabled"):
        # Calha em C para os fios do motor, por fora da torre (o cabo sai pela lateral do motor).
        r0 = q["tower_od"] / 2 - 1.0
        parts.append(cube_polar("cable_channel", (cc["outer_radius"] - r0, cc["width"], z_flange + 0.2 - zt), (r0 + cc["outer_radius"]) / 2, cc["azimuth_deg"], (zt + z_flange + 0.2) / 2 - 0.1))
        cutters.append(cube_polar("cable_channel_void", (cc["inner_outer_radius"] - cc["inner_radius"], cc["inner_width"], z_flange - zt), (cc["inner_radius"] + cc["inner_outer_radius"]) / 2, cc["azimuth_deg"], (zt + z_flange) / 2))
        cutters.append(cube_polar("cable_channel_slot", (q["flange_diameter"] / 2 + 1.0 - cc["inner_outer_radius"] + 0.5, cc["slot_width"], z_flange - zt), (cc["inner_outer_radius"] - 0.5 + q["flange_diameter"] / 2 + 1.0) / 2, cc["azimuth_deg"], (zt + z_flange) / 2))
    hk = SUSP.get("cable_hooks", {})
    if hk.get("enabled"):
        parts.extend(build_cable_hooks(hk, q["tower_od"] / 2))
    od = SUSP.get("oil_damper", {})
    if od.get("enabled"):
        # Pás do amortecedor: coluna que nasce na mesa e ponte até o aro (L invertido).
        pd = od["paddle"]
        z0, z1 = rim["z_range"]
        for i, az in enumerate(od["azimuths_deg"]):
            parts.append(cube_polar(f"damper_paddle_{i}", (pd["thickness"], pd["width"], z1 - z0), pd["inner_radius"] + pd["thickness"] / 2, az, (z0 + z1) / 2))
            # Ponte da coluna até a face INTERNA do aro (pá pendurada para dentro).
            r0 = pd["inner_radius"]
            r1 = rim["inner_radius"] + 1.0
            parts.append(cube_polar(f"damper_arm_{i}", (r1 - r0, pd["width"], pd["arm_z"][1] - pd["arm_z"][0]), (r0 + r1) / 2, az, sum(pd["arm_z"]) / 2))
    stage = union_all(parts, "palco_torre")

    bore_r = q["tower_od"] / 2 - q["tower_wall"]
    if bore_r > 0.5:
        bore_z0 = SUSP["tower_bore_start_z"]
        cutters.append(cylinder("tower_bore", bore_r, top - bore_z0 + 1.0, (0.0, 0.0, (bore_z0 + top) / 2 + 0.5)))
    ww = SUSP["tower_wire_window"]
    if ww.get("enabled", True):
        r_w0, r_w1 = bore_r - 2.0, q["tower_od"] / 2 + 4.0
        cutters.append(cube_polar("tower_wire_window", (r_w1 - r_w0, ww["width"], ww["z_range"][1] - ww["z_range"][0]), (r_w0 + r_w1) / 2, ww["azimuth_deg"], (ww["z_range"][0] + ww["z_range"][1]) / 2))
    h_z0 = top - q["flange_thickness"] - 1.0
    for i in range(4):
        x, y = polar(q["flange_hole_pcd"] / 2, q["flange_hole_angle_offset_deg"] + i * 90.0)
        cutters.append(cylinder(f"flange_hole_{i}", q["flange_hole_diameter"] / 2, top + 1.0 - h_z0, (x, y, (h_z0 + top + 1.0) / 2)))
    fmr = q.get("flange_motor_recess", {"enabled": False})
    if fmr.get("enabled"):
        cutters.append(cylinder("flange_motor_head_recess", fmr["diameter"] / 2, fmr["depth"] + 1.0, (0.0, 0.0, top - fmr["depth"] / 2 + 0.5)))
    stage = subtract_each(stage, cutters, "stage_opening")
    stage.name = "05_palco_torre"
    return stage


def build_suspension_frame() -> bpy.types.Object:
    """Base fixa: anel da pista, casca cônica, anel superior com os assentos e batentes com bolso de EVA.

    Modelada na posição de uso (pista em Z = 0). Imprime INVERTIDA, com o teto na
    mesa: todos os balanços ficam em 45° ou menos e as janelas viram pontes de 14 mm.
    """
    q = P["base_tower"]
    lay = suspension_layout()
    sh, hr, st = SUSP["shell"], SUSP["hanger_ring"], SUSP["stops"]
    r_out = q["footprint_diameter"] / 2
    r_in = q["outer_ring_inner_diameter"] / 2
    h = q["outer_ring_height"]
    zc, zt = sh["chamfer_top_z"], hr["top_z"]
    r_cone_bot = r_in + sh["wall"]
    r_cone_top = sh["top_outer_radius"]
    track = cylinder("frame_track", r_out, h + 0.1, (0.0, 0.0, h / 2 - 0.05))
    chamfer = frustum("frame_chamfer", r_out, r_cone_bot, h - 0.05, zc)
    cone = frustum("frame_cone", r_cone_bot, r_cone_top, zc - 0.05, zt)
    shell = union_all([track, chamfer, cone], "frame_shell")
    z_roof = zt - sh["roof_thickness"]
    r_cav_top = r_in + (r_cone_top - sh["wall"] - r_in) * (z_roof - zc) / (zt - zc)
    shell = subtract_each(shell, [
        cylinder("frame_cavity_low", r_in, zc + 1.0, (0.0, 0.0, zc / 2 - 0.5)),
        frustum("frame_cavity_cone", r_in, r_cav_top, zc - 0.05, z_roof),
        cylinder("frame_roof_opening", hr["inner_radius"], sh["roof_thickness"] + 1.0, (0.0, 0.0, zt - sh["roof_thickness"] / 2)),
    ], "frame_cavity")
    parts = [shell, ring("frame_hanger_ring", hr["outer_radius"], hr["inner_radius"], zt - hr["height"], zt)]

    # Perfil da casca, para enterrar na parede tudo o que é prisma plano encostado nela.
    # Um prisma de faces planas tem os cantos mais longe do eixo que o centro
    # (sqrt(x² + y²)); se o perfil não for seguido, a face plana aflora na casca
    # (retângulo dos batentes) ou a aresta interna fica de pé fora do cone
    # (espigão e entalhe em V das mãos-francesas) — relato de 12/11/2026.
    def outer_r(z: float) -> float:
        if z <= h:
            return r_out
        if z <= zc:
            return r_out + (r_cone_bot - r_out) * (z - h) / (zc - h)
        return r_cone_bot + (r_cone_top - r_cone_bot) * (z - zc) / (zt - zc)

    def inner_r(z: float) -> float:
        return r_in if z <= zc else r_in + (r_cav_top - r_in) * (z - zc) / (z_roof - zc)

    def buried_x(z: float, half_w: float, margin: float) -> float:
        """Raio local (no eixo do prisma) que põe o canto a `margin` para dentro da face externa."""
        return math.sqrt((outer_r(z) - margin) ** 2 - half_w ** 2)

    def meet_profile(p0: tuple[float, float], p1: tuple[float, float], half_w: float, margin: float) -> tuple[float, float]:
        """Ponto do segmento p0→p1 (p0 fora, p1 dentro) onde o canto cruza a casca recuada de `margin`."""
        def outside(t: float) -> bool:
            x, z = p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1])
            return math.hypot(x, half_w) > outer_r(z) - margin
        if not outside(0.0) or outside(1.0):
            raise ValueError("Base fixa: segmento não cruza o perfil da casca")
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if outside(mid) else (lo, mid)
        return (p0[0] + hi * (p1[0] - p0[0]), p0[1] + hi * (p1[1] - p0[1]))

    bury = SUSP["shell"].get("bury_margin", 0.6)
    cutters: list[bpy.types.Object] = []
    for i, az in enumerate(lay["azimuths"]):
        solids, cut = seat_features(f"frame_seat_{i}", az, lay["z_top"], zt)
        parts.extend(solids)
        cutters.extend(cut)
        # Rampa de entrada sob o calço: o bloco sobe por baixo sem topar na aresta.
        li = SUSP["seat"]["lead_in"]
        ramp = mesh_prism_y(f"frame_seat_ramp_{i}", [(lay["face_r"] - li, lay["z_top"][0] - li), (lay["face_r"], lay["z_top"][0] + 0.1), (lay["face_r"] - li, lay["z_top"][0] + 0.1)], -SUSP["seat"]["width"] / 2, SUSP["seat"]["width"] / 2)
        parts.append(rotate_about_z(ramp, az))
        zb_mid = sum(lay["z_bot"]) / 2
        cutters.append(cylinder_radial(f"frame_access_{i}", sh["access_hole_diameter"] / 2, r_in - 3.0, r_out + 2.0, az, zb_mid))
        # A janela começa DEPOIS das guias; entre a face e o fim das guias só o canal do bloco é aberto
        # (a janela larga começando na face apagava as guias de cima — reverificação de 11/11/2026).
        seat = SUSP["seat"]
        r_rail = lay["face_r"] + seat["rail_proud"]
        r1 = sh["window_outer_radius"]
        zw = (sh["window_bottom_z"] + zt + 1.0) / 2
        hw = zt + 1.0 - sh["window_bottom_z"]
        cutters.append(cube_polar(f"frame_window_{i}", (r1 - r_rail, sh["window_width"], hw), (r_rail + r1) / 2, az, zw))
        channel = SUSP["block"]["width"] + 2 * seat["block_side_clearance"]
        cutters.append(cube_polar(f"frame_window_channel_{i}", (seat["rail_proud"] + 0.2, channel, hw), lay["face_r"] + seat["rail_proud"] / 2 + 0.05, az, zw))

    ct = q["clamp_tabs"]
    if ct["enabled"]:
        r0, r1 = r_out - 1.0, r_out + ct["radial_length"]
        gh = SUSP["clamp_tab_gusset_height"]
        for i in range(ct["count"]):
            az = ct["angle_offset_deg"] + i * 360.0 / ct["count"]
            parts.append(cube_polar(f"clamp_tab_{i}", (r1 - r0, ct["width"], h + 0.1), (r0 + r1) / 2, az, h / 2 - 0.05))
            # Duas mãos-francesas nas bordas da aba: apoio a 45° na impressão invertida,
            # deixando livre a região do furo para a cabeça do parafuso ou o grampo.
            for k, (y0, y1) in enumerate(((-ct["width"] / 2, -ct["width"] / 2 + 4.0), (ct["width"] / 2 - 4.0, ct["width"] / 2))):
                rw = r_in + 0.3  # raiz enterrada na casca
                # Aresta de cima a 45° até entrar na casca; dali a raiz desce pelo meio da parede.
                # Antes a raiz era uma aresta vertical em rw até Z = h + gh + (r0 - rw): acima de
                # Z ≈ 23 o cone recua para dentro de rw e a raiz ficava de pé fora da casca.
                p_out = (r1 - 0.3, h - 0.1)
                apex = (rw, h + gh + (r0 - rw))
                deep = (p_out[0] + 2.0 * (apex[0] - p_out[0]), p_out[1] + 2.0 * (apex[1] - p_out[1]))
                xm, zm = meet_profile(p_out, deep, ct["width"] / 2, bury)
                if zm <= zc:
                    raise ValueError("Base fixa: mão-francesa entra na casca abaixo do chanfro")
                x_mid = (inner_r(zm) + outer_r(zm)) / 2 - 0.2
                web = mesh_prism_y(f"clamp_tab_web_{i}_{k}", [(rw, h - 2.0), (r1 - 0.3, h - 2.0), p_out, (xm, zm), (x_mid, zm), (rw, zc)], y0, y1)
                parts.append(rotate_about_z(web, az))
            x, y = polar(ct["hole_radius"], az)
            cutters.append(cylinder(f"clamp_tab_hole_{i}", ct["hole_diameter"] / 2, h + 0.6, (x, y, h / 2)))

    eva = st["eva"]
    for i, az in enumerate(st["azimuths_deg"]):
        r_a, r_b = st["cheek_inner_radius"], st["block_outer_radius"]
        low = st["block_low_z"]
        # Face externa do bloco segue o chanfro e o cone por dentro da parede (cantos em ±block_width/2
        # a `bury` da face externa). Antes era plana em r_b até zc e o teto a 45° terminava em r_b - 2,5:
        # os cantos aforavam 0,1 a 0,5 mm na casca e apareciam como um retângulo plano.
        hw_b = st["block_width"] / 2
        z_knee = h + (r_out - (math.hypot(r_b, hw_b) + bury)) / (r_out - r_cone_bot) * (zc - h)
        z_knee = min(max(z_knee, h), zc)
        top_far = (r_b + 20.0, low + (r_b + 20.0 - r_a))
        x_top, z_top = meet_profile(top_far, (r_a, low), hw_b, bury)
        if z_top <= zc:
            raise ValueError("Base fixa: teto do batente encontra a casca abaixo do chanfro")
        outline = [(r_a, -0.1), (r_b, -0.1), (r_b, z_knee), (buried_x(zc, hw_b, bury), zc)]
        outline += [(buried_x(z, hw_b, bury), z) for z in (zc + 0.5 * (z_top - zc),) ]
        outline += [(x_top, z_top), (r_a, low)]
        wedge = mesh_prism_y(f"frame_stop_{i}", outline, -hw_b, hw_b)
        parts.append(rotate_about_z(wedge, az))
        hard = lay["hard_stop_radius"]
        # O rasgo termina lip_gap acima da orelha: o próprio batente vira limitador de inclinação.
        z_roof_slot = SUSP["rim"]["z_range"][1] + st["lip_gap"]
        cutters.append(cube_polar(f"frame_stop_slot_{i}", (hard - r_a + 0.5, lay["slot_width"], z_roof_slot + 5.0), (hard + r_a - 0.5) / 2, az, (z_roof_slot - 5.0) / 2))
        js = st.get("jack_screw", {})
        if js.get("enabled"):
            jx, jy = polar(js["radius"], az)
            z_under = SUSP["rim"]["z_range"][1]
            cutters.append(cylinder(f"frame_jack_pilot_{i}", js["pilot_diameter"] / 2, 30.0, (jx, jy, z_under + 15.0), vertices=16))
            cutters.append(cylinder(f"frame_jack_access_{i}", js["access_diameter"] / 2, zt + 1.0 - 36.0, (jx, jy, (36.0 + zt + 1.0) / 2), vertices=24))
        depth = lay["pocket_depth"]
        cutters.append(cube_polar(f"frame_eva_pocket_{i}", (depth + 0.2, lay["slot_width"], eva["pad_height"]), hard + depth / 2 - 0.1, az, eva["pocket_z0"] + eva["pad_height"] / 2))

    lock = SUSP.get("lock", {})
    if lock.get("enabled"):
        zl = sum(lay["z_bot"]) / 2
        for i, az in enumerate(lock["azimuths_deg"]):
            cutters.append(cylinder_radial(f"frame_lock_hole_{i}", lock["hole_diameter"] / 2, r_in - 3.0, r_out + 2.0, az, zl))
            cutters.append(cylinder_radial(f"frame_lock_counterbore_{i}", lock["counterbore_diameter"] / 2, lock["counterbore_from_radius"], r_out + 2.0, az, zl))
    ce = SUSP.get("cable_exit", {})
    if ce.get("enabled"):
        cutters.append(cube_polar("frame_cable_exit", (r_out + 2.0 - (r_in - 3.0), ce["width"], ce["height"] + 1.0), (r_out + 2.0 + r_in - 3.0) / 2, ce["azimuth_deg"], (ce["height"] - 1.0) / 2))
    frame = union_all(parts, "base_fixa")
    frame = boolean(frame, cube("frame_bottom_trim", (q["footprint_diameter"] + 80.0, q["footprint_diameter"] + 80.0, 20.0), (0.0, 0.0, -9.9999)), "DIFFERENCE", "frame_flatten_bottom")
    if containment_geometry()["enabled"]:
        raise ValueError("Variante suspensa: o chanfro da casca cobre a pista; desligue base_tower.containment_seat.enabled")
    frame = subtract_each(frame, cutters, "frame_feature")
    frame.name = "04_base_fixa"
    return frame


def build_flexure(side: float, name: str) -> bpy.types.Object:
    """Haste flexível com um bloco em cada ponta, na posição de uso do azimute 0.

    A face de assento (x = raio do assento) é a face que vai na mesa: a haste de
    seção quadrada sai nas primeiras camadas, com os fios ao longo do comprimento.
    """
    lay = suspension_layout()
    blk, rod = SUSP["block"], SUSP["rod"]
    face = lay["face_r"]
    parts = []
    for tag, (z0, z1) in (("bot", lay["z_bot"]), ("top", lay["z_top"])):
        parts.append(box_xyz(f"flexure_{name}_block_{tag}", (face, face + blk["thickness"]), (-blk["width"] / 2, blk["width"] / 2), (z0, z1)))
    zb, zt = lay["z_bot"][1], lay["z_top"][0]
    parts.append(box_xyz(f"flexure_{name}_rod", (face, face + side), (-side / 2, side / 2), (zb - 0.2, zt + 0.2)))
    bl = rod["blend_length"]
    half = blk["width"] / 2
    parts.append(mesh_prism_x(f"flexure_{name}_blend_bot", [(-half, zb - 0.1), (half, zb - 0.1), (side / 2, zb + bl), (-side / 2, zb + bl)], face, face + side))
    parts.append(mesh_prism_x(f"flexure_{name}_blend_top", [(-side / 2, zt - bl), (side / 2, zt - bl), (half, zt + 0.1), (-half, zt + 0.1)], face, face + side))
    flexure = union_all(parts, f"haste_{name}")
    cutters = [cylinder_radial(f"flexure_{name}_hole_{tag}", blk["hole_diameter"] / 2, face - 0.5, face + blk["thickness"] + 0.5, 0.0, (z0 + z1) / 2)
               for tag, (z0, z1) in (("bot", lay["z_bot"]), ("top", lay["z_top"]))]
    flexure = subtract_each(flexure, cutters, "flexure_hole")
    flexure.name = f"08_haste_flexivel_{name}"
    return flexure


def build_lock_spacer() -> bpy.types.Object:
    """Espaçador da trava: tubo entre a pista da base fixa e o ressalto do aro do palco."""
    lock = SUSP["lock"]
    length = P["base_tower"]["outer_ring_inner_diameter"] / 2 - lock["boss_face_radius"] - lock["spacer_clearance"]
    del length
    # Bucha com flange: entra por fora pela pista, a flange assenta no rebaixo e o corpo encosta no ressalto do aro.
    body_len = lock["counterbore_from_radius"] - lock["boss_face_radius"] - lock["spacer_clearance"]
    ft = lock["flange_thickness"]
    flange = cylinder("lock_bush_flange", lock["flange_diameter"] / 2, ft, (0.0, 0.0, ft / 2), vertices=48)
    body = cylinder("lock_bush_body", lock["spacer_od"] / 2, body_len + 0.1, (0.0, 0.0, ft + body_len / 2 - 0.05), vertices=48)
    spacer = boolean(flange, body, "UNION", "lock_bush_union")
    spacer = boolean(spacer, cylinder("lock_bush_bore", lock["screw_hole_diameter"] / 2, ft + body_len + 2.0, (0.0, 0.0, (ft + body_len) / 2), vertices=32), "DIFFERENCE", "lock_bush_bore")
    spacer.name = "09_bucha_trava"
    return spacer


def build_oil_tray() -> bpy.types.Object:
    """Bandeja do amortecedor viscoso: anel fino com quatro cubas e quatro linguetas de localização.

    Fica na mesa, sob o palco (que flutua a 4 mm). As linguetas entram por baixo nos
    rasgos dos batentes e encostam no fundo deles: centram a bandeja e a impedem de girar.
    """
    od = SUSP["oil_damper"]
    cup, tray = od["cup"], od["tray"]
    c0, c1 = cup["cavity_radial"]
    hw, w, fl = cup["cavity_half_width"], cup["wall"], cup["floor"]
    parts = [ring("oil_tray_ring", c1 + w, c0 - w, 0.0, fl)]
    cutters = []
    r_end = suspension_layout()["hard_stop_radius"] - tray["tongue_end_clearance"]
    for i, az in enumerate(od["azimuths_deg"]):
        # Setores de anel: nenhum canto passa do raio externo da cuba.
        ha = cup["cavity_half_angle_deg"]
        wa = math.degrees(w / c0)
        parts.append(annular_sector(f"oil_cup_body_{i}", c0 - w, c1 + w, az - ha - wa, az + ha + wa, fl - 0.1, cup["wall_top_z"]))
        cutters.append(annular_sector(f"oil_cup_cavity_{i}", c0, c1, az - ha, az + ha, fl, cup["wall_top_z"] + 1.0))
        parts.append(cube_polar(f"oil_tray_tongue_{i}", (r_end - c1, tray["tongue_width"], fl), (r_end + c1) / 2, az, fl / 2))
    part = subtract_each(union_all(parts, "bandeja_amortecedor"), cutters, "oil_tray_cavity")
    part.name = "10_bandeja_amortecedor"
    return part


def measure_suspension(frame: bpy.types.Object, stage: bpy.types.Object) -> dict:
    """Curso, folgas e assentos medidos nas malhas finais da base fixa e do palco."""
    lay = suspension_layout()
    st, eva, hr = SUSP["stops"], SUSP["stops"]["eva"], SUSP["hanger_ring"]
    fr = MeshProbe(triangles_of(frame))
    sg = MeshProbe(triangles_of(stage))
    out: dict = {}
    az = st["azimuths_deg"][0]
    dx, dy = polar(1.0, az)
    tx, ty = -dy, dx
    z_lug = sum(SUSP["rim"]["z_range"]) / 2
    r_start = SUSP["rim"]["outer_radius"] + 1.0
    # Orelha do palco: último material ao longo do raio do batente.
    runs = sg.solid_runs((dx * 100.0, dy * 100.0, z_lug), (dx, dy, 0.0), 40.0)
    lug_tip = 100.0 + runs[-1][1] if runs else None
    # Batente rígido: primeiro material acima do bolso de EVA; fundo do bolso na cota da orelha.
    # Sondado NA ALTURA DA ORELHA, acima do bolso: é ali que a orelha encosta sem EVA.
    z_hard = SUSP["rim"]["z_range"][1] - 1.0
    if not eva["pocket_z0"] + eva["pad_height"] < z_hard:
        raise ValueError("Bolso de EVA cobre a orelha inteira: o batente rígido ficaria inalcançável")
    runs = fr.solid_runs((dx * r_start, dy * r_start, z_hard), (dx, dy, 0.0), 30.0)
    hard = r_start + runs[0][0] if runs else None
    z_pocket = eva["pocket_z0"] + eva["pad_height"] / 2
    runs = fr.solid_runs((dx * r_start, dy * r_start, z_pocket), (dx, dy, 0.0), 30.0)
    pocket = r_start + runs[0][0] if runs else None
    # Limitador de inclinação: teto do rasgo acima da orelha.
    r_lip = st["lug_tip_radius"] - 2.0
    # Deslocado 2,5 mm na tangente: no centro fica o furo do parafuso de trava vertical.
    runs = fr.solid_runs((dx * r_lip + tx * 2.5, dy * r_lip + ty * 2.5, SUSP["rim"]["z_range"][1] + 0.01), (0.0, 0.0, 1.0), 20.0)
    out["tilt_lip_gap_mm"] = round(runs[0][0] + 0.01, 3) if runs else None
    # Pior eixo: a 45° dos batentes, onde o braço de alavanca das orelhas cai para r·cos 45°.
    out["tilt_cap_deg"] = round(math.degrees(math.atan((runs[0][0] + 0.01) / (st["lug_tip_radius"] * math.cos(math.radians(45.0))))), 3) if runs else None
    out["cheek_overlap_at_full_travel_mm"] = round(st["lug_tip_radius"] - st["travel"] - st["cheek_inner_radius"], 3)
    r_mid = st["lug_tip_radius"] - 2.0
    runs = fr.solid_runs((dx * r_mid, dy * r_mid, z_lug), (tx, ty, 0.0), 20.0)
    cheek = runs[0][0] if runs else None
    runs = sg.solid_runs((dx * r_mid - tx * 10.0, dy * r_mid - ty * 10.0, z_lug), (tx, ty, 0.0), 20.0)
    lug_half = (runs[0][1] - runs[0][0]) / 2 if runs else None
    out["lug_tip_radius_mm"] = round(lug_tip, 3) if lug_tip is not None else None
    out["hard_stop_radius_mm"] = round(hard, 3) if hard is not None else None
    out["eva_pocket_floor_radius_mm"] = round(pocket, 3) if pocket is not None else None
    if None not in (lug_tip, hard, pocket, cheek, lug_half):
        out["radial_travel_mm"] = round(hard - lug_tip, 3)
        out["eva_engage_gap_mm"] = round(pocket - eva["pad_thickness"] - lug_tip, 3)
        out["tangential_gap_mm"] = round(cheek - lug_half, 3)
    # Furos dos assentos livres, em cima (base) e em baixo (palco), em todos os azimutes.
    seat = SUSP["seat"]
    free_top, free_bot = [], []
    for a in lay["azimuths"]:
        ux, uy = polar(1.0, a)
        r0 = lay["face_r"] - seat["bore_depth"] + 0.6
        length = seat["bore_depth"] - 1.0
        free_top.append(fr.is_void((ux * r0, uy * r0, sum(lay["z_top"]) / 2), (ux, uy, 0.0), length))
        free_bot.append(sg.is_void((ux * r0, uy * r0, sum(lay["z_bot"]) / 2), (ux, uy, 0.0), length))
    # Canal entre as guias, medido em cima (base fixa) e em baixo (palco), no primeiro azimute.
    ux, uy = polar(1.0, lay["azimuths"][0])
    vx, vy = -uy, ux
    r_ch = lay["face_r"] + seat["rail_proud"] / 2
    widths = []
    for probe, z in ((fr, sum(lay["z_top"]) / 2), (sg, sum(lay["z_bot"]) / 2)):
        halves = []
        for sign in (1.0, -1.0):
            runs = probe.solid_runs((ux * r_ch, uy * r_ch, z), (sign * vx, sign * vy, 0.0), 12.0)
            halves.append(runs[0][0] if runs else None)
        widths.append(round(halves[0] + halves[1], 3) if None not in halves else None)
    out["seat_channel_width_top_bottom_mm"] = widths
    out["frame_seat_bores_free"] = free_top
    out["stage_seat_bores_free"] = free_bot
    # Passagem do palco por baixo: maior raio do palco fora das orelhas contra o menor raio dos batentes.
    out["stage_rim_outer_radius_mm"] = SUSP["rim"]["outer_radius"]
    out["frame_top_z_mm"] = round(float(fr.hi[2]), 3)
    out["frame_extent_xy_mm"] = [round(float(fr.hi[0] - fr.lo[0]), 3), round(float(fr.hi[1] - fr.lo[1]), 3)]
    ct = P["base_tower"]["clamp_tabs"]
    if ct["enabled"]:
        cx, cy = polar(ct["hole_radius"], ct["angle_offset_deg"])
        out["clamp_tab_hole_free"] = fr.is_void((cx + 0.2, cy + 0.3, -1.0), (0, 0, 1), P["base_tower"]["outer_ring_height"] + 2.0)
    out["frame_winding_scan"] = fr.full_scan(3.0)
    return out


# --------------------------------------------------------------------------
# 07 — Tampa do cilindro de contenção (fora de escopo; só se enabled)
# --------------------------------------------------------------------------

def cap_geometry() -> dict:
    q = P["containment_cap"]
    cg = containment_geometry()
    holes = []
    if q["vent_center_hole_diameter"] > 0:
        holes.append((0.0, 0.0, q["vent_center_hole_diameter"]))
    for i in range(int(q["vent_ring_hole_count"])):
        x, y = polar(q["vent_ring_pcd"] / 2, i * 360.0 / q["vent_ring_hole_count"])
        holes.append((x, y, q["vent_ring_hole_diameter"]))
    free_area = sum(math.pi * (d / 2) ** 2 for _, _, d in holes)
    max_opening = max((d for _, _, d in holes), default=0.0)
    ring_outer_reach = q["vent_ring_pcd"] / 2 + q["vent_ring_hole_diameter"] / 2
    return {
        "enabled": bool(q["enabled"]),
        "outer_diameter_mm": q["outer_diameter"],
        "plate_thickness_mm": q["plate_thickness"],
        "seat_depth_mm": q["seat_depth"],
        "total_height_mm": q["plate_thickness"] + q["seat_depth"],
        "holes": holes,
        "free_area_mm2": round(free_area, 1),
        "max_opening_mm": max_opening,
        "vent_holes_outer_reach_mm": ring_outer_reach,
        "cap_bottom_z_mm": cg["top_z_mm"] - q["seat_depth"],
        "plate_underside_z_mm": cg["top_z_mm"],
        "cap_top_z_mm": cg["top_z_mm"] + q["plate_thickness"],
        "footprint_with_brim_mm": q["outer_diameter"] + 2 * P["fdm_rules"]["brim_mm"],
    }


def build_containment_cap() -> bpy.types.Object:
    """Placa com anel de assento e a mesma canaleta da base; face plana para cima."""
    q = P["containment_cap"]
    bt = P["base_tower"]
    cg = containment_geometry()
    r_out = q["outer_diameter"] / 2
    t = q["plate_thickness"]
    d = q["seat_depth"]
    plate = cylinder("cap_plate", r_out, t, (0.0, 0.0, d + t / 2))
    seat_ring = ring("cap_seat_ring", r_out, bt["outer_ring_inner_diameter"] / 2, -0.05, d + 0.1)
    cap = union_all([plate, seat_ring], "tampa_contencao")
    cutters = [ring("cap_seat_groove", cg["groove_outer_radius_mm"], cg["groove_inner_radius_mm"], -0.5, d)]
    for i, (x, y, dia) in enumerate(cap_geometry()["holes"]):
        cutters.append(cylinder(f"cap_vent_{i}", dia / 2, d + t + 1.0, (x, y, (d + t) / 2)))
    cap = subtract_each(cap, cutters, "cap_feature")
    cap.name = "07_tampa_contencao"
    return cap


# --------------------------------------------------------------------------
# 06 — Suporte do ímã (parte fixa)
# --------------------------------------------------------------------------

def datum_b_z() -> float:
    return tower_top_z() + P["motor_plate"]["thickness"] + P["unverified_interfaces"]["motor_stack"]["plate_top_to_datum_b"]


def plate_top_z() -> float:
    return tower_top_z() + P["motor_plate"]["thickness"]


def magnet_post_height() -> float:
    q = P["magnet_bracket"]
    datum_a = datum_b_z() - P["spider"]["hub_thickness"]
    return datum_a - plate_top_z() - q["air_gap"]


def build_magnet_bracket() -> bpy.types.Object:
    """Arco preso sob dois parafusos M4 da flange, braço radial e poste do ímã.

    Dois pontos de fixação impedem a rotação da peça (B4): o azimute do poste
    é a referência de fase da imagem inteira. Os furos dos parafusos abrem
    para dentro do arco (garfo), porque fechar 2 mm de parede do lado interno
    esbarraria na campânula (Ø30) — o parafuso e a cabeça continuam prendendo
    a aba entre r = 18 e r = 23,5. O arco é centrado em `arc_center_azimuth_deg`
    (45°, entre os M4 de 0° e 90°).
    """
    q = P["magnet_bracket"]
    bt = P["base_tower"]
    t = q["tab_thickness"]
    r_bolt = bt["flange_hole_pcd"] / 2
    arc = annular_sector(
        "bracket_arc",
        q["arc_inner_radius"],
        q["arc_outer_radius"],
        q["arc_center_azimuth_deg"] - q["arc_half_angle_deg"],
        q["arc_center_azimuth_deg"] + q["arc_half_angle_deg"],
        0.0,
        t,
        steps=48,
    )
    r_arm0 = q["arc_outer_radius"] - 1.0
    r_arm1 = q["post_tip_radius"]
    arm = cube_polar("bracket_arm", (r_arm1 - r_arm0, q["arm_width"], t), (r_arm0 + r_arm1) / 2, q["post_azimuth_deg"], t / 2)
    post_xy = polar(q["post_radius"], q["post_azimuth_deg"])
    height = magnet_post_height()
    column = cylinder("magnet_column", q["post_diameter"] / 2, height, (post_xy[0], post_xy[1], height / 2))
    part = union_all([arc, arm, column], "suporte_ima")
    cutters = []
    for i, az in enumerate(q["bolt_azimuths_deg"]):
        bx, by = polar(r_bolt, az)
        cutters.append(cylinder(f"bracket_bolt_hole_{i}", q["bolt_hole_diameter"] / 2, t + 1.0, (bx, by, t / 2)))
    cutters.append(cylinder("magnet_pocket", q["magnet_pocket_diameter"] / 2, q["magnet_pocket_depth"] + 0.2, (post_xy[0], post_xy[1], height - q["magnet_pocket_depth"] / 2 + 0.1)))
    part = subtract_each(part, cutters, "bracket_feature")
    part.name = "06_suporte_ima"
    return part


# --------------------------------------------------------------------------
# Cupons e referência da chapa
# --------------------------------------------------------------------------

def build_joint_coupon() -> bpy.types.Object:
    panel = P["panel"]["boss"]
    spider = P["spider"]["arm"]
    bx, by, bz = P["coupons"]["joint_block"]
    block = cube("joint_coupon_block", (bx, by, bz), (0.0, 0.0, bz / 2))
    socket_internal_end = bx / 2 - panel["socket_depth"]
    socket_open_end = bx / 2 + 0.2
    socket = cube(
        "joint_coupon_socket",
        (socket_open_end - socket_internal_end, panel["socket_width"], panel["socket_height"]),
        ((socket_open_end + socket_internal_end) / 2.0, 0.0, bz / 2),
    )
    socket_coupon = boolean(block, socket, "DIFFERENCE", "coupon_socket")
    tenon_len = panel["socket_depth"] - P["quality"]["joint_bottom_clearance"]
    tenon = cube(
        "joint_coupon_tenon",
        (tenon_len, spider["tenon_width"], spider["tenon_height"]),
        (bx / 2 + 2.0 + tenon_len / 2, 0.0, spider["tenon_height"] / 2),
    )
    # Ponte fina destacável mantém as duas metades como um único STL.
    bridge = cube("coupon_breakaway_bridge", (3.2, 3.0, 0.6), (bx / 2 + 1.0, 0.0, 0.3))
    coupon = union_all([socket_coupon, tenon, bridge], "cupom_junta")
    coupon.name = "C01_cupom_junta"
    return coupon


def build_led_coupon(panel: bpy.types.Object) -> bpy.types.Object:
    """Fatia real da ponta inferior do painel: pele, bolso de fios, canal em
    degrau, piso de 0,8 mm e cavidade atrás. É exatamente a ponte que o lote
    vai imprimir, no mesmo material e orientação."""
    z0, z1 = P["coupons"]["led_slice_z_range"]
    slice_box = box_xyz("led_slice_box", (-12.0, 12.0), (-20.0, 20.0), (z0 - 1.0, z1))
    coupon = duplicate(panel, "C02_cupom_canal_LED")
    coupon = intersect(coupon, slice_box, "led_coupon_slice")
    coupon.name = "C02_cupom_canal_LED"
    return coupon


def build_motor_plate_reference() -> bpy.types.Object:
    q = P["motor_plate"]
    motor = P["unverified_interfaces"]["motor"]
    plate = cube("motor_plate_reference", (q["width"], q["depth"], q["thickness"]), (0.0, 0.0, q["thickness"] / 2))
    cutters = []
    # Furação do motor em cruz: 16 e 19 mm são as diagonais (furos opostos).
    hx = motor["base_bolt_diagonal_x"] / 2
    hy = motor["base_bolt_diagonal_y"] / 2
    for i, (x, y) in enumerate(((hx, 0.0), (0.0, hy), (-hx, 0.0), (0.0, -hy))):
        cutters.append(cylinder(f"motor_plate_motor_hole_{i}", motor["base_bolt_hole_diameter"] / 2, q["thickness"] + 0.4, (x, y, q["thickness"] / 2)))
    bt = P["base_tower"]
    for i in range(4):
        x, y = polar(bt["flange_hole_pcd"] / 2, bt["flange_hole_angle_offset_deg"] + i * 90.0)
        cutters.append(cylinder(f"motor_plate_flange_hole_{i}", bt["flange_hole_diameter"] / 2, q["thickness"] + 0.4, (x, y, q["thickness"] / 2)))
    cutters.append(cylinder("motor_plate_center_clearance", q["center_clearance_diameter"] / 2, q["thickness"] + 0.4, (0.0, 0.0, q["thickness"] / 2)))
    plate = subtract_each(plate, cutters, "motor_plate_hole")
    plate.name = "R01_suporte_motor_aluminio_NAO_IMPRIMIR"
    return plate


# --------------------------------------------------------------------------
# Medição na malha, exportação e relatório
# --------------------------------------------------------------------------

def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords))),
        Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords))),
    )


def triangles_of(obj: bpy.types.Object) -> np.ndarray:
    """Sopa de triângulos (N, 3, 3) em coordenadas do mundo (transformações já aplicadas)."""
    mesh = obj.data
    mesh.calc_loop_triangles()
    co = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
    mesh.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    idx = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
    mesh.loop_triangles.foreach_get("vertices", idx)
    return co[idx.reshape(-1, 3)]


def mesh_volume_centroid(obj: bpy.types.Object) -> tuple[float, Vector]:
    """Volume assinado e centróide volumétrico (soma de tetraedros)."""
    tri = triangles_of(obj)
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    vols = np.einsum("ij,ij->i", v0, np.cross(v1, v2)) / 6.0
    total = float(vols.sum())
    if abs(total) < 1e-9:
        return 0.0, Vector((0.0, 0.0, 0.0))
    centroid = ((v0 + v1 + v2) * (vols / 4.0)[:, None]).sum(axis=0) / total
    return total, Vector(centroid.tolist())


def object_stats(obj: bpy.types.Object, density_g_cm3: float) -> dict:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
    triangles = sum(max(1, len(face.verts) - 2) for face in bm.faces)
    bm.free()
    volume, centroid = mesh_volume_centroid(obj)
    volume = abs(volume)
    low, high = world_bounds(obj)
    dims = high - low
    return {
        "dimensions_mm": [round(dims.x, 3), round(dims.y, 3), round(dims.z, 3)],
        "bounds_min_mm": [round(low.x, 3), round(low.y, 3), round(low.z, 3)],
        "bounds_max_mm": [round(high.x, 3), round(high.y, 3), round(high.z, 3)],
        "volume_cm3": round(volume / 1000.0, 3),
        "estimated_mass_g": round(volume / 1000.0 * density_g_cm3, 2),
        "centroid_mm": [round(centroid.x, 3), round(centroid.y, 3), round(centroid.z, 3)],
        "triangles": int(triangles),
        "non_manifold_edges": int(non_manifold),
    }


def _first_run(runs: list[tuple[float, float]]) -> tuple[float, float] | None:
    return runs[0] if runs else None


def measure_panel(panel: bpy.types.Object) -> dict:
    """Critérios do painel medidos na malha por traçado de raios (B2)."""
    q = P["panel"]
    b = q["boss"]
    pr = MeshProbe(triangles_of(panel))
    hh = q["height"] / 2
    out: dict = {}

    # Socket, parede socket→cavidade, cavidade e piso do canal, num raio radial
    # no plano da junta (z = 1,41 evita o diafragma de z = 0 e y = 0,37 evita
    # a aresta de simetria).
    origin = (-30.0, 0.37, 1.41)
    runs = pr.solid_runs(origin, (1, 0, 0), 34.0)
    runs_x = [(origin[0] + t0, origin[0] + t1) for t0, t1 in runs]
    out["joint_ray_solid_runs_x"] = [[round(a, 3), round(b_, 3)] for a, b_ in runs_x]
    if runs_x:
        socket_bottom_x = runs_x[0][0]
        out["socket_depth_mm"] = round(socket_bottom_x - b["contact_face_x"], 3)
        out["socket_to_cavity_wall_mm"] = round(runs_x[0][1] - runs_x[0][0], 3)
    floor_runs = [r for r in runs_x if r[0] > 0.0]
    out["led_floor_at_joint_mm"] = round(floor_runs[0][1] - floor_runs[0][0], 3) if floor_runs else None

    # Piso do canal a meia altura, no centro e na borda do canal, e a terra
    # onde a parede local de 2,8 encontra a parede de 2,0 — longe do boss e
    # dos diafragmas.
    z_mid = 50.3
    ch = q["led_channel"]
    runs = pr.solid_runs((-6.0, 0.37, z_mid), (1, 0, 0), 12.0)
    runs_x = [(-6.0 + t0, -6.0 + t1) for t0, t1 in runs]
    out["mid_ray_solid_runs_x"] = [[round(a, 3), round(b_, 3)] for a, b_ in runs_x]
    floor_runs = [r for r in runs_x if r[0] > 0.0]
    out["led_floor_mm"] = round(floor_runs[0][1] - floor_runs[0][0], 3) if floor_runs else None
    out["inner_wall_mm"] = round(runs_x[0][1] - runs_x[0][0], 3) if runs_x else None
    y_edge = ch["width"] / 2 - 1.0 + 0.13
    runs = pr.solid_runs((-6.0, y_edge, z_mid), (1, 0, 0), 12.0)
    runs_x = [(-6.0 + t0, -6.0 + t1) for t0, t1 in runs]
    edge_runs = [r for r in runs_x if r[0] > 0.0]
    out["led_floor_edge_mm"] = round(edge_runs[0][1] - edge_runs[0][0], 3) if edge_runs else None
    y_land = ch["width"] / 2 + ch["local_wall_band_margin"] / 2 + 0.07
    runs = pr.solid_runs((-6.0, y_land, z_mid), (1, 0, 0), 12.0)
    runs_x = [(-6.0 + t0, -6.0 + t1) for t0, t1 in runs]
    land_runs = [r for r in runs_x if r[0] > 0.0]
    out["channel_land_mm"] = round(land_runs[0][1] - land_runs[0][0], 3) if land_runs else None

    # Furos M3 livres em toda a torre; bolso de porca com a profundidade certa.
    holes = []
    pockets = []
    for x in b["screw_x_positions"]:
        holes.append(pr.is_void((x + 0.37, 0.41, -hh / 4 - 1.0), (0, 0, 1), b["tower_height"] / 2 + 1.0 + hh / 4))
        # Raio paralelo ao eixo do parafuso, entre o furo (r 1,6) e o hexágono
        # (inraio 2,9): bolso vazio de −18 a −15,2, torre sólida de −15,2 a +18
        # interrompida só pelo socket (z ±3,1), que a espiga atravessa.
        z0 = -b["tower_height"] / 2 - 1.0
        runs = pr.solid_runs((x + 2.3, 0.41, z0), (0, 0, 1), b["tower_height"] + 2.0)
        runs_z = [(z0 + t0, z0 + t1) for t0, t1 in runs]
        if runs_z:
            gaps = [(runs_z[i][1], runs_z[i + 1][0]) for i in range(len(runs_z) - 1)]
            pockets.append(
                {
                    "depth_mm": round(runs_z[0][0] + b["tower_height"] / 2, 3),
                    "tower_solid_to_z_mm": round(runs_z[-1][1], 3),
                    "gaps_z_mm": [[round(a, 3), round(b_, 3)] for a, b_ in gaps],
                }
            )
        else:
            pockets.append({"depth_mm": None, "tower_solid_to_z_mm": None, "gaps_z_mm": []})
    out["screw_holes_free"] = holes
    out["nut_pockets"] = pockets

    # Casca da carenagem no flanco plano, fora do socket e da janela de fios.
    runs = pr.solid_runs((-30.0, 5.37, 12.41), (1, 0, 0), 10.0)
    first = _first_run(runs)
    out["fairing_wall_mm"] = round(first[1] - first[0], 3) if first else None

    # Varredura completa de enrolamento (A1/A2).
    out["winding_scan"] = pr.full_scan(P["quality"]["winding_scan_pitch_mm"])
    return out


def measure_spider(spider: bpy.types.Object) -> dict:
    q = P["spider"]
    a = q["arm"]
    pr = MeshProbe(triangles_of(spider))
    out: dict = {}
    shoulders = []
    for i in range(3):
        ang = i * 120.0
        ox, oy = rot_xy(30.0, 6.4, ang)
        dx, dy = polar(1.0, ang)
        runs = pr.solid_runs((ox, oy, 2.9), (dx, dy, 0.0), 70.0)
        shoulders.append(round(30.0 + runs[-1][1], 3) if runs else None)
    out["shoulder_radius_mm"] = shoulders
    tenons = []
    for i in range(3):
        ang = i * 120.0
        ox, oy = rot_xy(30.0, 0.37, ang)
        dx, dy = polar(1.0, ang)
        runs = pr.solid_runs((ox, oy, 3.41), (dx, dy, 0.0), 70.0)
        tenons.append(round(30.0 + runs[-1][1], 3) if runs else None)
    out["tenon_tip_radius_mm"] = tenons
    out["bay_entries"] = measure_bay_entries(triangles_of(spider), P)
    out["bore_free"] = pr.is_void((0.37, 0.41, -q["hub_thickness"] - 1.0), (0, 0, 1), q["hub_thickness"] + 2.0)
    runs = pr.solid_runs((9.0, 0.41, -q["hub_thickness"] - 1.0), (0, 0, 1), q["hub_thickness"] + 2.0)
    first = _first_run(runs)
    out["counterbore_depth_mm"] = round(q["hub_thickness"] - (first[1] - first[0]), 3) if first else None
    out["hub_under_washer_mm"] = round(first[1] - first[0], 3) if first else None
    # Pele sobre os alívios de massa (raio médio do bolso, azimute do centro).
    # A pele é a distância do TETO do alívio ao topo do cubo. Medir pelo início
    # da primeira corrida, não pelo comprimento dela: com os trilhos do berço em
    # x = ±12 há material fundido acima do ponto de sondagem, e o comprimento
    # passaria a somar trilho (revisão de 03/09: o valor virou 3,0 e deixou de medir a
    # pele, ainda que continuasse "passando").
    lp = q["lightening_pockets"]
    px, py = polar((lp["inner_radius"] + lp["outer_radius"]) / 2 + 0.37, lp["first_center_deg"] + 0.7)
    z0 = -q["hub_thickness"] - 1.0
    runs = pr.solid_runs((px, py, z0), (0, 0, 1), q["hub_thickness"] + 20.0)
    first = _first_run(runs)
    out["pocket_skin_mm"] = round(-(z0 + first[0]), 3) if first else None

    # Revisão 08, item 2: menor raio de QUALQUER material acima do topo do cubo.
    # A arruela Ø20 assenta no topo do cubo; se algo (os trilhos do berço) entra
    # em r < 10, ela apoia nos cantos e a porca aperta torto. O raio é varrido na
    # espessura da arruela, não lido dos parâmetros.
    m6w = P["unverified_interfaces"]["m6_nut"]
    min_r = None
    for k in range(360):
        dx, dy = polar(1.0, k + 0.37)
        for z in (0.4, m6w["washer_thickness"] / 2, m6w["washer_thickness"] - 0.4):
            runs = pr.solid_runs((0.0, 0.0, z), (dx, dy, 0.0), 45.0)
            if runs and (min_r is None or runs[0][0] < min_r):
                min_r = runs[0][0]
    out["min_solid_radius_above_hub_mm"] = round(min_r, 3) if min_r is not None else None

    # Revisão 08, item 1: topo do trilho medido na malha — é o fundo do pack, e
    # é contra ele que a ponta do eixo tem de ter folga.
    bc = q["battery_cradle"]
    rx = max(bc["rail_x_positions"])
    runs = pr.solid_runs((rx, 0.37, -q["hub_thickness"] - 1.0), (0, 0, 1), 60.0)
    out["battery_floor_z_measured_mm"] = round(runs[-1][1] - q["hub_thickness"] - 1.0, 3) if runs else None

    out["winding_scan"] = pr.full_scan(max(1.5, P["quality"]["winding_scan_pitch_mm"]))
    return out


def measure_base(base: bpy.types.Object) -> dict:
    q = P["base_tower"]
    pr = MeshProbe(triangles_of(base))
    out: dict = {}
    tower_top = tower_top_z()
    hx, hy = polar(q["flange_hole_pcd"] / 2, q["flange_hole_angle_offset_deg"])
    runs = pr.solid_runs((hx + 0.2, hy + 0.2, -1.0), (0, 0, 1), tower_top + 2.0)
    first = _first_run(runs)
    out["floor_under_flange_bolt_solid_mm"] = [round(first[0] - 1.0, 3), round(first[1] - 1.0, 3)] if first else None
    out["upper_flange_hole_free"] = pr.is_void((hx + 0.2, hy + 0.2, tower_top - q["flange_thickness"] - 0.5), (0, 0, 1), q["flange_thickness"] + 1.0)
    ct = q["clamp_tabs"]
    if ct["enabled"] and not SUSPENDED:
        tx, ty = polar(ct["hole_radius"], ct["angle_offset_deg"])
        out["clamp_tab_hole_free"] = pr.is_void((tx + 0.2, ty + 0.3, -1.0), (0, 0, 1), q["outer_ring_height"] + 2.0)
    # Revisão 08, item 3: rebaixo para as cabeças dos M3 do motor, medido na
    # malha — profundidade no raio da cabeça e raio livre no topo da flange.
    mot = P["unverified_interfaces"]["motor"]
    # Cruz 16/19: o parafuso mais externo fica em r = 9,5, a 90°. A cabeça cai quase toda
    # sobre o furo Ø22 da torre; a sonda vai na borda externa dela, sobre o piso do rebaixo.
    r_head = max(mot["base_bolt_diagonal_x"], mot["base_bolt_diagonal_y"]) / 2
    out["motor_screw_radius_mm"] = round(r_head, 3)
    r_probe = r_head + mot["base_bolt_head_diameter"] / 2 - 0.3
    hx2, hy2 = polar(r_probe, 90.0 if mot["base_bolt_diagonal_y"] >= mot["base_bolt_diagonal_x"] else 0.0)
    runs = pr.solid_runs((hx2, hy2, -1.0), (0, 0, 1), tower_top + 2.0)
    top_at_head = (runs[-1][1] - 1.0) if runs else None
    out["flange_top_at_motor_screw_radius_mm"] = round(top_at_head, 3) if top_at_head is not None else None
    out["flange_motor_recess_depth_mm"] = round(tower_top - top_at_head, 3) if top_at_head is not None else None
    runs = pr.solid_runs((0.0, 0.0, tower_top - 0.5), (1.0, 0.0, 0.0), 45.0)
    out["flange_recess_free_radius_mm"] = round(runs[0][0], 3) if runs else None

    lo, hi = pr.lo, pr.hi
    out["footprint_extent_mm"] = round(float(max(abs(lo[0]), abs(hi[0]), abs(lo[1]), abs(hi[1])) * 2.0), 3)
    out["winding_scan"] = pr.full_scan(3.0)
    return out


def measure_simple(obj: bpy.types.Object, pitch: float) -> dict:
    pr = MeshProbe(triangles_of(obj))
    return {"winding_scan": pr.full_scan(pitch)}


def export_stl(
    source: bpy.types.Object,
    filepath: Path,
    rotate_y_deg: float = 0.0,
    copies: list[tuple[float, float, float]] | None = None,
    rotate_x_deg: float = 0.0,
) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    clones = []
    placements = copies or [(0.0, 0.0, 0.0)]
    for index, placement in enumerate(placements):
        clone = duplicate(source, f"EXPORT_{source.name}_{index}")
        clone.rotation_euler[0] = math.radians(rotate_x_deg)
        clone.rotation_euler[1] = math.radians(rotate_y_deg)
        apply_transform(clone)
        low, _ = world_bounds(clone)
        clone.location.x += placement[0]
        clone.location.y += placement[1]
        clone.location.z += placement[2] - low.z
        clones.append(clone)
    bpy.ops.object.select_all(action="DESELECT")
    for clone in clones:
        clone.select_set(True)
    bpy.context.view_layer.objects.active = clones[0]
    bpy.ops.wm.stl_export(
        filepath=str(filepath),
        export_selected_objects=True,
        ascii_format=False,
        global_scale=1.0,
        use_scene_unit=False,
        apply_modifiers=True,
    )
    for clone in clones:
        delete_object(clone)


def material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0, alpha: float = 1.0) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.42
        if alpha < 1.0 and "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
    return mat


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def aim_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_guard_reference(z0: float, height: float, inner_r: float, wall: float, top_cap: bool = False) -> list[bpy.types.Object]:
    outer = inner_r + wall
    parts = [
        ring("REF_cilindro_encomendado_base", outer, inner_r, z0, z0 + 1.0),
        ring("REF_cilindro_encomendado_topo", outer, inner_r, z0 + height - 1.0, z0 + height),
    ]
    mean_r = (inner_r + outer) / 2
    for i in range(16):
        x, y = polar(mean_r, i * 360.0 / 16)
        parts.append(cylinder(f"REF_cilindro_haste_{i}", 0.65, height, (x, y, z0 + height / 2)))
    if top_cap:
        parts.append(cylinder("REF_cilindro_tampa", outer, 1.0, (0.0, 0.0, z0 + height + 0.5), vertices=96))
    return parts


def configure_render(scene: bpy.types.Scene, filepath: Path) -> None:
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
        sh = scene.display.shading
        sh.light = "STUDIO"
        sh.color_type = "MATERIAL"
        sh.show_cavity = True
        sh.cavity_type = "BOTH"
        sh.show_object_outline = True
        sh.show_shadows = True
        scene.display.render_aa = "8"
    except Exception:
        scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(filepath)
    scene.render.film_transparent = False
    scene.view_settings.exposure = 1.3
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.color = (0.32, 0.34, 0.38)

    bpy.ops.object.light_add(type="AREA", location=(250.0, -250.0, 420.0))
    key = bpy.context.object
    key.data.energy = 2800.0
    key.data.shape = "DISK"
    key.data.size = 240.0
    bpy.ops.object.light_add(type="AREA", location=(-250.0, -80.0, 280.0))
    fill = bpy.context.object
    fill.data.energy = 1800.0
    fill.data.size = 200.0

    bpy.ops.object.camera_add(location=(500.0, -620.0, 380.0))
    camera = bpy.context.object
    camera.data.lens = 50.0
    aim_camera(camera, (0.0, 0.0, 150.0))
    scene.camera = camera

    ground = cylinder("preview_ground", 220.0, 2.0, (0.0, 0.0, -2.0), vertices=96)
    assign_material(ground, material("Ground", (0.18, 0.19, 0.21, 1.0)))


def assemble_and_save(parts: dict[str, bpy.types.Object], output_dir: Path, render_preview: bool, panel_radius: float) -> dict:
    rotor_z = datum_b_z()
    sp = P["spider"]
    asm = P["assembly"]
    ui = P["unverified_interfaces"]
    abs_mat = material("ABS cinza", (0.36, 0.38, 0.42, 1.0))
    panel_mat = material("ABS painéis", (0.10, 0.32, 0.70, 1.0))
    metal_mat = material("Alumínio", (0.42, 0.45, 0.5, 1.0), metallic=0.75)
    ref_mat = material("Referência", (0.55, 0.35, 0.08, 1.0))
    guard_mat = material("Cilindro encomendado (fora de escopo)", (0.06, 0.35, 0.55, 1.0), metallic=0.1)

    for obj in parts.values():
        obj.hide_render = True
        obj.hide_viewport = True

    base = duplicate(parts["base_tower"], "MONTAGEM_base_torre")
    assign_material(base, abs_mat)
    if SUSPENDED:
        frame_mat = material("PETG base fixa", (0.20, 0.22, 0.26, 1.0))
        rod_mat = material("Hastes", (0.85, 0.45, 0.10, 1.0))
        frame = duplicate(parts["base_frame"], "MONTAGEM_base_fixa")
        assign_material(frame, frame_mat)
        chosen = next((n for n, side in SUSP["rod"]["variants"].items() if abs(side - SUSP["rod"]["side"]) < 1e-9), next(iter(SUSP["rod"]["variants"])))
        for i, az in enumerate(suspension_layout()["azimuths"]):
            rod = duplicate(parts[f"flexure_{chosen}"], f"MONTAGEM_haste_{i + 1}")
            rod.rotation_euler[2] = math.radians(az)
            assign_material(rod, rod_mat)
        if "oil_cup" in parts:
            tray = duplicate(parts["oil_cup"], "MONTAGEM_bandeja_amortecedor")
            assign_material(tray, rod_mat)
    plate = duplicate(parts["motor_plate"], "MONTAGEM_suporte_motor_ref")
    plate.location.z = plate_top_z() - P["motor_plate"]["thickness"]
    assign_material(plate, metal_mat)
    bracket = duplicate(parts["magnet_bracket"], "MONTAGEM_suporte_ima")
    bracket.location.z = plate_top_z()
    assign_material(bracket, abs_mat)

    spider = duplicate(parts["spider"], "MONTAGEM_aranha")
    spider.location.z = rotor_z
    assign_material(spider, abs_mat)
    lid = duplicate(parts["lid"], "MONTAGEM_tampa")
    lid.location.z = rotor_z + sp["electronics_bay_height"]
    assign_material(lid, abs_mat)

    # A rotação do objeto é aplicada em torno da própria origem ANTES da
    # translação: o vetor de posição também precisa ser rotacionado (spec §8).
    # O raio é o MEDIDO na malha da aranha (ombro + 26), não o nominal.
    for i in range(3):
        panel = duplicate(parts["panel"], f"MONTAGEM_painel_{i + 1}")
        angle = math.radians(i * 120.0)
        panel.rotation_euler[2] = angle
        panel.location = (panel_radius * math.cos(angle), panel_radius * math.sin(angle), rotor_z + asm["panel_mid_plane_above_datum_b"])
        assign_material(panel, panel_mat)

    # Referências visuais de hardware (não impressas), com as cotas medidas.
    motor = ui["motor"]
    motor_ref = cylinder("MONTAGEM_motor_%s_ref" % motor["model"].split()[0], motor["body_diameter"] / 2, motor["body_height"], (0.0, 0.0, plate_top_z() + motor["body_height"] / 2))
    assign_material(motor_ref, metal_mat)
    shaft = ui["shaft"]
    bell_top = plate_top_z() + ui["motor_stack"]["plate_top_to_bell_face"]
    datum_a = rotor_z - sp["hub_thickness"]
    # Eixo conforme o desenho do datasheet: ressalto, colar Ø8 e rosca M6.
    boss_ref = cylinder("MONTAGEM_%s_ref" % shaft.get("boss_label", "eixo_ressalto"), shaft["boss_diameter"] / 2, shaft["boss_height"], (0.0, 0.0, bell_top + shaft["boss_height"] / 2))
    assign_material(boss_ref, metal_mat)
    collar_ref = cylinder("MONTAGEM_%s_ref" % shaft.get("collar_label", "eixo_colar"), shaft["collar_diameter"] / 2, shaft["collar_height"], (0.0, 0.0, bell_top + shaft["boss_height"] + shaft["collar_height"] / 2))
    assign_material(collar_ref, metal_mat)
    thread_ref = cylinder("MONTAGEM_eixo_rosca_%s_ref" % shaft["thread"], shaft.get("thread_diameter", 6.0) / 2, shaft["thread_length"], (0.0, 0.0, bell_top + shaft["collar_top_above_bell"] + shaft["thread_length"] / 2))
    assign_material(thread_ref, metal_mat)
    nut = ui["m6_nut"]
    washer_z0 = rotor_z - sp["counterbore_depth"]
    washer = ring("MONTAGEM_arruela_ref", nut["washer_od"] / 2, nut["washer_id"] / 2, washer_z0, washer_z0 + nut["washer_thickness"])
    assign_material(washer, metal_mat)
    nut_ref = cylinder("MONTAGEM_%s_ref" % nut.get("ref_label", "porca_fina_" + shaft["thread"]), nut["across_flats"] / math.sqrt(3.0), nut["height"], (0.0, 0.0, washer_z0 + nut["washer_thickness"] + nut["height"] / 2), vertices=6)
    assign_material(nut_ref, metal_mat)
    # Envelopes dos componentes da baia (layout D2), na cor de referência.
    comp_mat = material("Eletrônica (envelope)", (0.78, 0.52, 0.10, 1.0))
    for c in bay_layout_components():
        if not c.get("plan"):
            continue
        z0, z1 = c["z_range"]
        cx, cy = c["center_xy"]
        if c.get("mount") == "wall_slot":
            depth, width, height = c["size_xyz"]
            ref = cube(f"MONTAGEM_baia_{c['id']}", (depth, width, height), (cx, cy, rotor_z + (z0 + z1) / 2), rotation_z_deg=c["wall_azimuth_deg"])
        elif "polygon_xy" in c:
            ref = mesh_prism_z(f"MONTAGEM_baia_{c['id']}", [tuple(pt) for pt in c["polygon_xy"]], rotor_z + z0, rotor_z + z1)
        elif "diameter" in c:
            ref = cylinder(f"MONTAGEM_baia_{c['id']}", c["diameter"] / 2, z1 - z0, (cx, cy, rotor_z + (z0 + z1) / 2), vertices=32)
        else:
            dx, dy, dz = c["size_xyz"]
            ref = cube(f"MONTAGEM_baia_{c['id']}", (dx, dy, dz), (cx, cy, rotor_z + (z0 + z1) / 2))
        assign_material(ref, comp_mat)
    bat = ui["battery"]
    cradle = sp["battery_cradle"]
    battery_ref = cube("MONTAGEM_bateria_ref", (bat["width"], bat["length"], bat["height"]), (0.0, 0.0, rotor_z + cradle["rail_height"] + bat["height"] / 2))
    assign_material(battery_ref, ref_mat)
    hs = sp["hall_sensor"]
    hx, hy = polar(hs["radius"], hs["azimuth_deg"])
    hall_ref = cube("MONTAGEM_sensor_hall_ref", (ui["hall_sensor"]["body_height"], ui["hall_sensor"]["body_width"], ui["hall_sensor"]["body_thickness"]), (hx, hy, datum_a + ui["hall_sensor"]["body_thickness"] / 2), rotation_z_deg=hs["azimuth_deg"])
    assign_material(hall_ref, ref_mat)

    cont = ui["containment"]
    cg = containment_geometry()
    guard_top = cg["top_z_mm"]
    use_cap_part = P["containment_cap"]["enabled"] and "containment_cap" in parts
    for obj in build_guard_reference(cg["rest_z_mm"], cont["height"], cont["inner_diameter"] / 2, cont["wall"], cg["cylinder_has_top_cap"] and not use_cap_part):
        assign_material(obj, guard_mat)
    if use_cap_part:
        cap = duplicate(parts["containment_cap"], "MONTAGEM_tampa_contencao")
        cap.location.z = cap_geometry()["cap_bottom_z_mm"]
        assign_material(cap, abs_mat)

    blend_dir = output_dir / "fonte"
    blend_dir.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_dir / "Hologram_Orbiter_v3_0.blend"))

    if render_preview:
        preview_dir = output_dir / "preview"
        preview_dir.mkdir(parents=True, exist_ok=True)
        configure_render(bpy.context.scene, preview_dir / "montagem.png")
        bpy.ops.render.render(write_still=True)
        # Vista da baia: tampa e referências do cilindro ocultas, câmera sobre o
        # cubo, para conferir o layout da eletrônica.
        scene = bpy.context.scene
        hidden = [lid] + [o for o in bpy.data.objects if o.name.startswith("REF_")]
        for o in hidden:
            o.hide_render = True
        cam = scene.camera
        cam.location = (30.0, -75.0, rotor_z + 150.0)
        aim_camera(cam, (0.0, 0.0, rotor_z + 8.0))
        cam.data.lens = 60.0
        scene.render.filepath = str(preview_dir / "montagem_baia.png")
        bpy.ops.render.render(write_still=True)
        for o in hidden:
            o.hide_render = False

    panel_h = P["panel"]["height"]
    mid = rotor_z + asm["panel_mid_plane_above_datum_b"]
    shaft_top = bell_top + shaft["protrusion_above_bell"]
    nut_top = washer_z0 + nut["washer_thickness"] + nut["height"]
    shaft_top_alt = bell_top + shaft.get("protrusion_alt_mm", shaft["protrusion_above_bell"])
    collar_top = bell_top + shaft["collar_top_above_bell"]
    washer_top = washer_z0 + nut["washer_thickness"]
    return {
        "shaft_above_nut_alt_protrusion_mm": round(shaft_top_alt - nut_top, 2),
        "collar_top_above_hub_mm": round(collar_top - rotor_z, 2),
        "washer_top_above_hub_mm": round(washer_top - rotor_z, 2),
        "washer_top_minus_collar_top_mm": round(washer_top - collar_top, 2),
        "washer_hole_minus_collar_mm": round(nut["washer_id"] - shaft["collar_diameter"], 2),
        "nut_top_above_hub_mm": round(nut_top - rotor_z, 2),
        "datum_b_z_mm": rotor_z,
        "datum_a_z_mm": datum_a,
        "bell_face_z_mm": bell_top,
        "panel_mid_plane_z_mm": mid,
        "panel_radius_used_mm": round(panel_radius, 3),
        "rotor_z_min_mm": mid - panel_h / 2,
        "rotor_z_max_mm": mid + panel_h / 2,
        "plate_top_z_mm": plate_top_z(),
        "magnet_post_top_z_mm": plate_top_z() + magnet_post_height(),
        "hall_air_gap_mm": P["magnet_bracket"]["air_gap"],
        "shaft_top_z_mm": shaft_top,
        "nut_top_z_mm": round(nut_top, 2),
        "shaft_above_nut_mm": round(shaft_top - nut_top, 2),
        "index_pulse_note": "Sensor em r=29, azimute %.0f° do rotor; ímã em r=29, mesmo azimute na base: o pulso ocorre quando o braço 1 está alinhado com +x da base." % sp["hall_sensor"]["azimuth_deg"],
        "containment_reference_top_z_mm": guard_top,
        "containment_vertical_margin_mm": round(guard_top - (mid + panel_h / 2), 2),
    }


def compute_report(stats: dict, measured: dict, assembly: dict, physics: dict) -> dict:
    q = P["panel"]
    f = q["fairing"]
    b = q["boss"]
    sp = P["spider"]
    bt = P["base_tower"]
    ncm = P["non_cad_masses_g"]
    cs = sp["cooling_slots"]
    cx = panel_channel_x()

    panel_mass_bare = stats["panel_each"]["estimated_mass_g"]
    panel_assembled = panel_mass_bare + ncm["led_strip_per_panel"] + ncm["hardware_per_panel"]
    rotor_cad = stats["spider"]["estimated_mass_g"] + 3.0 * panel_mass_bare + stats["lid"]["estimated_mass_g"]
    rotor_total = (
        rotor_cad
        + 3.0 * (ncm["led_strip_per_panel"] + ncm["hardware_per_panel"])
        + ncm["battery_pack"]
        + ncm["m6_nut_and_washer"]
        + ncm["onboard_electronics_allowance"]
        + ncm["hall_sensor_bare"]
    )

    frontal_width = f["blade_flat_face_x"] - f["flat_flank_x"]
    frontal_area = frontal_width * 2.0 * f["half_height"]
    chord = f["nose_center_xy"][1] + f["nose_semi_axes"][1] - f["tail_xy"][1]
    fineness = chord / frontal_width
    cd_lo, cd_hi = P["drag_estimate"]["cd_range_frontal"]

    slot_area = cs["count"] * math.radians(cs["arc_deg"]) * (cs["outer_radius"] ** 2 - cs["inner_radius"] ** 2) / 2.0
    lv = bt["lateral_vents"]
    vent_area = lv["count"] * lv["width"] * lv["height"]

    omega = P["operating_point"]["omega_rad_s"]
    r_mid = P["operating_point"]["panel_mid_plane_radius_mm"] / 1000.0
    force = panel_assembled / 1000.0 * omega ** 2 * r_mid

    panel_cg_z = stats["panel_each"]["centroid_mm"][2]
    strip_len = P["unverified_interfaces"]["led_strip"]["strip_length"]
    strip_z0 = -q["height"] / 2 + q["led_channel"]["bottom_skin"] + q["led_channel"]["wire_pocket_height"]
    strip_cg_z = strip_z0 + strip_len / 2
    wire_mass = 1.2
    wire_cg_z = (strip_z0 + f["blade_wire_hole_z"][0]) / 2
    cg_assembled = (
        panel_mass_bare * panel_cg_z + ncm["led_strip_per_panel"] * strip_cg_z + wire_mass * wire_cg_z
    ) / (panel_mass_bare + ncm["led_strip_per_panel"] + wire_mass)

    shoulders = [s for s in measured["spider"]["shoulder_radius_mm"] if s is not None]
    mean_shoulder = sum(shoulders) / len(shoulders) if shoulders else None
    m6 = P["unverified_interfaces"]["m6_nut"]
    nut_top = -sp["counterbore_depth"] + m6["washer_thickness"] + m6["height"]

    # Ponta do eixo acima do topo do cubo, nas duas leituras do desenho cotado
    # (14 e 12 mm sobre a campânula). É contra ela que o fundo do pack tem folga.
    sh = P["unverified_interfaces"]["shaft"]
    # Altura do fundo do cubo sobre a campânula: 0 no A2212 (cubo na campânula); 5 no
    # AX-2810Q, cujo cubo assenta na base serrilhada do adaptador de hélice.
    ms = P["unverified_interfaces"]["motor_stack"]
    seat = ms["plate_top_to_datum_b"] - ms["plate_top_to_bell_face"] - sp["hub_thickness"]
    shaft_tip_hi = sh["protrusion_above_bell"] - seat - sp["hub_thickness"]
    shaft_tip_lo = sh.get("protrusion_alt_mm", sh["protrusion_above_bell"]) - seat - sp["hub_thickness"]

    deflections = [case["tip_deflection_mm"] for case in physics["flexure"]["acceptance_limit_cases"]]
    deflection_worst = max(deflections)

    layout = bay_layout_components()
    layout_checks = bay_layout_checks(layout)
    balance = bay_balance(layout, stats)
    counterweight = balance["counterweight_mass_g"]
    rotor_total_with_cw = rotor_total + counterweight

    return {
        "physics": physics,
        "panel": {
            "bare_mass_g": panel_mass_bare,
            "assembled_mass_g": round(panel_assembled, 2),
            "assembled_mass_limit_g": q["mass_limit_assembled_g"],
            "datum_d_mm": round(0.0 - stats["panel_each"]["bounds_min_mm"][2], 3),
            "abs_centroid_z_mm": panel_cg_z,
            "assembled_centroid_z_estimate_mm": round(cg_assembled, 2),
            "assembled_centroid_note": "Estimativa histórica com 1,2 g de fios: não validada para o chicote de seis condutores; pesar e recalcular CG e ferragens antes da montagem operacional.",
            "parasitic_moment_n_mm": round(force * abs(cg_assembled), 1),
            "centrifugal_force_n_with_cad_mass": round(force, 1),
            "led_floor_nominal_mm": round(cx["floor_thickness"], 3),
            "led_floor_measured_mm": measured["panel"]["led_floor_mm"],
            "led_floor_at_joint_measured_mm": measured["panel"]["led_floor_at_joint_mm"],
            "led_floor_edge_measured_mm": measured["panel"]["led_floor_edge_mm"],
            "channel_land_measured_mm": measured["panel"]["channel_land_mm"],
            "channel_bridge_width_mm": q["led_channel"]["width"],
            "socket_depth_measured_mm": measured["panel"].get("socket_depth_mm"),
            "socket_to_cavity_wall_measured_mm": measured["panel"].get("socket_to_cavity_wall_mm"),
            "screw_holes_free": measured["panel"]["screw_holes_free"],
            "nut_pockets_measured": measured["panel"]["nut_pockets"],
            "fairing_wall_measured_mm": measured["panel"]["fairing_wall_mm"],
            "nut_pocket_wall_mm": round(b["tower_diameter"] / 2 - b["nut_hex_circumradius"], 3),
            "led_channel_start_z_mm": strip_z0,
            "led_strip_top_z_mm": round(strip_z0 + strip_len, 2),
            "panel_top_z_mm": q["height"] / 2,
            "winding_scan": measured["panel"]["winding_scan"],
        },
        "boss_drag": {
            "frontal_width_mm": frontal_width,
            "frontal_area_mm2": round(frontal_area, 1),
            "fairing_chord_mm": round(chord, 2),
            "fineness_ratio": round(fineness, 2),
            "cd_range": [cd_lo, cd_hi],
            "a_cd_range_mm2": [round(frontal_area * cd_lo, 1), round(frontal_area * cd_hi, 1)],
            "target_mm2": P["drag_estimate"]["target_a_cd_mm2"],
            "method": P["drag_estimate"]["note"],
        },
        "spider": {
            "mass_g": stats["spider"]["estimated_mass_g"],
            "mass_limit_g": sp["mass_limit_g"],
            "shoulder_radius_measured_mm": measured["spider"]["shoulder_radius_mm"],
            "tenon_tip_radius_measured_mm": measured["spider"]["tenon_tip_radius_mm"],
            "bay_entries": measured["spider"]["bay_entries"],
            "panel_mid_plane_radius_from_mesh_mm": round(mean_shoulder - b["contact_face_x"], 3) if mean_shoulder is not None else None,
            "bore_free": measured["spider"]["bore_free"],
            "counterbore_depth_measured_mm": measured["spider"]["counterbore_depth_mm"],
            "hub_under_washer_measured_mm": measured["spider"]["hub_under_washer_mm"],
            "pocket_skin_measured_mm": measured["spider"]["pocket_skin_mm"],
            "cooling_free_area_mm2": round(slot_area, 1),
            "hub_rim_outside_slots_mm": round(sp["hub_diameter"] / 2 - cs["outer_radius"], 2),
            "bay_wall_to_slot_mm": round(cs["inner_radius"] - sp["electronics_bay_od"] / 2, 2),
            "nut_top_above_hub_mm": round(nut_top, 2),
            "battery_floor_z_mm": sp["battery_cradle"]["rail_height"],
            "battery_floor_z_measured_mm": measured["spider"]["battery_floor_z_measured_mm"],
            "min_solid_radius_above_hub_mm": measured["spider"]["min_solid_radius_above_hub_mm"],
            "washer_seat_radius_mm": round(m6["washer_od"] / 2, 2),
            "shaft_tip_above_hub_mm": round(shaft_tip_hi, 2),
            "shaft_tip_above_hub_alt_mm": round(shaft_tip_lo, 2),
            "shaft_tip_to_battery_floor_mm": round(measured["spider"]["battery_floor_z_measured_mm"] - shaft_tip_hi, 2),
            "shaft_tip_to_battery_floor_alt_mm": round(measured["spider"]["battery_floor_z_measured_mm"] - shaft_tip_lo, 2),
            "battery_top_z_mm": sp["battery_cradle"]["rail_height"] + P["unverified_interfaces"]["battery"]["height"],
            "bay_internal_height_mm": sp["electronics_bay_height"],
            "battery_half_diagonal_mm": round(math.hypot(sp["battery_cradle"]["pack_length_y"] / 2 + sp["battery_cradle"]["end_tab_thickness"] + sp["battery_cradle"]["clearance"], sp["battery_cradle"]["end_tab_width_x"] / 2), 2),
            "bay_inner_radius_mm": sp["electronics_bay_id"] / 2,
            "winding_scan": measured["spider"]["winding_scan"],
        },
        "lid": {"mass_g": stats["lid"]["estimated_mass_g"], "mass_limit_g": P["lid"]["mass_limit_g"], "winding_scan": measured["lid"]["winding_scan"]},
        "base_tower": {
            "mass_g": stats["base_tower"]["estimated_mass_g"],
            "mass_limit_g": bt.get("mass_limit_g"),
            "lateral_vent_area_mm2": vent_area,
            "footprint_diameter_mm": bt["footprint_diameter"],
            "footprint_extent_measured_mm": measured["base"]["footprint_extent_mm"],
            "footprint_with_brim_mm": round(measured["base"]["footprint_extent_mm"] + 2 * P["fdm_rules"]["brim_mm"], 2),
            "floor_under_flange_bolt_solid_mm": measured["base"]["floor_under_flange_bolt_solid_mm"],
            "upper_flange_hole_free": measured["base"]["upper_flange_hole_free"],
            "motor_screw_radius_mm": measured["base"].get("motor_screw_radius_mm"),
            "flange_motor_recess_depth_mm": measured["base"].get("flange_motor_recess_depth_mm"),
            "flange_recess_free_radius_mm": measured["base"].get("flange_recess_free_radius_mm"),
            "motor_screw_head_diameter_mm": P["unverified_interfaces"]["motor"].get("base_bolt_head_diameter"),
            "motor_screw_head_height_mm": P["unverified_interfaces"]["motor"].get("base_bolt_head_height"),
            "clamp_tab_hole_free": measured["base"].get("clamp_tab_hole_free"),
            "winding_scan": measured["base"]["winding_scan"],
        },
        "magnet_bracket": {
            "mass_g": stats["magnet_bracket"]["estimated_mass_g"],
            "post_height_mm": round(magnet_post_height(), 2),
            "bolts": len(P["magnet_bracket"]["bolt_azimuths_deg"]),
            "arc_to_bell_clearance_mm": round(P["magnet_bracket"]["arc_inner_radius"] - P["unverified_interfaces"]["motor"]["body_diameter"] / 2, 2),
            "winding_scan": measured["magnet_bracket"]["winding_scan"],
        },
        "containment": {
            **containment_geometry(),
            # The envelope is recalculated from the actual section every build.
            "rotor_dynamic_radius_mm": round(P["operating_point"]["image_cylinder_diameter_mm"] / 2 + deflection_worst, 2),
            "radial_clearance_mm": round(containment_geometry()["cylinder_inner_radius"] - (P["operating_point"]["image_cylinder_diameter_mm"] / 2 + deflection_worst), 2),
            "tip_deflection_used_mm": deflection_worst,
            "tip_deflection_range_mm": [round(min(deflections), 3), round(max(deflections), 3)],
            "peripheral_holes": "removidos (abas de grampo no lugar)" if not P["base_tower"]["peripheral_holes"]["enabled"] else "PCD %.0f" % P["base_tower"]["peripheral_holes"]["pcd"],
        },
        "containment_cap": {
            **cap_geometry(),
            "mass_g": stats["containment_cap"]["estimated_mass_g"] if "containment_cap" in stats else None,
        },
        "bay_layout": {
            "components": [
                {
                    "id": c["id"],
                    "label": c.get("label", c["id"]),
                    "mass_g_estimate": c["mass_g"],
                    "center_xy_mm": c["center_xy"],
                    "z_range_mm": c.get("z_range"),
                    "mount": c.get("mount", "none"),
                }
                for c in layout
            ],
            **layout_checks,
            **balance,
            "mesh_intersections": measured["bay_intersections"],
        },
        "rotor": {
            "cad_mass_g": round(rotor_cad, 2),
            "total_mass_estimate_g": round(rotor_total_with_cw, 2),
            "total_without_counterweight_g": round(rotor_total, 2),
            "limit_g": P["requirements"]["rotor_mass_max_g"],
            "mass_budget_complete": ncm["panel_hardware_and_wiring_verified"],
            "mass_budget_note": ncm["panel_mass_budget_note"],
            "components": {
                "spider": stats["spider"]["estimated_mass_g"],
                "panels_bare_x3": round(3 * panel_mass_bare, 2),
                "lid": stats["lid"]["estimated_mass_g"],
                "strips_x3": round(3 * ncm["led_strip_per_panel"], 2),
                "hardware_x3": round(3 * ncm["hardware_per_panel"], 2),
                "battery": ncm["battery_pack"],
                "nut_washer": ncm["m6_nut_and_washer"],
                "electronics_allowance": ncm["onboard_electronics_allowance"],
                "hall_sensor": ncm["hall_sensor_bare"],
                "counterweight_planned": counterweight,
            },
        },
        "assembly": assembly,
    }


def acceptance(report: dict, stats: dict, measured: dict) -> list[dict]:
    q = P["panel"]
    b = q["boss"]
    sp = P["spider"]
    checks = []
    # Lido de P aqui dentro: os testes executam esta função isolada, só com P no escopo.
    susp = P["base_tower"].get("suspension") or {}
    suspended = bool(susp.get("enabled"))

    def add(name, value, criterion, ok, note=""):
        checks.append({"criterio": name, "valor": value, "requisito": criterion, "passa": bool(ok), "nota": note})

    def num_ok(value, lo=None, hi=None):
        if value is None:
            return False
        if lo is not None and value < lo:
            return False
        if hi is not None and value > hi:
            return False
        return True

    rp = report["panel"]
    rs = report["spider"]
    rb = report["base_tower"]

    # -- geometria medida na malha --
    r_mid = rs["panel_mid_plane_radius_from_mesh_mm"]
    add("Raio do plano médio do painel", r_mid, "100 ±0,1 mm", num_ok(r_mid, 99.9, 100.1), "medido: ombro da longarina na malha da aranha (%s) + 26 da face de contato" % rs["shoulder_radius_measured_mm"])
    add("Datum D", rp["datum_d_mm"], "104 ±0,2 mm", abs(rp["datum_d_mm"] - 104.0) <= 0.2, "da malha do painel")
    add("Δh entre painéis", 0.0, "≤ ±0,5 mm", True, "os três painéis são o mesmo STL")
    add("Ponta da espiga", rs["tenon_tip_radius_measured_mm"], "96 ±0,1 mm", all(num_ok(v, 95.9, 96.1) for v in rs["tenon_tip_radius_measured_mm"]), "medido na malha")
    add("Profundidade do socket", rp["socket_depth_measured_mm"], "%.1f ±0,1 mm" % b["socket_depth"], num_ok(rp["socket_depth_measured_mm"], b["socket_depth"] - 0.1, b["socket_depth"] + 0.1), "medido: primeiro material no eixo do socket")
    add("Parede entre o fundo do socket e a cavidade", rp["socket_to_cavity_wall_measured_mm"], "≥ 1,2 mm", num_ok(rp["socket_to_cavity_wall_measured_mm"], 1.2), "medido")
    add("Piso sob o canal do LED", rp["led_floor_measured_mm"], "≥ 0,6 mm (nominal %.2f)" % rp["led_floor_nominal_mm"], num_ok(rp["led_floor_measured_mm"], 0.6) and num_ok(rp["led_floor_edge_measured_mm"], 0.6), "medido a meia altura no centro; na borda do canal: %s; na junta: %s. Ponte de %.1f mm" % (rp["led_floor_edge_measured_mm"], rp["led_floor_at_joint_measured_mm"], rp["channel_bridge_width_mm"]))
    add("Terra entre o piso e a parede de 2,0", rp["channel_land_measured_mm"], "≥ 2,0 mm (parede local 2,8 em 1 mm de cada lado do canal)", num_ok(rp["channel_land_measured_mm"], 2.0), "medido")
    add("Furos M3 livres em toda a torre", rp["screw_holes_free"], "livres (sem pino de casca invertida)", all(rp["screw_holes_free"]), "raio ao longo do eixo de cada parafuso: enrolamento 0 em toda a extensão (06-PENDENCIAS A1)")
    socket_gap = (-b["socket_height"] / 2, b["socket_height"] / 2)
    pockets_ok = all(
        p["depth_mm"] is not None
        and abs(p["depth_mm"] - b["nut_pocket_depth"]) <= 0.1
        and abs(p["tower_solid_to_z_mm"] - b["tower_height"] / 2) <= 0.1
        and len(p["gaps_z_mm"]) == 1
        and abs(p["gaps_z_mm"][0][0] - socket_gap[0]) <= 0.1
        and abs(p["gaps_z_mm"][0][1] - socket_gap[1]) <= 0.1
        for p in rp["nut_pockets_measured"]
    )
    add("Bolso da porca M3 e torre", [p["depth_mm"] for p in rp["nut_pockets_measured"]], "bolso %.1f ±0,1 mm; torre sólida de −15,2 a +%.0f, só o socket (z ±%.1f) a interrompe" % (b["nut_pocket_depth"], b["tower_height"] / 2, b["socket_height"] / 2), pockets_ok, "medido ao longo do eixo de cada parafuso; vãos: %s" % [p["gaps_z_mm"] for p in rp["nut_pockets_measured"]])
    add("Parede ao redor do bolso de porca", rp["nut_pocket_wall_mm"], "≥ 1,5 mm", rp["nut_pocket_wall_mm"] >= 1.5, "geometria: torre Ø10, hexágono de circunraio 3,35")
    add("Casca da carenagem", rp["fairing_wall_measured_mm"], "%.1f ±0,05 mm" % q["fairing"]["wall"], num_ok(rp["fairing_wall_measured_mm"], q["fairing"]["wall"] - 0.05, q["fairing"]["wall"] + 0.05), "medido no flanco plano")
    min_wall_candidates = [v for v in (rp["fairing_wall_measured_mm"], rp["led_floor_measured_mm"], rs["hub_rim_outside_slots_mm"], P["lid"]["skin_thickness"], q["ribs"]["thickness"]) if v is not None]
    min_wall = min(min_wall_candidates)
    add("Parede estrutural nas seções amostradas", round(min_wall, 2), "≥ %.2f mm" % P["fdm_rules"]["min_structural_wall_mm"], min_wall >= P["fdm_rules"]["min_structural_wall_mm"], "Amostras: piso do canal, flanco da carenagem, borda do disco, pele da tampa e nervuras; não certifica a espessura mínima global da malha")

    # -- enrolamento --
    for label, scan in (("painel", rp["winding_scan"]), ("aranha", rs["winding_scan"]), ("tampa", report["lid"]["winding_scan"]), ("base", rb["winding_scan"]), ("suporte do ímã", report["magnet_bracket"]["winding_scan"])):
        add(
            "Enrolamento por raios — %s" % label,
            [scan["bad_winding_segments"], scan["thin_solid_segments"]],
            "0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm",
            scan["bad_winding_segments"] == 0 and scan["thin_solid_segments"] == 0,
            "%d raios, passo %.1f mm" % (scan["rays"], scan["pitch_mm"]),
        )

    # -- cubo e eixo --
    add("Furo do cubo livre", rs["bore_free"], "livre", rs["bore_free"], "Ø%.1f para eixo medido em Ø%.1f" % (sp["bore_diameter"], P["unverified_interfaces"]["shaft"]["diameter_through_hub"]))
    add("Rebaixo da arruela", rs["counterbore_depth_measured_mm"], "%.1f ±0,1 mm (zero: arruela no topo do cubo)" % sp["counterbore_depth"], num_ok(rs["counterbore_depth_measured_mm"], sp["counterbore_depth"] - 0.1, sp["counterbore_depth"] + 0.1), "medido; %s mm de cubo sob a arruela" % rs["hub_under_washer_measured_mm"])
    add("Pele sobre os alívios do cubo", rs["pocket_skin_measured_mm"], "≥ 2,0 mm", num_ok(rs["pocket_skin_measured_mm"], 1.95), "medido")
    asm = report["assembly"]
    sh = P["unverified_interfaces"]["shaft"]
    m6 = P["unverified_interfaces"]["m6_nut"]
    add("Arruela passa pelo colar Ø%.1f do eixo" % sh["collar_diameter"], asm["washer_hole_minus_collar_mm"], "furo − colar ≥ 0,3 mm", asm["washer_hole_minus_collar_mm"] >= 0.3, "arruela Ø%.0f × Ø%.1f × %.1f (%s). Uma arruela M6 (furo 6,4) assentaria no colar e a porca não apertaria o cubo" % (m6["washer_od"], m6["washer_id"], m6["washer_thickness"], m6["washer_material"].split(";")[0]))
    add("Porca não toca o colar do eixo", asm["washer_top_minus_collar_top_mm"], "topo da arruela ≥ topo do colar + 0,5 mm", asm["washer_top_minus_collar_top_mm"] >= 0.5, "colar até %.1f acima do topo do cubo (desenho: ressalto %.0f + colar %.0f); arruela até %.1f" % (asm["collar_top_above_hub_mm"], sh["boss_height"], sh["collar_height"], asm["washer_top_above_hub_mm"]))
    add(
        "Rosca sobrando acima da porca",
        asm["shaft_above_nut_mm"],
        "≥ 1 mm",
        asm["shaft_above_nut_mm"] >= 1.0,
        "eixo de %.0f mm acima da campânula (desenho; não medido); na leitura de %.0f mm sobrariam %.1f. Porca fina de %.0f mm sobre arruela de %.1f, sem rebaixo; trava química no lugar do anel de nylon"
        % (sh["protrusion_above_bell"], sh.get("protrusion_alt_mm", sh["protrusion_above_bell"]), asm["shaft_above_nut_alt_protrusion_mm"], m6["height"], m6["washer_thickness"]),
    )
    add("Trilhos do berço acima da porca", rs["battery_floor_z_mm"], "≥ %.1f mm (topo da porca)" % rs["nut_top_above_hub_mm"], rs["battery_floor_z_mm"] >= rs["nut_top_above_hub_mm"], "")
    # NOVO (revisão de 03/09, item 1). A porca não era o obstáculo mais alto: a ponta
    # do eixo passa dela. Vale nas duas leituras do desenho, 14 e 12 mm.
    gap_hi = rs["shaft_tip_to_battery_floor_mm"]
    gap_lo = rs["shaft_tip_to_battery_floor_alt_mm"]
    add(
        "Fundo da bateria acima da ponta do eixo",
        [gap_hi, gap_lo],
        "≥ 1,0 mm nas duas leituras do eixo (14 e 12 mm sobre a campânula)",
        gap_hi >= 1.0 and gap_lo >= 1.0,
        "piso medido na malha em Z = %.1f; ponta do eixo em +%.1f (leitura de %.0f) e +%.1f (leitura de %.0f). Critério novo: o eixo é mais alto que a porca e nenhum critério os comparava"
        % (rs["battery_floor_z_measured_mm"], rs["shaft_tip_above_hub_mm"], P["unverified_interfaces"]["shaft"]["protrusion_above_bell"], rs["shaft_tip_above_hub_alt_mm"], P["unverified_interfaces"]["shaft"].get("protrusion_alt_mm", 0)),
    )
    # NOVO (revisão de 03/09, item 2). Assento plano para a arruela Ø20.
    min_r = rs["min_solid_radius_above_hub_mm"]
    seat_r = rs["washer_seat_radius_mm"]
    add(
        "Assento da arruela livre acima do cubo",
        min_r,
        "menor raio sólido ≥ %.1f mm (raio da arruela + 0,3)" % (seat_r + 0.3),
        min_r is not None and min_r >= seat_r + 0.3,
        "varredura de 360 raios na espessura da arruela; os trilhos do berço são o material mais interno",
    )
    bay_ok = rs["battery_top_z_mm"] <= rs["bay_internal_height_mm"]
    add("Bateria cabe na baia sobre a porca", rs["battery_top_z_mm"], "≤ %.0f mm" % rs["bay_internal_height_mm"], bay_ok, "pack de %.0f mm sobre trilhos em Z=%.0f" % (P["unverified_interfaces"]["battery"]["height"], rs["battery_floor_z_mm"]))
    add("Berço da bateria dentro da baia (meia-diagonal)", rs["battery_half_diagonal_mm"], "≤ %.0f mm" % rs["bay_inner_radius_mm"], rs["battery_half_diagonal_mm"] <= rs["bay_inner_radius_mm"], "abas de topo inclusas")

    # -- layout da baia (D2) --
    entries = rs["bay_entries"]
    add("Raízes sem saliência dentro da baia", [r["root_blocked_rays"] for r in entries["arms"]], "zero raios obstruídos nos três braços", entries["roots_clear"], "Sondagem da faixa central de cada raiz (y ±2 mm), junto à face interna da parede e acima do piso; guias laterais fora da amostra")
    add("Entradas de fios atravessam a parede da baia", [r["window_blocked_rays"] for r in entries["arms"]], "zero raios obstruídos nas três janelas e na transição ao bolso", entries["windows_clear"], "Sondagem da abertura completa e da ligação ao bolso externo, na malha final")
    bay = report["bay_layout"]
    add("Layout da baia: envelopes e faixas dos feixes", "ok" if bay["ok"] else "; ".join(bay["problems"]), "envelopes dentro da baia, Z ≤ %.1f; piso livre para feixes" % (sp["electronics_bay_height"] - 1), bay["ok"], "%d componentes; pilares em %s" % (len([c for c in bay["components"] if c["z_range_mm"]]), bay["standoffs"]))
    collisions = bay["mesh_intersections"]
    add("Eletrônica sem interseção com a malha final da aranha", [c["intersection_mm3"] for c in collisions["components"]], "≤ %.3f mm³ por envelope (tolerância numérica)" % collisions["tolerance_mm3"], collisions["ok"], "Inclui raízes dos braços e suportes; módulos reais ainda precisam de medição")
    section_checks = report["physics"]["stl_section_checks"]
    add("Seção de flexão confere com cortes da malha", [round(c["measured"]["Iyy_mm4"], 4) for c in section_checks], "integrais da seção iguais nos parâmetros e em três cortes", all(c["matches_parameters"] for c in section_checks), "Verifica o cálculo geométrico; não certifica resistência, fluência ou ABS FDM")
    add("Eletrônica embarcada (estimada) dentro da folga", bay["electronics_mass_g"], "≤ %.0f g" % bay["allowance_g"], bay["electronics_mass_g"] <= bay["allowance_g"] + 1e-9, "massas de catálogo, não pesadas; o XL4015 sozinho (~18 g) estouraria")
    # Revisão 08, item 11: o vetor agora soma os centróides das peças impressas
    # e o sensor hall, e o contrapeso é repartido entre os dois alívios que
    # cercam a direção pedida — arredondar para o alívio mais próximo deixava
    # resíduo maior que o admissível.
    add(
        "Contrapeso planejado do layout",
        [q["mass_g"] for q in bay["counterweight_placement"]],
        "cabe nos alívios (≤ %.1f g cada) e deixa resíduo ≤ %.1f g·mm" % (bay["pocket_capacity_g"], bay["admissible_g_mm"]),
        bay["counterweight_fits_pockets"] and bay["residual_within_admissible"],
        "desbalanceamento nominal %.1f g·mm a %.1f° (admissível %.1f); correção a %.1f° repartida em %s; resíduo %.2f g·mm. Fontes: %s"
        % (
            bay["unbalance_g_mm"],
            bay["unbalance_azimuth_deg"],
            bay["admissible_g_mm"],
            bay["counterweight_azimuth_deg"],
            ", ".join("%.2f g no alívio de %.0f°" % (c["mass_g"], c["pocket_center_deg"]) for c in bay["counterweight_placement"]),
            bay["residual_g_mm"],
            "; ".join("%s %.1f g·mm a %.0f°" % (x["id"], x["u_g_mm"], x["azimuth_deg"]) for x in bay["sources"]),
        ),
    )
    # -- ventilação, arrasto --
    add("Área livre de ventilação do cubo", rs["cooling_free_area_mm2"], "≥ 300 mm², sem abrir a baia", rs["cooling_free_area_mm2"] >= 300.0 and rs["bay_wall_to_slot_mm"] >= 0.0, "3 rasgos de 60° fora da baia (r %.1f–%.1f)" % (sp["cooling_slots"]["inner_radius"], sp["cooling_slots"]["outer_radius"]))
    if not suspended:
        add("Área livre de ventilação da base", rb["lateral_vent_area_mm2"], "≥ 600 mm², na lateral", rb["lateral_vent_area_mm2"] >= 600.0, "8 janelas na parede lateral da baia")
    a_cd_hi = report["boss_drag"]["a_cd_range_mm2"][1]
    add("A × Cd do boss carenado", report["boss_drag"]["a_cd_range_mm2"], "≤ %.1f mm²" % P["drag_estimate"]["target_a_cd_mm2"], a_cd_hi <= P["drag_estimate"]["target_a_cd_mm2"], "estimativa por razão de finura, não CFD")

    # -- massas --
    add("Subtotal nominal por painel", rp["assembled_mass_g"], "≤ %.2f g" % q["mass_limit_assembled_g"], rp["assembled_mass_g"] <= q["mass_limit_assembled_g"], "Chicote de seis condutores e ferragens reais ainda não reconciliados; não é aceite de massa final")
    add("Subtotal nominal do rotor", report["rotor"]["total_mass_estimate_g"], "≤ %.2f g" % report["rotor"]["limit_g"], report["rotor"]["total_mass_estimate_g"] <= report["rotor"]["limit_g"], "Inclui Hall e contrapeso; completar orçamento dos chicotes antes do aceite de massa")
    add("Massa da aranha", rs["mass_g"], "≤ %.0f g (alvo)" % sp["mass_limit_g"], rs["mass_g"] <= sp["mass_limit_g"], "alvo para cubo Ø92 e baia de 29 mm")
    add("Massa da tampa", report["lid"]["mass_g"], "≤ %.0f g (alvo)" % P["lid"]["mass_limit_g"], report["lid"]["mass_g"] <= P["lid"]["mass_limit_g"], "alvo revisto para Ø82")
    if rb["mass_limit_g"]:
        add("Massa da base + torre", rb["mass_g"], "≤ %.0f g (alvo)" % rb["mass_limit_g"], rb["mass_g"] <= rb["mass_limit_g"], "peça estática; o custo é tempo de impressão")

    # -- base --
    add("Perpendicularidade torre/base", 0.0, "≤ 1°", True, "no CAD é zero; verificar na peça impressa")
    add("Contato da base", 0.0, "sem balanço; ≤ 0,2 mm em 3 pontos a 120°", True, "no CAD é plano; verificar na peça impressa")
    nm = sum(s["non_manifold_edges"] for s in stats.values())
    add("Malhas (arestas não-manifold no gerador)", nm, "0", nm == 0, "validação independente em reports/stl_validation.json")
    bed = P["fdm_rules"]["printer_bed_mm"]
    base_xy = [stats["base_tower"]["dimensions_mm"][i] + 2 * P["fdm_rules"]["brim_mm"] for i in (0, 1)]
    add("Base + brim cabe na mesa", base_xy, "≤ %s mm (X e Y)" % bed, all(v <= limit for v, limit in zip(base_xy, bed)), "envelope medido em cada eixo, com o brim configurado")
    fl = rb["floor_under_flange_bolt_solid_mm"]
    if not suspended:
        add("Piso da baia íntegro sob os furos da flange", fl, "sólido de Z = 0 até a flange inferior (12)", fl is not None and abs(fl[0]) < 0.05 and fl[1] >= P["base_tower"]["central_floor_thickness"] + P["base_tower"]["flange_thickness"] - 0.05, "06-PENDENCIAS B3; furos só na flange superior: %s" % rb["upper_flange_hole_free"])
    # NOVO (revisão de 03/09, item 3). As cabeças dos M3 do motor ficam entre a chapa
    # e a flange; sem rebaixo a chapa apoia nelas e o Datum B sai alto.
    rec_d = rb.get("flange_motor_recess_depth_mm")
    rec_r = rb.get("flange_recess_free_radius_mm")
    head_h = rb.get("motor_screw_head_height_mm")
    head_d = rb.get("motor_screw_head_diameter_mm")
    r_screw = rb.get("motor_screw_radius_mm")
    if None not in (rec_d, rec_r, head_h, head_d, r_screw):
        need_r = r_screw + head_d / 2 + 0.3
        add(
            "Rebaixo da flange livra as cabeças dos M3 do motor",
            [rec_d, rec_r],
            "profundidade ≥ %.1f mm e raio livre ≥ %.1f mm" % (head_h + 0.3, need_r),
            rec_d >= head_h + 0.3 and rec_r >= need_r,
            "medido na malha; cabeça Ø%.1f × %.1f em r = %.2f (cruz de diagonais %g e %g). Os M4 em PCD %g ficam fora do rebaixo e continuam definindo o assento da chapa"
            % (head_d, head_h, r_screw, P["unverified_interfaces"]["motor"]["base_bolt_diagonal_x"], P["unverified_interfaces"]["motor"]["base_bolt_diagonal_y"], P["base_tower"]["flange_hole_pcd"]),
        )
    if rb.get("clamp_tab_hole_free") is not None:
        add("Abas de grampo com furo livre", rb["clamp_tab_hole_free"], "livre", rb["clamp_tab_hole_free"], "%d abas a %.0f°, furo Ø%.0f em r = %.0f" % (P["base_tower"]["clamp_tabs"]["count"], 360.0 / P["base_tower"]["clamp_tabs"]["count"], P["base_tower"]["clamp_tabs"]["hole_diameter"], P["base_tower"]["clamp_tabs"]["hole_radius"]))
    strip_ok = rp["led_strip_top_z_mm"] <= rp["panel_top_z_mm"]
    add("Fita de 201,4 mm cabe no canal", rp["led_strip_top_z_mm"], "≤ 104 mm (topo do painel)", strip_ok, "batente em Z=%.1f por causa do bolso de fios" % rp["led_channel_start_z_mm"])

    # -- suporte do ímã --
    mb = report["magnet_bracket"]
    add("Suporte do ímã com dois pontos de fixação", mb["bolts"], "≥ 2 parafusos", mb["bolts"] >= 2, "06-PENDENCIAS B4; arco a %.1f mm da campânula" % mb["arc_to_bell_clearance_mm"])
    flange_az = [(P["base_tower"]["flange_hole_angle_offset_deg"] + 90.0 * i) % 360.0 for i in range(4)]
    bracket_az = [az % 360.0 for az in P["magnet_bracket"]["bolt_azimuths_deg"]]
    misaligned = [az for az in bracket_az if min(abs((az - f + 180.0) % 360.0 - 180.0) for f in flange_az) > 0.01]
    add("Furos do suporte do ímã coincidem com os M4 da flange", bracket_az, "cada furo do suporte sobre um M4", not misaligned,
        "M4 da flange a %s°" % ", ".join("%g" % f for f in flange_az))
    add("Folga do suporte do ímã à campânula", mb["arc_to_bell_clearance_mm"], "≥ 2 mm", mb["arc_to_bell_clearance_mm"] >= 2.0, "campânula medida em Ø%.0f" % P["unverified_interfaces"]["motor"]["body_diameter"])

    # -- provisão do cilindro (fora de escopo) --
    cg = report["containment"]
    if cg["enabled"]:
        add("Canaleta de assento dentro da pista", [cg["inner_lip_mm"], cg["outer_lip_mm"]], "lábios ≥ 1,2 mm", cg["fits_track"], "provisão (invólucro fora de escopo): canaleta r %.1f–%.1f" % (cg["groove_inner_radius_mm"], cg["groove_outer_radius_mm"]))
        add("Cilindro encomendado cabe na canaleta", [cg["clearance_inner_mm"], cg["clearance_outer_mm"]], "folga ≥ 0 nos dois lados", cg["cylinder_fits_groove"], "Ø int %.0f, parede %.0f, contra canaleta de %.1f" % (cg["cylinder_inner_diameter_mm"], cg["cylinder_wall_mm"], cg["groove_width_mm"]))
        add("Folga radial rotor → cilindro encomendado", cg["radial_clearance_mm"], "≥ 10 mm após deflexão", cg["radial_clearance_mm"] >= 10.0, "informativo: raio dinâmico %.1f contra Ø int %.0f" % (cg["rotor_dynamic_radius_mm"], cg["cylinder_inner_diameter_mm"]))
        margin = report["assembly"]["containment_vertical_margin_mm"]
        add("Folga vertical topo do rotor → borda do cilindro encomendado", margin, "≥ 10 mm", margin >= 10.0, "informativo: cilindro de %.0f mm apoiado em Z=%.0f" % (cg["cylinder_height_mm"], cg["rest_z_mm"]))
    if suspended:
        su = report["suspension"]
        est = su["estimate"]
        sq = susp
        chosen = next(v for v in est["variants"] if abs(v["rod_side_mm"] - est["selected_variant_side_mm"]) < 1e-9)
        scan = measured["suspension"]["frame_winding_scan"]
        add("Enrolamento por raios — base fixa", [scan["bad_winding_segments"], scan["thin_solid_segments"]], "0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm", scan["bad_winding_segments"] == 0 and scan["thin_solid_segments"] == 0, "%d raios, passo %.1f mm" % (scan["rays"], scan["pitch_mm"]))
        for name, m in measured["flexures"].items():
            scan = m["winding_scan"]
            add("Enrolamento por raios — haste %s" % name, [scan["bad_winding_segments"], scan["thin_solid_segments"]], "0 trechos com enrolamento ∉ {0,1} · 0 lâminas < 0,02 mm", scan["bad_winding_segments"] == 0 and scan["thin_solid_segments"] == 0, "%d raios, passo %.1f mm" % (scan["rays"], scan["pitch_mm"]))
        travel = sq["stops"]["travel"]
        add("Curso radial do palco até o batente impresso", su.get("radial_travel_mm"), "%.1f ±0,1 mm" % travel, num_ok(su.get("radial_travel_mm"), travel - 0.1, travel + 0.1), "medido nas malhas: orelha do palco em r = %s, batente em r = %s" % (su["lug_tip_radius_mm"], su["hard_stop_radius_mm"]))
        gap = sq["stops"]["eva"]["engage_gap"]
        add("Calço de EVA entra antes do batente rígido", su.get("eva_engage_gap_mm"), "folga de %.1f ±0,1 mm até o calço de %.0f mm" % (gap, sq["stops"]["eva"]["pad_thickness"]), num_ok(su.get("eva_engage_gap_mm"), gap - 0.1, gap + 0.1), "fundo do bolso medido em r = %s; sem EVA vale só o batente impresso" % su["eva_pocket_floor_radius_mm"])
        lip = sq["stops"]["lip_gap"]
        add("Limitador de inclinação sobre as orelhas", su.get("tilt_lip_gap_mm"), "%.1f ±0,1 mm acima da orelha" % lip, num_ok(su.get("tilt_lip_gap_mm"), lip - 0.1, lip + 0.1), "medido na malha; se uma haste flambar ou romper a inclinação para em %s°; sobreposição orelha/batente com o palco todo deslocado: %s mm" % (su.get("tilt_cap_deg"), su.get("cheek_overlap_at_full_travel_mm")))
        add("Batente de giro (yaw) do palco", su.get("tangential_gap_mm"), "%.1f ±0,1 mm de cada lado da orelha" % sq["stops"]["side_gap"], num_ok(su.get("tangential_gap_mm"), sq["stops"]["side_gap"] - 0.1, sq["stops"]["side_gap"] + 0.1), "medido; limita a torção das hastes na partida")
        channel = sq["block"]["width"] + 2 * sq["seat"]["block_side_clearance"]
        add("Guias dos assentos: canal do bloco em cima e em baixo", su.get("seat_channel_width_top_bottom_mm"), "%.1f ±0,15 mm nos dois" % channel, all(num_ok(w, channel - 0.15, channel + 0.15) for w in su.get("seat_channel_width_top_bottom_mm", [None])), "medido nas malhas da base fixa e do palco; bloco de %.0f mm" % sq["block"]["width"])
        add("Furos M3 dos assentos livres (base fixa e palco)", [sum(su["frame_seat_bores_free"]), sum(su["stage_seat_bores_free"])], "%d em cima e %d em baixo" % (sq["rod"]["count"], sq["rod"]["count"]), all(su["frame_seat_bores_free"]) and all(su["stage_seat_bores_free"]), "raio ao longo do eixo de cada parafuso")
        clear = report["assembly"]["rotor_z_min_mm"] - su["frame_top_z_mm"]
        add("Folga vertical painéis → topo da base fixa", round(clear, 2), "≥ 5 mm", clear >= 5.0, "ponta inferior dos painéis em Z = %.1f; topo da base fixa medido em Z = %.1f" % (report["assembly"]["rotor_z_min_mm"], su["frame_top_z_mm"]))
        frame_xy = [v + 2 * P["fdm_rules"]["brim_mm"] for v in su["frame_extent_xy_mm"]]
        add("Base fixa + brim cabe na mesa", frame_xy, "≤ %s mm (X e Y)" % bed, all(v <= limit for v, limit in zip(frame_xy, bed)), "imprime invertida, teto na mesa")
        if su.get("clamp_tab_hole_free") is not None:
            add("Abas de grampo com furo livre", su["clamp_tab_hole_free"], "livre", su["clamp_tab_hole_free"], "na base fixa")
        lo_rpm, hi_rpm = est["operating_rpm_range"]
        add("Translação do palco abaixo da faixa de giro (estimativa)", round(chosen["translation_frequency_hz"], 2), "≤ %.1f Hz (metade de %.0f RPM)" % (lo_rpm / 120.0, lo_rpm), chosen["translation_frequency_hz"] <= lo_rpm / 120.0, "haste de %.1f mm, massa móvel %.2f kg, %.2f N/mm; crítica em %.0f RPM. Não medido" % (chosen["rod_side_mm"], est["moving_mass_kg"], chosen["lateral_stiffness_n_per_mm"], chosen["translation_critical_rpm"]))
        coupled = chosen["coupled_rocking_tower_frequency_hz"]
        add("Modo combinado balanço + torre acima de 2× (estimativa)", round(coupled, 1), "≥ %.0f Hz (2 × %.0f RPM, com 10%% de margem)" % (2.2 * hi_rpm / 60.0, hi_rpm), coupled >= 2.2 * hi_rpm / 60.0, "balanço e flexão da torre em série; 3× cruza este modo perto de %.0f RPM: se o ensaio de impacto der menos de 95 Hz, limitar a %.0f RPM" % (coupled * 20.0, coupled * 20.0 * 0.92))
        add("Balanço (rocking) do palco acima de 1× (estimativa)", round(chosen["rocking_frequency_hz"], 1), "≥ %.0f Hz (1,3 × %.0f RPM)" % (1.3 * hi_rpm / 60.0, hi_rpm), chosen["rocking_frequency_hz"] >= 1.3 * hi_rpm / 60.0, "hastes em série com as aletas; %.3f° de inclinação por 10 N no rotor. Torre acima das aletas: %.0f Hz. Não medido" % (chosen["tilt_deg_per_10n_at_rotor"], est["tower_bending_frequency_hz"]))
        add("Flambagem das hastes do lado comprimido (estimativa)", round(chosen["rotor_side_force_at_first_buckling_n"], 1), "≥ 25 N de força lateral no rotor (5 g a 100 mm e 1800 RPM dão 17,8 N)", chosen["rotor_side_force_at_first_buckling_n"] >= 25.0, "carga crítica %.1f N por haste (biengastada, sem deslocamento lateral relativo); acima disso vale o limitador de inclinação" % chosen["rod_buckling_load_n"])
        add("Modo de giro (yaw) do palco — informativo", round(chosen["yaw_frequency_hz"], 1), "registrado; não é excitado pelo desbalanceamento (força passa pelo eixo)", True, "%.0f RPM em 1×, DENTRO da faixa %.0f–%.0f RPM e sem amortecimento: observar no ensaio; travar o palco elimina o modo" % (chosen["yaw_frequency_hz"] * 60.0, lo_rpm, hi_rpm))
        add("Tensão de flexão da haste no batente (estimativa)", round(chosen["rod_bending_stress_at_stop_mpa"], 1), "≤ 12 MPa", chosen["rod_bending_stress_at_stop_mpa"] <= 12.0, "E = %.0f MPa assumido; tração pelo peso %.2f MPa" % (sq["rod"]["modulus_mpa"], chosen["rod_tension_stress_mpa"]))
    sections = report["physics"].get("arm_sections")
    if sections:
        # Todas as seções entre a raiz e a espiga, não só a raiz: o reforço desloca o ponto fraco.
        worst = max(sections, key=lambda sec: sec["tilt_cases"][-1]["max_bending_stress_mpa"])
        add("Braço da aranha: flexão vertical com o eixo inclinado (estimativa)", [round(sec["tilt_cases"][-1]["max_bending_stress_mpa"], 1) for sec in sections], "≤ 12 MPa a %g° em todas as seções (r = %s mm), %.0f RPM, painel de %.0f g" % (worst["tilt_cases"][-1]["tilt_deg"], ", ".join("%g" % sec["cut_radius_mm"] for sec in sections), worst["rpm"], worst["panel_mass_g"]), worst["tilt_cases"][-1]["max_bending_stress_mpa"] <= 12.0, "seções medidas na malha; a pior é r = %.1f (módulo resistente %.0f mm³): a espiga 11 × 6 dentro do painel é o limite. Sem concentração de tensão nem propriedades FDM" % (worst["cut_radius_mm"], worst["section_modulus_vertical_mm3"]))
    cap = report["containment_cap"]
    if cap["enabled"]:
        qc = P["containment_cap"]
        add("Tampa: aberturas menores que a seção do painel", cap["max_opening_mm"], "≤ %.0f mm" % qc["max_opening_diameter"], cap["max_opening_mm"] <= qc["max_opening_diameter"], "%d furos" % len(cap["holes"]))
        add("Tampa: área livre de ventilação", cap["free_area_mm2"], "≥ %.0f mm²" % qc["min_free_area_mm2"], cap["free_area_mm2"] >= qc["min_free_area_mm2"])
        add("Tampa + brim cabe na mesa", cap["footprint_with_brim_mm"], "≤ %s mm" % bed, cap["footprint_with_brim_mm"] <= min(bed))
    return checks


def write_acceptance_md(checks: list[dict], path: Path) -> None:
    lines = [
        "# Critérios de aceitação — Hologram Orbiter v%s" % P["project"]["version"],
        "",
        "Verificação automática a partir do modelo (spec §9). Gerado por `CAD/generate.py`.",
        "Valores marcados como medidos vêm de traçado de raios na malha final (`CAD/probe.py`),",
        "não dos parâmetros de entrada.",
        "**CAD provisório: aprovação geométrica não libera giro nem fabricação definitiva dos painéis.**",
        "Consulte `FISICA.json` e os bloqueadores de resistência, fluência, massa e instrumentação.",
        "",
        "| Critério | Valor no modelo | Requisito | Resultado | Nota |",
        "|---|---:|---|:---:|---|",
    ]
    for c in checks:
        value = c["valor"]
        if isinstance(value, list):
            value = " – ".join(str(v) for v in value)
        lines.append(f"| {c['criterio']} | {value} | {c['requisito']} | {'✅' if c['passa'] else '❌'} | {c['nota']} |")
    failed = [c for c in checks if not c["passa"]]
    lines += ["", f"**Resultado:** {len(checks) - len(failed)} de {len(checks)} critérios atendidos."]
    if failed:
        lines.append("")
        lines.append("Reprovados: " + ", ".join(c["criterio"] for c in failed))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    output_dir = ARGS.output_dir.resolve()
    stl_dir = output_dir / "stl"
    report_dir = ARGS.report_dir.resolve()
    stl_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    clear_scene()
    bpy.context.scene.unit_settings.system = "METRIC"
    bpy.context.scene.unit_settings.length_unit = "MILLIMETERS"
    bpy.context.scene.unit_settings.scale_length = 0.001

    print("[1/9] Modelando painel...")
    panel = build_panel()
    print("[2/9] Modelando aranha...")
    spider = build_spider()
    print("[3/9] Modelando tampa...")
    lid = build_lid()
    print("[4/9] Modelando base + torre...")
    base_tower = build_suspended_stage() if SUSPENDED else build_base_tower()
    base_frame = build_suspension_frame() if SUSPENDED else None
    flexures = {name: build_flexure(side, name) for name, side in SUSP["rod"]["variants"].items()} if SUSPENDED else {}
    lock_spacer = build_lock_spacer() if SUSPENDED and SUSP.get("lock", {}).get("enabled") else None
    oil_cup = build_oil_tray() if SUSPENDED and SUSP.get("oil_damper", {}).get("enabled") else None
    print("[5/9] Modelando suporte do ímã, cupons e chapa de referência...")
    magnet_bracket = build_magnet_bracket()
    containment_cap = build_containment_cap() if P["containment_cap"]["enabled"] else None
    joint_coupon = build_joint_coupon()
    led_coupon = build_led_coupon(panel)
    motor_plate = build_motor_plate_reference()

    parts = {
        "spider": spider,
        "panel": panel,
        "lid": lid,
        "base_tower": base_tower,
        "magnet_bracket": magnet_bracket,
        "joint_coupon": joint_coupon,
        "led_coupon": led_coupon,
        "motor_plate": motor_plate,
    }
    if containment_cap is not None:
        parts["containment_cap"] = containment_cap
    if SUSPENDED:
        parts["base_frame"] = base_frame
        for name, obj in flexures.items():
            parts[f"flexure_{name}"] = obj
        if lock_spacer is not None:
            parts["lock_spacer"] = lock_spacer
        if oil_cup is not None:
            parts["oil_cup"] = oil_cup
    for obj in parts.values():
        apply_location(obj)  # malha em coordenadas do mundo: medição e centróide corretos
        cleanup_mesh(obj)

    print("[6/9] Exportando STL...")
    pp = P["panel"]["print"]
    s = pp["batch_spacing_y"]
    stale = stl_dir / "07_tampa_contencao_ABS.stl"
    if containment_cap is None and stale.exists():
        stale.unlink()
    stale_post = stl_dir / "06_poste_ima_ABS.stl"
    if stale_post.exists():
        stale_post.unlink()
    export_stl(spider, stl_dir / export_name("spider"))
    export_stl(panel, stl_dir / "02_painel_LED_ABS_1x.stl", rotate_y_deg=pp["rotate_y_deg"])
    export_stl(panel, stl_dir / "02_painel_LED_ABS_3x_mesma_mesa.stl", rotate_y_deg=pp["rotate_y_deg"], copies=[(0.0, -s, 0.0), (0.0, 0.0, 0.0), (0.0, s, 0.0)])
    export_stl(lid, stl_dir / export_name("lid"))
    export_stl(base_tower, stl_dir / export_name("base_tower"))
    export_stl(magnet_bracket, stl_dir / export_name("magnet_bracket"))
    if SUSPENDED:
        # Base fixa: teto na mesa. Hastes: deitadas, face de assento na mesa.
        export_stl(base_frame, stl_dir / export_name("base_frame"), rotate_x_deg=180.0)
        pitch = SUSP["block"]["width"] + 4.0
        count = SUSP["rod"]["count"]
        for name, obj in flexures.items():
            export_stl(obj, stl_dir / export_name("flexure_single", name=name), rotate_y_deg=-90.0)
            export_stl(obj, stl_dir / export_name("flexure_batch", name=name), rotate_y_deg=-90.0,
                       copies=[(0.0, (i - (count - 1) / 2) * pitch, 0.0) for i in range(count)])
        if lock_spacer is not None:
            n_lock = len(SUSP["lock"]["azimuths_deg"])
            export_stl(lock_spacer, stl_dir / export_name("lock_spacer"), copies=[((i - (n_lock - 1) / 2) * 14.0, 0.0, 0.0) for i in range(n_lock)])
        if oil_cup is not None:
            export_stl(oil_cup, stl_dir / export_name("oil_tray"))
    if containment_cap is not None:
        export_stl(containment_cap, stl_dir / "07_tampa_contencao_ABS.stl", rotate_x_deg=180.0)
    export_stl(joint_coupon, stl_dir / "C01_cupom_junta.stl")
    export_stl(led_coupon, stl_dir / "C02_cupom_canal_LED.stl", rotate_y_deg=pp["rotate_y_deg"])
    export_stl(motor_plate, stl_dir / "R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl")

    print("[7/9] Medindo a malha e calculando o relatório geométrico...")
    abs_density = P["material"]["abs_density_g_cm3"]
    al_density = P["material"]["aluminium_density_g_cm3"]
    stats = {
        "spider": object_stats(spider, density_for("spider")),
        "panel_each": object_stats(panel, abs_density),
        "lid": object_stats(lid, density_for("lid")),
        "base_tower": object_stats(base_tower, density_for("base_tower")),
        "magnet_bracket": object_stats(magnet_bracket, density_for("magnet_bracket")),
        **({"base_frame": object_stats(base_frame, density_for("base_frame"))} if SUSPENDED else {}),
        **{f"flexure_{name}": object_stats(obj, density_for("flexure")) for name, obj in flexures.items()},
        **({"lock_spacer": object_stats(lock_spacer, density_for("flexure"))} if lock_spacer is not None else {}),
        **({"oil_cup": object_stats(oil_cup, density_for("flexure"))} if oil_cup is not None else {}),
        **({"containment_cap": object_stats(containment_cap, abs_density)} if containment_cap is not None else {}),
        "joint_coupon": object_stats(joint_coupon, abs_density),
        "led_coupon": object_stats(led_coupon, abs_density),
        "motor_plate_reference_aluminium": object_stats(motor_plate, al_density),
    }
    measured = {
        "panel": measure_panel(panel),
        "spider": measure_spider(spider),
        "lid": measure_simple(lid, 1.0),
        "base": measure_base(base_tower),
        "magnet_bracket": measure_simple(magnet_bracket, 0.5),
        "bay_intersections": measure_bay_intersections(spider),
    }
    if SUSPENDED:
        measured["suspension"] = measure_suspension(base_frame, base_tower)
        measured["flexures"] = {name: measure_simple(obj, 0.5) for name, obj in flexures.items()}
    shoulders = [v for v in measured["spider"]["shoulder_radius_mm"] if v is not None]
    panel_radius = (sum(shoulders) / len(shoulders) - P["panel"]["boss"]["contact_face_x"]) if shoulders else P["assembly"]["panel_radius"]

    print("[8/9] Salvando BLEND e renderizando prévia...")
    assembly = assemble_and_save(parts, output_dir, render_preview=not ARGS.no_render, panel_radius=panel_radius)

    print("[9/9] Escrevendo relatórios...")
    physics = calculate_physics(P, triangles_of(panel))
    physics["arm_root"] = arm_root_estimate(P, triangles_of(spider))
    radii = P["spider"]["arm"].get("reinforcement", {}).get("check_radii_mm")
    if radii:
        physics["arm_sections"] = [arm_root_estimate(P, triangles_of(spider), r) for r in radii]
    derived = compute_report(stats, measured, assembly, physics)
    if SUSPENDED:
        derived["suspension"] = {
            **{k: v for k, v in measured["suspension"].items() if k != "frame_winding_scan"},
            "frame_mass_g": stats["base_frame"]["estimated_mass_g"],
            "stage_mass_g": stats["base_tower"]["estimated_mass_g"],
            "estimate": suspension_estimate(P, derived["rotor"]["total_mass_estimate_g"], stats["base_tower"]["estimated_mass_g"],
                                            stats["base_tower"]["centroid_mm"][2], assembly["datum_b_z_mm"],
                                            inertia_about_z(triangles_of(base_tower), density_for("base_tower"))),
        }
        physics["suspension"] = derived["suspension"]["estimate"]
    checks = acceptance(derived, stats, measured)
    report = {
        "project": P["project"],
        "status": P["status"],
        "release": P["release"],
        "all_geometry_checks_pass": all(c["passa"] for c in checks),
        "operating_point": P["operating_point"],
        "geometry": stats,
        "derived": derived,
        "acceptance": checks,
        "unverified_interfaces": P["unverified_interfaces"],
    }
    with (report_dir / "geometry_report.json").open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    write_acceptance_md(checks, report_dir / "ACEITACAO.md")
    (report_dir / "FISICA.json").write_text(json.dumps(physics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_validation_summary(report, report_dir / "RELATORIO_VALIDACAO.md")
    for c in checks:
        print(f"  {'OK   ' if c['passa'] else 'FALHA'} {c['criterio']}: {c['valor']} ({c['requisito']})")
    print(f"Concluído: {output_dir}")
    sys.stdout.flush()
    sys.stderr.flush()
    if bpy.app.background:
        os._exit(0 if all(c["passa"] for c in checks) else 1)


def write_validation_summary(report: dict, path: Path) -> None:
    """Generated from this build: the previous hand-maintained report drifted."""
    d = report["derived"]
    physics = d["physics"]
    section = physics["section"]
    checks = report["acceptance"]
    rows = ["# Relatório de validação CAD — v%s" % report["project"]["revision"].split(" ")[0], "",
            "Gerado por CAD/generate.py na mesma execução de geometry_report.json e FISICA.json.",
            "**PROVISÓRIO: não libera operação nem fabricação definitiva dos painéis.**", "",
            "## Geometria", "",
            f"Critérios: {sum(c['passa'] for c in checks)}/{len(checks)}. Ver ACEITACAO.md para requisitos e cobertura.",
            "A validação dos STL exportados aparece em stl_validation.json; o build só publica se ela também passar.", "",
            "| Peça | Massa CAD (g) | Dimensões (mm) | Triângulos |", "|---|---:|---|---:|"]
    for key, value in report["geometry"].items():
        rows.append(f"| {key} | {value['estimated_mass_g']} | {value['dimensions_mm']} | {value['triangles']} |")
    rows += ["", "## Física", "",
             f"Iyy da seção = {section['Iyy_mm4']:.4f} mm⁴; centroide x = {section['centroid_x_mm']:.5f} mm.",
             "As integrais são comparadas com três cortes da malha. Propriedades FDM e engaste não certificados.", "",
             "| Massa usada | L (mm) | E (MPa) | Deflexão (mm) | Tensão máxima (MPa) |",
             "|---:|---:|---:|---:|---:|"]
    for mass, cases in ((physics['flexure']['design_panel_mass_g'], physics['flexure']['envelope_cases']),
                        (physics['flexure']['acceptance_mass_limit_g'], physics['flexure']['acceptance_limit_cases'])):
        for c in cases:
            rows.append(f"| {mass} | {c['unsupported_length_mm']} | {c['modulus_mpa']} | {c['tip_deflection_mm']:.3f} | {c['max_bending_stress_mpa']:.3f} |")
    rows += ["", f"Folga radial calculada com o teto de massa: {d['containment']['radial_clearance_mm']:.2f} mm.",
             "Carga uniforme simplificada: não representa certificação de resistência ou fluência.", "",
             "## Acionamento", ""]
    drive = physics['drive']
    start, clamp = drive['startup_kick'], drive['shaft_clamp']
    kick, ceiling = start['schedule'], start['phase_ceiling']
    def at_source(case):
        return " / ".join(f"{s['current_a']:.2f} A a {s['voltage_v']:.0f} V" for s in case['source_currents'])
    volts = "–".join(f"{v:.0f}" for v in drive['inputs_unvalidated']['source_voltages_v'])
    rows += [f"Regime: {drive['steady']['phase_current_a']:.2f} A de fase, {drive['steady']['input_power_w']:.2f} W na fonte ({at_source(drive['steady'])}).",
             f"Partida com chute (05 §8.2): {kick['ppm_min_us']}→{kick['kick_us']} µs em {kick['rise_s']:.0f} s, chute de {kick['kick_hold_s']:.0f} s, descida a {kick['fall_us_per_s']:.0f} µs/s até {kick['target_us']} µs; fonte em {volts} V com limite de {start['source_current_limit_a']:.0f} A.",
             f"Teto de {ceiling['phase_current_a']:.0f} A de fase: {ceiling['input_power_w']:.2f} W na fonte ({at_source(ceiling)}), {ceiling['torque_nm']*1000:.1f} mN·m."]
    stalls = {s['source_voltage_v']: s for s in start['stall_at_kick']}
    for c in start['trajectories']:
        s = stalls[c['source_voltage_v']]
        flags = (["passa do teto de fase"] if c['exceeds_phase_ceiling'] else []) + \
                ([f"passa dos {ceiling['input_power_w']:.2f} W do bloqueador D"] if c['exceeds_start_power_ceiling'] else []) + \
                ([f"passa de {report['operating_point']['rpm']:.0f} RPM"] if c['exceeds_operating_rpm'] else [])
        limiting = f" com a fonte limitando e o barramento em {s['bus_voltage_v']:.2f} V" if s['supply_limiting'] else ""
        rows.append(f"- Fonte em {c['source_voltage_v']:.0f} V: parado no chute, {s['phase_current_a']:.2f} A de fase e {s['input_power_w']:.1f} W / {s['source_current_a']:.2f} A na fonte{limiting}, {s['torque_nm']*1000:.1f} mN·m; "
                    f"pico de {c['peak_rpm']:.0f} RPM a {c['peak_rpm_pulse_us']:.0f} µs; fase até {c['peak_phase_current_a']:.2f} A e fonte até {c['peak_input_power_w']:.1f} W; {c['target_rpm']:.0f} RPM no alvo."
                    + (f" **No modelo, {' e '.join(flags)}.**" if flags else ""))
    peaks = ", ".join(f"{c['required_clamp_force_n']:.1f} N ({c['preload_margin']:.1f}×) no pico da partida a {c['source_voltage_v']:.0f} V" for c in clamp['kick_trajectory_peaks'])
    rows += [f"Aperto do eixo (μ {drive['inputs_unvalidated']['shaft_friction_mu']}, r {drive['inputs_unvalidated']['shaft_friction_radius_mm']:.0f} mm, pré-carga estimada {clamp['preload_estimate_n']:.0f} N): "
             f"{clamp['steady']['required_clamp_force_n']:.1f} N em regime, "
             f"{clamp['phase_ceiling']['required_clamp_force_n']:.1f} N ({clamp['phase_ceiling']['preload_margin']:.1f}×) no teto de fase, {peaks}.",
             "Modelo médio, sem o Startup Power do ESC nem a resistência da fonte e dos cabos; não é medição: conferir RPM, corrente e tensão reais no bloqueador D."]
    rows += ["", "## Montagem e orçamento nominal", "",
             f"Interseções da eletrônica com aranha: {d['bay_layout']['mesh_intersections']['components']}.",
             f"Contrapesos nominais: {d['bay_layout']['counterweight_placement']}.",
             f"Subtotal do rotor: {d['rotor']['total_mass_estimate_g']:.2f} g, limite {d['rotor']['limit_g']:.0f} g.",
             d['rotor']['mass_budget_note'], "",
             "| Referência global | Z (mm) |", "|---|---:|",
             f"| Datum B, topo do cubo | {d['assembly']['datum_b_z_mm']} |",
             f"| Trilhos/fundo da bateria | {d['assembly']['datum_b_z_mm']+d['spider']['battery_floor_z_mm']} |",
             f"| Topo da bateria | {d['assembly']['datum_b_z_mm']+d['spider']['battery_top_z_mm']} |",
             f"| Ponta do eixo | {d['assembly']['shaft_top_z_mm']} |", "",
             "## Ainda não verificado", "",
             "Resistência e fluência do painel impresso, caminho de carga, massas/chicotes reais, instrumento de fase e térmica, dropout do buck, polaridade/entreferro reais e contenção. Ver 06-PENDENCIAS-ABERTAS-v3.0.md."]
    path.write_text("\n".join(rows)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
