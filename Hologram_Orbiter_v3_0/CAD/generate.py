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
  * base/torre, chapa e poste do ímã: z = 0 na face de apoio da base;
  * tampa: z = 0 na face inferior da pele.
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
from mathutils import Vector


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--parameters", type=Path, default=HERE / "parameters.json")
    parser.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "exports")
    parser.add_argument("--no-render", action="store_true")
    return parser.parse_args(argv)


ARGS = parse_args()
with ARGS.parameters.open("r", encoding="utf-8") as stream:
    P = json.load(stream)

SEGMENTS = int(P["quality"]["curve_segments"])
BOOL_SOLVER = P["quality"]["boolean_solver"]


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


def join_cutters(cutters: list[bpy.types.Object], name: str) -> bpy.types.Object:
    if len(cutters) == 1:
        cutters[0].name = name
        return cutters[0]
    bpy.ops.object.select_all(action="DESELECT")
    for cutter in cutters:
        cutter.select_set(True)
    bpy.context.view_layer.objects.active = cutters[0]
    bpy.ops.object.join()
    cutters[0].name = name
    return cutters[0]


def subtract_all(target: bpy.types.Object, cutters: list[bpy.types.Object], label: str) -> bpy.types.Object:
    if not cutters:
        return target
    joined = join_cutters(cutters, f"{label}_cutters")
    return boolean(target, joined, "DIFFERENCE", label)


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

    # Contorno externo: flanco plano, nariz, lado da lâmina (+0,2 dentro da
    # parede para fundir), flanco traseiro externo, cauda, flanco traseiro interno.
    outer = ellipse(a, b)  # de (xf, yh) até (xb+ov, yh)
    outer[0] = (xf, yh)
    outer[-1] = (xb + ov, yh)
    outer += [
        (xb + ov, y_flat0),
        (taper_end[0] + ov, taper_end[1]),
        tail,
        (xf, -yh),
    ]

    # Contorno interno = externo deslocado t para dentro nas paredes livres.
    o4 = (taper_end[0] + ov, taper_end[1])
    d_out = unit((tail[0] - o4[0], tail[1] - o4[1]))
    n_out = (-d_out[1], d_out[0])
    if n_out[0] > 0:  # normal deve apontar para -x (interior)
        n_out = (-n_out[0], -n_out[1])
    o6 = (xf, -yh)
    d_in = unit((o6[0] - tail[0], o6[1] - tail[1]))
    n_in = (-d_in[1], d_in[0])
    if n_in[0] < 0:  # normal deve apontar para +x (interior)
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


def build_panel() -> bpy.types.Object:
    q = P["panel"]
    b = q["boss"]
    f = q["fairing"]
    ch = q["led_channel"]
    rb = q["ribs"]
    height = q["height"]
    hh = height / 2.0
    skin = q["end_skin"]

    outer_profile = [tuple(p) for p in q["profile_outer_xy"]]
    cavity_profile = [tuple(p) for p in q["profile_cavity_xy"]]

    shell = mesh_prism_z("panel_shell_outer", outer_profile, -hh, hh)
    cavity = mesh_prism_z("panel_shell_cavity", cavity_profile, -hh + skin, hh - skin)
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

    # ---- Cortes ----
    cutters: list[bpy.types.Object] = []
    x_out = q["max_thickness"] / 2  # face externa em x = +4
    channel_z0 = -hh + ch["bottom_skin"] + ch["wire_pocket_height"]
    cutters.append(
        box_xyz(
            "led_channel_cut",
            (x_out - ch["depth"], x_out + 0.5),
            (-ch["width"] / 2, ch["width"] / 2),
            (channel_z0, hh + 0.2),
        )
    )
    pocket_z0 = -hh + skin + 0.2
    cutters.append(
        box_xyz(
            "led_wire_pocket",
            (x_out - q["shell_wall"] - 0.2, x_out + 0.5),
            (-ch["wire_pocket_width"] / 2, ch["wire_pocket_width"] / 2),
            (pocket_z0, channel_z0),
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
    panel = subtract_all(panel, cutters, "panel_features")
    panel.name = "02_painel_led"
    return panel


# --------------------------------------------------------------------------
# 01 — Aranha
# --------------------------------------------------------------------------

def build_arm(index: int) -> bpy.types.Object:
    a = P["spider"]["arm"]
    airfoil = [tuple(p) for p in a["airfoil_yz"]]
    beam = mesh_prism_x(f"arm_{index}_airfoil", airfoil, a["root_radius"], a["shoulder_radius"] + 0.2)
    tenon = box_xyz(
        f"arm_{index}_tenon",
        (a["shoulder_radius"] - 0.2, a["tenon_tip_radius"]),
        (-a["tenon_width"] / 2, a["tenon_width"] / 2),
        (0.0, a["tenon_height"]),
    )
    root = mesh_prism_z(f"arm_{index}_root_blend", [tuple(p) for p in a["root_blend_xy"]], -0.1, a["height"])
    arm = union_all([beam, tenon, root], f"arm_{index}")
    return rotate_about_z(arm, index * 120.0)


def build_spider() -> bpy.types.Object:
    q = P["spider"]
    a = q["arm"]
    ui = P["unverified_interfaces"]
    hub_t = q["hub_thickness"]
    hub = cylinder("hub_disk", q["hub_diameter"] / 2, hub_t, (0.0, 0.0, -hub_t / 2))

    bay = ring("electronics_bay_wall", q["electronics_bay_od"] / 2, q["electronics_bay_id"] / 2, -0.1, q["electronics_bay_height"])
    post_x = q["lid_post_spacing"] / 2
    lid_posts = [
        cylinder(f"lid_post_{i}", q["lid_post_diameter"] / 2 + q["lid_post_ring_overlap"], q["electronics_bay_height"] + 0.1, (x, 0.0, q["electronics_bay_height"] / 2 - 0.05))
        for i, x in enumerate((-post_x, post_x))
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
    spider = union_all([hub, bay, *lid_posts, *cradle, *arms], "aranha")

    cutters: list[bpy.types.Object] = []
    bore_r = (q["bore_diameter"] + P["quality"]["fdm_bore_compensation_mm"]) / 2
    bore = cylinder("hub_bore", bore_r, hub_t + 2.0, (0.0, 0.0, -hub_t / 2))
    counterbore = cylinder(
        "hub_counterbore",
        q["counterbore_diameter"] / 2,
        q["counterbore_depth"] + 0.2,
        (0.0, 0.0, -q["counterbore_depth"] / 2 + 0.1),
    )
    cutters.append(union_all([bore, counterbore], "hub_center_cut"))
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
    pocket = cube_polar(
        "hall_pocket",
        (hs["pocket_radial"], hs["pocket_tangential"], hs["pocket_depth"] + 0.5),
        hs["radius"],
        hs["azimuth_deg"],
        -hub_t + hs["pocket_depth"] / 2 - 0.25,
    )
    slot_r = hs["radius"] - hs["pocket_radial"] / 2 + hs["lead_slot_radial"] / 2 + 0.3
    lead_slot = cube_polar(
        "hall_lead_slot",
        (hs["lead_slot_radial"], hs["lead_slot_tangential"], hub_t + 1.0),
        slot_r,
        hs["azimuth_deg"],
        -hub_t / 2,
    )
    cutters.append(union_all([pocket, lead_slot], "hall_cut"))

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
        route = union_all([window, root_pocket, groove], f"wire_route_{arm_i}")
        cutters.append(rotate_about_z(route, angle))

    for i, x in enumerate((-post_x, post_x)):
        depth = q["lid_post_hole_depth"]
        cutters.append(
            cylinder(
                f"lid_post_hole_{i}",
                q["lid_post_hole_diameter"] / 2,
                depth + 0.2,
                (x, 0.0, q["electronics_bay_height"] - depth / 2 + 0.1),
            )
        )

    spider = subtract_all(spider, cutters, "spider_features")
    spider.name = "01_aranha"
    return spider


# --------------------------------------------------------------------------
# 03 — Tampa da baia
# --------------------------------------------------------------------------

def build_lid() -> bpy.types.Object:
    q = P["lid"]
    spider = P["spider"]
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
        cylinder(f"lid_screw_hole_{i}", q["screw_hole_diameter"] / 2, q["height"] + 0.4, (x, 0.0, q["height"] / 2))
        for i, x in enumerate((-spider["lid_post_spacing"] / 2, spider["lid_post_spacing"] / 2))
    ]
    if P["unverified_interfaces"]["lid_access_window"]["enabled"]:
        w = q["access_window"]
        cutters.append(box_xyz("lid_access_window", tuple(w["x_range"]), tuple(w["y_range"]), (-0.3, q["height"] + 0.3)))
    lid = subtract_all(lid, cutters, "lid_features")
    lid.name = "03_tampa_baia"
    return lid


# --------------------------------------------------------------------------
# 04/05 — Base e torre integradas
# --------------------------------------------------------------------------

def containment_geometry() -> dict:
    """Canaleta de assento na pista externa e posição do cilindro de contenção."""
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
    central_inner = cylinder(
        "central_bay_inner",
        bay_r - q["central_bay_wall"],
        bay_h - floor_z + 0.2,
        (0.0, 0.0, (bay_h + floor_z) / 2 + 0.05),
    )
    central_bay = boolean(central_outer, central_inner, "DIFFERENCE", "central_bay_hollow")

    outer_ring = ring("base_outer_ring", q["footprint_diameter"] / 2, q["outer_ring_inner_diameter"] / 2, 0.0, q["outer_ring_height"])
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

    tower_top = floor_z + q["tower_total_height_from_floor"]
    tower = cylinder("tower_outer", q["tower_od"] / 2, tower_top - floor_z + 0.1, (0.0, 0.0, (floor_z + tower_top) / 2 - 0.05))
    bore_z0 = q["tower_bore_start_z"]
    lower_flange = cylinder("tower_lower_flange", q["flange_diameter"] / 2, q["flange_thickness"], (0.0, 0.0, floor_z + q["flange_thickness"] / 2))
    upper_flange = cylinder("tower_upper_flange", q["flange_diameter"] / 2, q["flange_thickness"], (0.0, 0.0, tower_top - q["flange_thickness"] / 2))
    base = union_all([central_bay, outer_ring, *ribs, tower, lower_flange, upper_flange], "base_torre")
    # As nervuras cruzam as peças adjacentes 0,1 mm em Z para evitar faces
    # coplanares internas. Este corte devolve uma única face de apoio plana.
    bottom_trim = cube("base_bottom_trim", (q["footprint_diameter"] + 40.0, q["footprint_diameter"] + 40.0, 20.0), (0.0, 0.0, -9.9999))
    base = boolean(base, bottom_trim, "DIFFERENCE", "base_flatten_bottom")

    cutters: list[bpy.types.Object] = []
    # Furo central da torre, atravessando as duas flanges, a partir de
    # tower_bore_start_z; a janela lateral liga a baia ao interior do tubo.
    bore = cylinder("tower_bore", q["tower_od"] / 2 - q["tower_wall"], tower_top - bore_z0 + 1.0, (0.0, 0.0, (bore_z0 + tower_top) / 2 + 0.5))
    ww = q["wire_window"]
    window = cube("tower_wire_window", tuple(ww["size_xyz"]), tuple(ww["center_xyz"]))
    cutters.append(union_all([bore, window], "tower_cut"))

    flange_r = q["flange_hole_pcd"] / 2
    for i in range(4):
        x, y = polar(flange_r, q["flange_hole_angle_offset_deg"] + i * 90.0)
        cutters.append(cylinder(f"flange_hole_{i}", q["flange_hole_diameter"] / 2, tower_top + 2.0, (x, y, tower_top / 2)))

    ph = q["peripheral_holes"]
    if ph["enabled"]:
        for i in range(ph["count"]):
            x, y = polar(ph["pcd"] / 2, ph["angle_offset_deg"] + i * 360.0 / ph["count"])
            cutters.append(cylinder(f"peripheral_hole_{i}", ph["diameter"] / 2, q["outer_ring_height"] + 0.4, (x, y, q["outer_ring_height"] / 2)))

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

    base = subtract_all(base, cutters, "base_tower_openings")
    base.name = "04_05_base_torre_integradas"
    return base


# --------------------------------------------------------------------------
# 07 — Tampa do cilindro de contenção (parte fixa)
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
    cap = subtract_all(cap, cutters, "cap_features")
    cap.name = "07_tampa_contencao"
    return cap


# --------------------------------------------------------------------------
# 06 — Poste do ímã (parte fixa)
# --------------------------------------------------------------------------

def datum_b_z() -> float:
    bt = P["base_tower"]
    return bt["central_floor_thickness"] + bt["tower_total_height_from_floor"] + P["motor_plate"]["thickness"] + P["unverified_interfaces"]["motor_stack"]["plate_top_to_datum_b"]


def plate_top_z() -> float:
    bt = P["base_tower"]
    return bt["central_floor_thickness"] + bt["tower_total_height_from_floor"] + P["motor_plate"]["thickness"]


def magnet_post_height() -> float:
    q = P["magnet_post"]
    datum_a = datum_b_z() - P["spider"]["hub_thickness"]
    return datum_a - plate_top_z() - q["air_gap"]


def build_magnet_post() -> bpy.types.Object:
    q = P["magnet_post"]
    bolt = polar(q["bolt_radius"], q["bolt_azimuth_deg"])
    post = polar(q["post_radius"], q["post_azimuth_deg"])
    d = unit((post[0] - bolt[0], post[1] - bolt[1]))
    n = (-d[1], d[0])
    ext = q["tab_width"] / 2 + 1.0
    hw = q["tab_width"] / 2
    p0 = (bolt[0] - d[0] * ext, bolt[1] - d[1] * ext)
    p1 = (post[0] + d[0] * ext, post[1] + d[1] * ext)
    tab_poly = [
        (p0[0] + n[0] * hw, p0[1] + n[1] * hw),
        (p1[0] + n[0] * hw, p1[1] + n[1] * hw),
        (p1[0] - n[0] * hw, p1[1] - n[1] * hw),
        (p0[0] - n[0] * hw, p0[1] - n[1] * hw),
    ]
    tab = mesh_prism_z("magnet_tab", tab_poly, 0.0, q["tab_thickness"])
    height = magnet_post_height()
    column = cylinder("magnet_column", q["post_diameter"] / 2, height, (post[0], post[1], height / 2))
    part = union_all([tab, column], "poste_ima")
    cutters = [
        cylinder("magnet_tab_bolt_hole", q["bolt_hole_diameter"] / 2, q["tab_thickness"] + 1.0, (bolt[0], bolt[1], q["tab_thickness"] / 2)),
        cylinder("magnet_pocket", q["magnet_pocket_diameter"] / 2, q["magnet_pocket_depth"] + 0.2, (post[0], post[1], height - q["magnet_pocket_depth"] / 2 + 0.1)),
    ]
    part = subtract_all(part, cutters, "magnet_post_features")
    part.name = "06_poste_ima"
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


def build_led_coupon() -> bpy.types.Object:
    ch = P["panel"]["led_channel"]
    bx, by, bz = P["coupons"]["led_block"]
    block = cube("led_coupon_block", (bx, by, bz), (0.0, 0.0, bz / 2))
    channel = box_xyz("led_coupon_channel", (bx / 2 - ch["depth"], bx / 2 + 0.5), (-ch["width"] / 2, ch["width"] / 2), (ch["bottom_skin"] + ch["wire_pocket_height"], bz + 0.5))
    pocket = box_xyz("led_coupon_wire_pocket", (bx / 2 - P["panel"]["shell_wall"] - 0.2, bx / 2 + 0.5), (-ch["wire_pocket_width"] / 2, ch["wire_pocket_width"] / 2), (ch["bottom_skin"], ch["bottom_skin"] + ch["wire_pocket_height"]))
    coupon = subtract_all(block, [channel, pocket], "coupon_led_features")
    coupon.name = "C02_cupom_canal_LED"
    return coupon


def build_motor_plate_reference() -> bpy.types.Object:
    q = P["motor_plate"]
    motor = P["unverified_interfaces"]["motor"]
    plate = cube("motor_plate_reference", (q["width"], q["depth"], q["thickness"]), (0.0, 0.0, q["thickness"] / 2))
    cutters = []
    hx = motor["base_bolt_rectangle_x"] / 2
    hy = motor["base_bolt_rectangle_y"] / 2
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        cutters.append(cylinder(f"motor_plate_motor_hole_{i}", motor["base_bolt_hole_diameter"] / 2, q["thickness"] + 0.4, (sx * hx, sy * hy, q["thickness"] / 2)))
    bt = P["base_tower"]
    for i in range(4):
        x, y = polar(bt["flange_hole_pcd"] / 2, bt["flange_hole_angle_offset_deg"] + i * 90.0)
        cutters.append(cylinder(f"motor_plate_flange_hole_{i}", bt["flange_hole_diameter"] / 2, q["thickness"] + 0.4, (x, y, q["thickness"] / 2)))
    cutters.append(cylinder("motor_plate_center_clearance", q["center_clearance_diameter"] / 2, q["thickness"] + 0.4, (0.0, 0.0, q["thickness"] / 2)))
    plate = subtract_all(plate, cutters, "motor_plate_holes")
    plate.name = "R01_suporte_motor_aluminio_NAO_IMPRIMIR"
    return plate


# --------------------------------------------------------------------------
# Medição, exportação e relatório
# --------------------------------------------------------------------------

def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords))),
        Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords))),
    )


def mesh_volume_centroid(obj: bpy.types.Object) -> tuple[float, Vector]:
    """Volume assinado e centróide volumétrico (soma de tetraedros)."""
    mesh = obj.data
    mesh.calc_loop_triangles()
    verts = mesh.vertices
    total = 0.0
    acc = Vector((0.0, 0.0, 0.0))
    for tri in mesh.loop_triangles:
        v0 = verts[tri.vertices[0]].co
        v1 = verts[tri.vertices[1]].co
        v2 = verts[tri.vertices[2]].co
        vol = v0.dot(v1.cross(v2)) / 6.0
        total += vol
        acc += (v0 + v1 + v2) * (vol / 4.0)
    if abs(total) < 1e-9:
        return 0.0, Vector((0.0, 0.0, 0.0))
    return total, acc / total


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
        ring("REF_contencao_base", outer, inner_r, z0, z0 + 1.0),
        ring("REF_contencao_topo", outer, inner_r, z0 + height - 1.0, z0 + height),
    ]
    mean_r = (inner_r + outer) / 2
    for i in range(16):
        x, y = polar(mean_r, i * 360.0 / 16)
        parts.append(cylinder(f"REF_contencao_haste_{i}", 0.65, height, (x, y, z0 + height / 2)))
    if top_cap:
        parts.append(cylinder("REF_contencao_tampa", outer, 1.0, (0.0, 0.0, z0 + height + 0.5), vertices=96))
    return parts


def configure_render(scene: bpy.types.Scene, filepath: Path) -> None:
    # Workbench dá leitura clara das arestas; os materiais ficam no .blend para EEVEE.
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


def assemble_and_save(parts: dict[str, bpy.types.Object], output_dir: Path, render_preview: bool) -> dict:
    rotor_z = datum_b_z()
    sp = P["spider"]
    asm = P["assembly"]
    ui = P["unverified_interfaces"]
    abs_mat = material("ABS cinza", (0.36, 0.38, 0.42, 1.0))
    panel_mat = material("ABS painéis", (0.10, 0.32, 0.70, 1.0))
    metal_mat = material("Alumínio", (0.42, 0.45, 0.5, 1.0), metallic=0.75)
    ref_mat = material("Referência", (0.55, 0.35, 0.08, 1.0))
    guard_mat = material("Contenção PENDENTE", (0.06, 0.35, 0.55, 1.0), metallic=0.1)

    for obj in parts.values():
        obj.hide_render = True
        obj.hide_viewport = True

    base = duplicate(parts["base_tower"], "MONTAGEM_base_torre")
    assign_material(base, abs_mat)
    plate = duplicate(parts["motor_plate"], "MONTAGEM_suporte_motor_ref")
    plate.location.z = plate_top_z() - P["motor_plate"]["thickness"]
    assign_material(plate, metal_mat)
    post = duplicate(parts["magnet_post"], "MONTAGEM_poste_ima")
    post.location.z = plate_top_z()
    assign_material(post, abs_mat)

    spider = duplicate(parts["spider"], "MONTAGEM_aranha")
    spider.location.z = rotor_z
    assign_material(spider, abs_mat)
    lid = duplicate(parts["lid"], "MONTAGEM_tampa")
    lid.location.z = rotor_z + sp["electronics_bay_height"]
    assign_material(lid, abs_mat)

    # A rotação do objeto é aplicada em torno da própria origem ANTES da
    # translação: o vetor de posição também precisa ser rotacionado (spec §8).
    panel_r = asm["panel_radius"]
    for i in range(3):
        panel = duplicate(parts["panel"], f"MONTAGEM_painel_{i + 1}")
        angle = math.radians(i * 120.0)
        panel.rotation_euler[2] = angle
        panel.location = (panel_r * math.cos(angle), panel_r * math.sin(angle), rotor_z + asm["panel_mid_plane_above_datum_b"])
        assign_material(panel, panel_mat)

    # Referências visuais de hardware (não impressas).
    motor = ui["motor"]
    motor_ref = cylinder("MONTAGEM_motor_A2212_ref", motor["body_diameter"] / 2, motor["body_height"], (0.0, 0.0, plate_top_z() + motor["body_height"] / 2))
    assign_material(motor_ref, metal_mat)
    shaft = ui["shaft"]
    datum_a = rotor_z - sp["hub_thickness"]
    smooth = cylinder("MONTAGEM_eixo_liso_ref", shaft["smooth_diameter"] / 2, shaft["smooth_length_above_bell"], (0.0, 0.0, datum_a + shaft["smooth_length_above_bell"] / 2))
    assign_material(smooth, metal_mat)
    thread = cylinder("MONTAGEM_eixo_rosca_M6_ref", 3.0, shaft["thread_length"], (0.0, 0.0, datum_a + shaft["smooth_length_above_bell"] + shaft["thread_length"] / 2))
    assign_material(thread, metal_mat)
    nut = ui["m6_nut"]
    washer_z0 = rotor_z - sp["counterbore_depth"]
    washer = ring("MONTAGEM_arruela_M6_ref", nut["washer_od"] / 2, 3.2, washer_z0, washer_z0 + nut["washer_thickness"])
    assign_material(washer, metal_mat)
    nut_ref = cylinder("MONTAGEM_porca_M6_baixa_ref", nut["across_flats"] / math.sqrt(3.0), nut["height"], (0.0, 0.0, washer_z0 + nut["washer_thickness"] + nut["height"] / 2), vertices=6)
    assign_material(nut_ref, metal_mat)
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
    use_cap_part = cg["cylinder_has_top_cap"] and P["containment_cap"]["enabled"] and "containment_cap" in parts
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

    panel_h = P["panel"]["height"]
    mid = rotor_z + asm["panel_mid_plane_above_datum_b"]
    return {
        "datum_b_z_mm": rotor_z,
        "datum_a_z_mm": datum_a,
        "panel_mid_plane_z_mm": mid,
        "rotor_z_min_mm": mid - panel_h / 2,
        "rotor_z_max_mm": mid + panel_h / 2,
        "plate_top_z_mm": plate_top_z(),
        "magnet_post_top_z_mm": plate_top_z() + magnet_post_height(),
        "hall_air_gap_mm": P["magnet_post"]["air_gap"],
        "index_pulse_note": "Sensor em r=29, azimute 30° do rotor; ímã em r=29, azimute 30° da base: o pulso ocorre quando o braço 1 está alinhado com +x da base.",
        "containment_reference_top_z_mm": guard_top,
        "containment_vertical_margin_mm": round(guard_top - (mid + panel_h / 2), 2),
    }


def compute_report(stats: dict, assembly: dict) -> dict:
    q = P["panel"]
    f = q["fairing"]
    b = q["boss"]
    sp = P["spider"]
    bt = P["base_tower"]
    ncm = P["non_cad_masses_g"]
    cs = sp["cooling_slots"]

    panel_mass_bare = stats["panel_each"]["estimated_mass_g"]
    panel_assembled = panel_mass_bare + ncm["led_strip_per_panel"] + ncm["hardware_per_panel"]
    rotor_cad = stats["spider"]["estimated_mass_g"] + 3.0 * panel_mass_bare + stats["lid"]["estimated_mass_g"]
    rotor_total = (
        rotor_cad
        + 3.0 * (ncm["led_strip_per_panel"] + ncm["hardware_per_panel"])
        + ncm["battery_pack"]
        + ncm["m6_nut_and_washer"]
        + ncm["onboard_electronics_allowance"]
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

    return {
        "panel": {
            "bare_mass_g": panel_mass_bare,
            "assembled_mass_g": round(panel_assembled, 2),
            "assembled_mass_limit_g": q["mass_limit_assembled_g"],
            "datum_d_mm": round(0.0 - stats["panel_each"]["bounds_min_mm"][2], 3),
            "abs_centroid_z_mm": panel_cg_z,
            "assembled_centroid_z_estimate_mm": round(cg_assembled, 2),
            "assembled_centroid_note": "Estimativa com fita (6,2 g) e ~1,2 g de fios descendo pela cavidade até a ponta inferior. Momento parasita na junta = F × deslocamento.",
            "parasitic_moment_n_mm": round(force * abs(cg_assembled), 1),
            "centrifugal_force_n_with_cad_mass": round(force, 1),
            "led_floor_mm": round(q["shell_wall"] - q["led_channel"]["depth"], 3),
            "nut_pocket_wall_mm": round(b["tower_diameter"] / 2 - b["nut_hex_circumradius"], 3),
            "led_channel_start_z_mm": strip_z0,
            "led_strip_top_z_mm": round(strip_z0 + strip_len, 2),
            "panel_top_z_mm": q["height"] / 2,
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
            "cooling_free_area_mm2": round(slot_area, 1),
            "hub_rim_outside_slots_mm": round(sp["hub_diameter"] / 2 - cs["outer_radius"], 2),
            "bay_wall_to_slot_mm": round(cs["inner_radius"] - sp["electronics_bay_od"] / 2, 2),
            "nut_top_above_hub_mm": round(-sp["counterbore_depth"] + P["unverified_interfaces"]["m6_nut"]["washer_thickness"] + P["unverified_interfaces"]["m6_nut"]["height"], 2),
            "battery_floor_z_mm": sp["battery_cradle"]["rail_height"],
            "battery_top_z_mm": sp["battery_cradle"]["rail_height"] + P["unverified_interfaces"]["battery"]["height"],
            "bay_internal_height_mm": sp["electronics_bay_height"],
        },
        "lid": {"mass_g": stats["lid"]["estimated_mass_g"], "mass_limit_g": P["lid"]["mass_limit_g"]},
        "base_tower": {
            "mass_g": stats["base_tower"]["estimated_mass_g"],
            "mass_limit_g": bt.get("mass_limit_g"),
            "mass_note": "peça estática: sem critério de massa (decisão de 02/09/2026); só o rotor tem orçamento",
            "lateral_vent_area_mm2": vent_area,
            "footprint_diameter_mm": bt["footprint_diameter"],
            "footprint_with_brim_mm": bt["footprint_diameter"] + 2 * P["fdm_rules"]["brim_mm"],
        },
        "containment": {
            **containment_geometry(),
            "rotor_dynamic_radius_mm": round(P["operating_point"]["image_cylinder_diameter_mm"] / 2 + P["loads_from_spec"]["tip_deflection_mm"], 2),
            "radial_clearance_mm": round(containment_geometry()["cylinder_inner_radius"] - (P["operating_point"]["image_cylinder_diameter_mm"] / 2 + P["loads_from_spec"]["tip_deflection_mm"]), 2),
            "peripheral_holes": "removidos (spec 5.4 pedia 4 x Ø4; sem faixa livre na pista ao lado da canaleta)" if not P["base_tower"]["peripheral_holes"]["enabled"] else "PCD %.0f" % P["base_tower"]["peripheral_holes"]["pcd"],
        },
        "containment_cap": {
            **cap_geometry(),
            "mass_g": stats["containment_cap"]["estimated_mass_g"] if "containment_cap" in stats else None,
            "rotor_top_z_mm": P["assembly"]["panel_mid_plane_above_datum_b"] + q["height"] / 2 + 0.0,
        },
        "rotor": {
            "cad_mass_g": round(rotor_cad, 2),
            "total_mass_estimate_g": round(rotor_total, 2),
            "limit_g": 280.0,
            "components": {
                "spider": stats["spider"]["estimated_mass_g"],
                "panels_bare_x3": round(3 * panel_mass_bare, 2),
                "lid": stats["lid"]["estimated_mass_g"],
                "strips_x3": round(3 * ncm["led_strip_per_panel"], 2),
                "hardware_x3": round(3 * ncm["hardware_per_panel"], 2),
                "battery": ncm["battery_pack"],
                "nut_washer": ncm["m6_nut_and_washer"],
                "electronics_allowance": ncm["onboard_electronics_allowance"],
            },
        },
        "assembly": assembly,
    }


def acceptance(report: dict, stats: dict) -> list[dict]:
    q = P["panel"]
    checks = []

    def add(name, value, criterion, ok, note=""):
        checks.append({"criterio": name, "valor": value, "requisito": criterion, "passa": bool(ok), "nota": note})

    add("Raio do plano médio do painel", P["assembly"]["panel_radius"], "100 ±0,1 mm", abs(P["assembly"]["panel_radius"] - 100.0) <= 0.1, "por construção na montagem; face interna em r=96 e externa em r=104")
    add("Datum D", report["panel"]["datum_d_mm"], "104 ±0,2 mm", abs(report["panel"]["datum_d_mm"] - 104.0) <= 0.2)
    add("Δh entre painéis", 0.0, "≤ ±0,5 mm", True, "os três painéis são o mesmo STL")
    add("Piso sob o canal do LED", report["panel"]["led_floor_mm"], "≥ 0,6 mm", report["panel"]["led_floor_mm"] >= 0.6)
    add("Parede ao redor do bolso de porca", report["panel"]["nut_pocket_wall_mm"], "≥ 1,5 mm", report["panel"]["nut_pocket_wall_mm"] >= 1.5)
    min_wall = min(
        q["fairing"]["wall"],
        report["panel"]["led_floor_mm"],
        P["spider"]["hub_diameter"] / 2 - P["spider"]["cooling_slots"]["outer_radius"],
        P["lid"]["skin_thickness"],
        P["panel"]["ribs"]["thickness"],
    )
    add("Menor parede estrutural do modelo", round(min_wall, 2), "≥ 0,8 mm", min_wall >= 0.8, "mínimo entre piso do canal, casca da carenagem, borda do disco fora dos rasgos, pele da tampa e nervuras (1,0 mm, conforme spec §5.1)")
    add("Área livre de ventilação do cubo", report["spider"]["cooling_free_area_mm2"], "≥ 300 mm², sem abrir a baia", report["spider"]["cooling_free_area_mm2"] >= 300.0, "3 rasgos de 60° fora da baia (r 35,5–39)")
    add("Área livre de ventilação da base", report["base_tower"]["lateral_vent_area_mm2"], "≥ 600 mm², na lateral", report["base_tower"]["lateral_vent_area_mm2"] >= 600.0, "8 janelas na parede lateral da baia")
    a_cd_hi = report["boss_drag"]["a_cd_range_mm2"][1]
    add("A × Cd do boss carenado", report["boss_drag"]["a_cd_range_mm2"], "≤ 350 mm²", a_cd_hi <= 350.0, "estimativa por razão de finura, não CFD")
    add("Massa por painel montado", report["panel"]["assembled_mass_g"], "≤ 45 g", report["panel"]["assembled_mass_g"] <= 45.0)
    add("Massa do rotor completo", report["rotor"]["total_mass_estimate_g"], "≤ 280 g", report["rotor"]["total_mass_estimate_g"] <= 280.0, "inclui bateria, fitas, ferragens e folga de eletrônica")
    add("Massa da aranha", report["spider"]["mass_g"], "≤ 55 g (alvo)", report["spider"]["mass_g"] <= 55.0)
    add("Massa da tampa", report["lid"]["mass_g"], "≤ 8 g (alvo)", report["lid"]["mass_g"] <= 8.0)
    add("Perpendicularidade torre/base", 0.0, "≤ 1°", True, "no CAD é zero; verificar na peça impressa")
    add("Planeza da base", 0.0, "±2 mm", True, "no CAD é zero; verificar na peça impressa")
    nm = sum(s["non_manifold_edges"] for s in stats.values())
    add("Malhas (arestas não-manifold no gerador)", nm, "0", nm == 0, "validação independente em reports/stl_validation.json")
    add("Base + brim cabe na mesa", report["base_tower"]["footprint_with_brim_mm"], "≤ 300 mm", report["base_tower"]["footprint_with_brim_mm"] <= 300.0)
    bay_ok = report["spider"]["battery_top_z_mm"] <= report["spider"]["bay_internal_height_mm"]
    add("Bateria cabe na baia sobre a porca", report["spider"]["battery_top_z_mm"], f"≤ {report['spider']['bay_internal_height_mm']} mm", bay_ok, "porca baixa no rebaixo, topo em Z=%.1f" % report["spider"]["nut_top_above_hub_mm"])
    strip_ok = report["panel"]["led_strip_top_z_mm"] <= report["panel"]["panel_top_z_mm"]
    add("Fita de 201,4 mm cabe no canal", report["panel"]["led_strip_top_z_mm"], "≤ 104 mm (topo do painel)", strip_ok, "batente em Z=%.1f por causa do bolso de fios" % report["panel"]["led_channel_start_z_mm"])
    cg = report["containment"]
    if cg["enabled"]:
        add("Canaleta de assento dentro da pista", [cg["inner_lip_mm"], cg["outer_lip_mm"]], "lábios ≥ 1,2 mm", cg["fits_track"], "canaleta r %.1f–%.1f, largura %.1f, profundidade %.0f" % (cg["groove_inner_radius_mm"], cg["groove_outer_radius_mm"], cg["groove_width_mm"], cg["groove_depth_mm"]))
        add("Cilindro cabe na canaleta", [cg["clearance_inner_mm"], cg["clearance_outer_mm"]], "folga ≥ 0 nos dois lados", cg["cylinder_fits_groove"], "Ø int %.0f, parede %.0f, contra canaleta de %.1f" % (cg["cylinder_inner_diameter_mm"], cg["cylinder_wall_mm"], cg["groove_width_mm"]))
        add("Cotas do cilindro confirmadas", cg["cylinder_source"] or "não", "verified = true", cg["measured"], "conferir Ø interno e borda na peça recebida")
        add("Folga radial rotor → cilindro", cg["radial_clearance_mm"], "≥ 10 mm após deflexão", cg["radial_clearance_mm"] >= 10.0, "raio dinâmico %.1f contra Ø int %.0f" % (cg["rotor_dynamic_radius_mm"], cg["cylinder_inner_diameter_mm"]))
        margin = report["assembly"]["containment_vertical_margin_mm"]
        add("Folga vertical topo do rotor → topo do cilindro", margin, "≥ 10 mm", margin >= 10.0, "cilindro de %.0f mm apoiado em Z=%.0f (piso da canaleta); a placa da tampa fica acima da borda e não desconta" % (cg["cylinder_height_mm"], cg["rest_z_mm"]))
    cap = report["containment_cap"]
    if cap["enabled"]:
        qc = P["containment_cap"]
        add("Tampa: aberturas menores que a seção do painel", cap["max_opening_mm"], "≤ %.0f mm (círculo mínimo da seção 30 × 8 = Ø31,05)" % qc["max_opening_diameter"], cap["max_opening_mm"] <= qc["max_opening_diameter"], "%d furos" % len(cap["holes"]))
        add("Tampa: área livre de ventilação", cap["free_area_mm2"], "≥ %.0f mm² (único caminho de ar com a base na mesa)" % qc["min_free_area_mm2"], cap["free_area_mm2"] >= qc["min_free_area_mm2"])
        add("Tampa + brim cabe na mesa", cap["footprint_with_brim_mm"], "≤ 300 mm", cap["footprint_with_brim_mm"] <= 300.0)
        add("Tampa: furos de ventilação fora da trajetória dos painéis", cap["vent_holes_outer_reach_mm"], "< 96 mm (face interna do painel)", cap["vent_holes_outer_reach_mm"] < 96.0, "painel solto voa para fora, nunca para dentro")
    return checks


def write_acceptance_md(checks: list[dict], path: Path) -> None:
    lines = [
        "# Critérios de aceitação — Hologram Orbiter v3.0",
        "",
        "Verificação automática a partir do modelo (spec §9). Gerado por `CAD/generate.py`.",
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
    report_dir = PROJECT_ROOT / "reports"
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
    base_tower = build_base_tower()
    print("[5/9] Modelando poste do ímã, tampa do cilindro, cupons e chapa de referência...")
    magnet_post = build_magnet_post()
    containment_cap = build_containment_cap() if P["containment_cap"]["enabled"] else None
    joint_coupon = build_joint_coupon()
    led_coupon = build_led_coupon()
    motor_plate = build_motor_plate_reference()

    parts = {
        "spider": spider,
        "panel": panel,
        "lid": lid,
        "base_tower": base_tower,
        "magnet_post": magnet_post,
        "joint_coupon": joint_coupon,
        "led_coupon": led_coupon,
        "motor_plate": motor_plate,
    }
    if containment_cap is not None:
        parts["containment_cap"] = containment_cap
    for obj in parts.values():
        cleanup_mesh(obj)

    print("[6/9] Exportando STL...")
    pp = P["panel"]["print"]
    s = pp["batch_spacing_y"]
    export_stl(spider, stl_dir / "01_aranha_ABS.stl")
    export_stl(panel, stl_dir / "02_painel_LED_ABS_1x.stl", rotate_y_deg=pp["rotate_y_deg"])
    export_stl(panel, stl_dir / "02_painel_LED_ABS_3x_mesma_mesa.stl", rotate_y_deg=pp["rotate_y_deg"], copies=[(0.0, -s, 0.0), (0.0, 0.0, 0.0), (0.0, s, 0.0)])
    export_stl(lid, stl_dir / "03_tampa_baia_ABS.stl")
    export_stl(base_tower, stl_dir / "04_05_base_torre_ABS_integradas.stl")
    export_stl(magnet_post, stl_dir / "06_poste_ima_ABS.stl")
    if containment_cap is not None:
        # Face plana na mesa, anel de assento e canaleta para cima: sem suporte.
        export_stl(containment_cap, stl_dir / "07_tampa_contencao_ABS.stl", rotate_x_deg=180.0)
    export_stl(joint_coupon, stl_dir / "C01_cupom_junta.stl")
    export_stl(led_coupon, stl_dir / "C02_cupom_canal_LED.stl")
    export_stl(motor_plate, stl_dir / "R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl")

    print("[7/9] Calculando relatório geométrico...")
    abs_density = P["material"]["abs_density_g_cm3"]
    al_density = P["material"]["aluminium_density_g_cm3"]
    stats = {
        "spider": object_stats(spider, abs_density),
        "panel_each": object_stats(panel, abs_density),
        "lid": object_stats(lid, abs_density),
        "base_tower": object_stats(base_tower, abs_density),
        "magnet_post": object_stats(magnet_post, abs_density),
        **({"containment_cap": object_stats(containment_cap, abs_density)} if containment_cap is not None else {}),
        "joint_coupon": object_stats(joint_coupon, abs_density),
        "led_coupon": object_stats(led_coupon, abs_density),
        "motor_plate_reference_aluminium": object_stats(motor_plate, al_density),
    }

    print("[8/9] Salvando BLEND e renderizando prévia...")
    assembly = assemble_and_save(parts, output_dir, render_preview=not ARGS.no_render)

    print("[9/9] Escrevendo relatórios...")
    derived = compute_report(stats, assembly)
    checks = acceptance(derived, stats)
    report = {
        "project": P["project"],
        "status": P["status"],
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
    for c in checks:
        print(f"  {'OK   ' if c['passa'] else 'FALHA'} {c['criterio']}: {c['valor']} ({c['requisito']})")
    print(f"Concluído: {output_dir}")
    sys.stdout.flush()
    sys.stderr.flush()
    if bpy.app.background:
        os._exit(0)


if __name__ == "__main__":
    main()
