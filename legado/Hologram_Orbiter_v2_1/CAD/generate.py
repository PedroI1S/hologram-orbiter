#!/usr/bin/env python3
"""Gerador CAD paramétrico do Hologram Orbiter v2.1.

Execute dentro do Blender:
    blender -b --python CAD/generate.py -- --output-dir exports

Todas as dimensões geométricas são expressas em milímetros. O STL não guarda
unidade; os arquivos exportados devem ser interpretados como milímetros.
"""

from __future__ import annotations

import argparse
import bmesh
import json
import math
import os
import sys
from pathlib import Path

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


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
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
    bmesh.ops.triangulate(
        bm,
        faces=list(bm.faces),
        quad_method="BEAUTY",
        ngon_method="BEAUTY",
    )
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


def mesh_prism_z(
    name: str, points_xy: list[tuple[float, float]], z0: float, z1: float
) -> bpy.types.Object:
    count = len(points_xy)
    vertices = [(x, y, z0) for x, y in points_xy] + [(x, y, z1) for x, y in points_xy]
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


def mesh_prism_x(
    name: str, points_yz: list[tuple[float, float]], x0: float, x1: float
) -> bpy.types.Object:
    count = len(points_yz)
    vertices = [(x0, y, z) for y, z in points_yz] + [(x1, y, z) for y, z in points_yz]
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


def mesh_prism_y(
    name: str, points_xz: list[tuple[float, float]], y0: float, y1: float
) -> bpy.types.Object:
    count = len(points_xz)
    vertices = [(x, y0, z) for x, z in points_xz] + [(x, y1, z) for x, z in points_xz]
    faces = [list(range(count)), list(reversed(range(count, count * 2)))]
    for i in range(count):
        j = (i + 1) % count
        faces.append([i, i + count, j + count, j])
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    recalc_normals(obj)
    return obj


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


def boolean(
    target: bpy.types.Object,
    operand: bpy.types.Object,
    operation: str,
    label: str,
) -> bpy.types.Object:
    activate(target)
    modifier = target.modifiers.new(name=label, type="BOOLEAN")
    modifier.operation = operation
    modifier.solver = BOOL_SOLVER
    modifier.object = operand
    try:
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    except Exception as exc:
        raise RuntimeError(
            f"Falha booleana {operation} em {target.name} usando {operand.name}: {exc}"
        ) from exc
    delete_object(operand)
    # Não recalcular as normais após CSG: em corpos ocos isso inverteria a
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


def subtract_all(
    target: bpy.types.Object, cutters: list[bpy.types.Object], label: str
) -> bpy.types.Object:
    if not cutters:
        return target
    joined = join_cutters(cutters, f"{label}_cutters")
    return boolean(target, joined, "DIFFERENCE", label)


def rotate_about_z(obj: bpy.types.Object, angle_deg: float) -> bpy.types.Object:
    obj.rotation_euler[2] += math.radians(angle_deg)
    return apply_transform(obj)


def ring(
    name: str,
    outer_radius: float,
    inner_radius: float,
    z0: float,
    z1: float,
) -> bpy.types.Object:
    outer = cylinder(f"{name}_outer", outer_radius, z1 - z0, (0.0, 0.0, (z0 + z1) / 2))
    inner = cylinder(
        f"{name}_inner_cut", inner_radius, z1 - z0 + 0.2, (0.0, 0.0, (z0 + z1) / 2)
    )
    return boolean(outer, inner, "DIFFERENCE", f"{name}_hollow")


def build_panel() -> bpy.types.Object:
    q = P["panel"]
    height = q["height"]
    half_h = height / 2.0

    # Perfil: bordo de ataque R4, faces radiais planas e fuga afilada a 2 mm.
    outer = [
        (-1.0, -15.0),
        (1.0, -15.0),
        (4.0, -5.0),
        (4.0, 11.0),
        (3.696, 12.531),
        (2.828, 13.828),
        (1.531, 14.696),
        (0.0, 15.0),
        (-1.531, 14.696),
        (-2.828, 13.828),
        (-3.696, 12.531),
        (-4.0, 11.0),
        (-4.0, -5.0),
    ]
    inner = [
        (0.0, -11.0),
        (2.0, -5.0),
        (2.0, 11.0),
        (1.848, 11.765),
        (1.414, 12.414),
        (0.765, 12.848),
        (0.0, 13.0),
        (-0.765, 12.848),
        (-1.414, 12.414),
        (-1.848, 11.765),
        (-2.0, 11.0),
        (-2.0, -5.0),
    ]

    shell = mesh_prism_z("panel_shell_outer", outer, -half_h, half_h)
    cavity = mesh_prism_z("panel_shell_cavity", inner, -half_h + 2.0, half_h - 2.0)
    shell = boolean(shell, cavity, "DIFFERENCE", "hollow_panel")

    # Diafragmas internos atravessam a cavidade e se sobrepõem 0,2 mm à parede.
    rib_points = [(x * 1.08, y * 1.015) for x, y in inner]
    ribs = [
        mesh_prism_z(
            f"panel_rib_{index}",
            rib_points,
            z - q["rib_thickness"] / 2,
            z + q["rib_thickness"] / 2,
        )
        for index, z in enumerate(q["rib_z_positions"])
    ]

    # Sleeve leve do socket e torres para os dois parafusos M3.
    sleeve = cube("boss_socket_sleeve", (24.0, 15.2, 10.2), (-14.0, 0.0, 0.0))
    screw_x = [-20.0, -10.0]
    towers = [
        cylinder(f"boss_tower_{index}", 4.0, 36.0, (x, 0.0, 0.0))
        for index, x in enumerate(screw_x)
    ]
    lateral_transition = mesh_prism_z(
        "boss_lateral_transition",
        [(-13.0, -7.6), (-2.0, -14.0), (-2.0, 14.0), (-13.0, 7.6)],
        -4.1,
        4.1,
    )
    top_gusset = mesh_prism_y(
        "boss_top_gusset",
        [(-15.0, 4.8), (-9.0, 18.0), (-3.0, 18.0), (-2.0, 4.8)],
        -4.0,
        4.0,
    )
    bottom_gusset = mesh_prism_y(
        "boss_bottom_gusset",
        [(-15.0, -4.8), (-9.0, -18.0), (-3.0, -18.0), (-2.0, -4.8)],
        -4.0,
        4.0,
    )

    panel = union_all(
        [shell, *ribs, sleeve, *towers, lateral_transition, top_gusset, bottom_gusset],
        "painel_led",
    )

    channel_x0 = 4.0 - q["led_channel_depth"]
    channel_length = height - q["led_channel_bottom_stop"] + 0.2
    channel_z0 = -half_h + q["led_channel_bottom_stop"]
    channel = cube(
        "led_channel_cut",
        (q["led_channel_depth"] + 0.5, q["led_channel_width"], channel_length),
        (
            (channel_x0 + 4.5) / 2.0,
            0.0,
            channel_z0 + channel_length / 2.0,
        ),
    )
    socket_x0 = -26.2
    socket_x1 = -4.0 + P["quality"]["joint_bottom_clearance"]
    socket = cube(
        "socket_cut",
        (socket_x1 - socket_x0, q["socket_width"], q["socket_height"]),
        ((socket_x0 + socket_x1) / 2.0, 0.0, 0.0),
    )
    holes = [
        cylinder(f"panel_screw_hole_{i}", q["screw_hole_diameter"] / 2, 38.4, (x, 0.0, 0.0))
        for i, x in enumerate(screw_x)
    ]
    nuts = [
        cylinder(
            f"panel_nut_pocket_{i}",
            q["nut_hex_circumradius"],
            q["nut_pocket_depth"] + 0.2,
            (x, 0.0, -18.0 + q["nut_pocket_depth"] / 2.0 - 0.05),
            vertices=6,
            rotation_z_deg=30.0,
        )
        for i, x in enumerate(screw_x)
    ]
    panel = subtract_all(panel, [channel, socket, *holes, *nuts], "panel_features")
    panel.name = "02_painel_led"
    return panel


def build_arm(index: int) -> bpy.types.Object:
    q = P["spider"]
    airfoil_yz = [
        (-7.5, 3.0),
        (-4.5, 1.0),
        (2.5, 0.0),
        (4.6, 0.5),
        (6.3, 1.7),
        (7.5, 3.0),
        (6.3, 4.3),
        (4.6, 5.5),
        (2.5, 6.0),
        (-4.5, 5.0),
    ]
    beam = mesh_prism_x(f"arm_{index}_airfoil", airfoil_yz, 38.0, q["spar_shoulder_radius"])
    tenon = cube(
        f"arm_{index}_tenon",
        (q["spar_tip_radius"] - q["spar_shoulder_radius"] + 0.2, q["tenon_width"], q["tenon_height"]),
        ((q["spar_tip_radius"] + q["spar_shoulder_radius"] - 0.2) / 2, 0.0, 3.0),
    )
    root = mesh_prism_z(
        f"arm_{index}_root_blend",
        [(34.5, -13.0), (41.0, -11.5), (51.0, -7.5), (51.0, 7.5), (41.0, 11.5), (34.5, 13.0)],
        -0.1,
        6.0,
    )
    arm = union_all([beam, tenon, root], f"arm_{index}")
    return rotate_about_z(arm, index * 120.0)


def build_spider() -> bpy.types.Object:
    q = P["spider"]
    motor = P["unverified_interfaces"]["motor_bell_mount"]
    hub = cylinder("hub_disk", q["hub_diameter"] / 2, q["hub_thickness"], (0.0, 0.0, -3.0))

    bay = ring(
        "electronics_bay_wall",
        q["electronics_bay_od"] / 2,
        q["electronics_bay_id"] / 2,
        -0.1,
        q["electronics_bay_height"],
    )
    lid_posts = [
        cylinder(f"lid_post_{i}", 4.0, q["electronics_bay_height"] + 0.1, (x, 0.0, q["electronics_bay_height"] / 2 - 0.05))
        for i, x in enumerate((-q["lid_screw_spacing"] / 2, q["lid_screw_spacing"] / 2))
    ]

    impeller_blades = []
    blade_length = q["impeller_outer_radius"] - q["impeller_inner_radius"]
    blade_center = (q["impeller_outer_radius"] + q["impeller_inner_radius"]) / 2
    for i in range(q["impeller_blade_count"]):
        impeller_blades.append(
            cube(
                f"impeller_blade_{i}",
                (blade_length + 0.2, q["impeller_blade_thickness"], q["impeller_blade_height"]),
                (blade_center, 0.0, -q["hub_thickness"] - q["impeller_blade_height"] / 2 + 0.05),
                rotation_z_deg=i * 360.0 / q["impeller_blade_count"],
            )
        )

    arms = [build_arm(i) for i in range(3)]
    spider = union_all([hub, bay, *lid_posts, *impeller_blades, *arms], "aranha")

    cutters: list[bpy.types.Object] = []
    cutters.append(
        cylinder(
            "motor_center_clearance",
            motor["center_clearance_diameter"] / 2,
            14.0,
            (0.0, 0.0, -2.0),
        )
    )
    for i in range(motor["hole_count"]):
        angle = math.radians(i * 360.0 / motor["hole_count"])
        radius = motor["pcd"] / 2
        cutters.append(
            cylinder(
                f"motor_bell_hole_{i}",
                motor["hole_diameter"] / 2,
                14.0,
                (radius * math.cos(angle), radius * math.sin(angle), -2.0),
            )
        )
    for i in range(q["cooling_hole_count"]):
        # 15° evita a interseção com a furação provisória PCD 19 do motor.
        angle = math.radians(15.0 + i * 360.0 / q["cooling_hole_count"])
        radius = q["cooling_hole_pcd"] / 2
        cutters.append(
            cylinder(
                f"cooling_hole_{i}",
                q["cooling_hole_diameter"] / 2,
                14.0,
                (radius * math.cos(angle), radius * math.sin(angle), -2.0),
            )
        )

    # Alívios inferiores deixam pele superior de 2 mm no disco.
    for i in range(6):
        angle = 30.0 + i * 60.0
        rad = math.radians(angle)
        pocket = cube(
            f"hub_lightening_pocket_{i}",
            (14.0, 8.0, 4.2),
            (29.0 * math.cos(rad), 29.0 * math.sin(rad), -4.0),
            rotation_z_deg=angle,
        )
        cutters.append(pocket)

    for arm_i in range(3):
        angle = math.radians(arm_i * 120.0)
        for hole_i, radius in enumerate(q["screw_radii"]):
            cutters.append(
                cylinder(
                    f"arm_screw_{arm_i}_{hole_i}",
                    q["screw_hole_diameter"] / 2,
                    9.0,
                    (radius * math.cos(angle), radius * math.sin(angle), 3.0),
                )
            )
        trim = cube(
            f"trim_pocket_{arm_i}",
            (12.0, 6.0, 1.3),
            (97.0 * math.cos(angle), 97.0 * math.sin(angle), 5.55),
            rotation_z_deg=arm_i * 120.0,
        )
        cutters.append(trim)

    for i, x in enumerate((-q["lid_screw_spacing"] / 2, q["lid_screw_spacing"] / 2)):
        cutters.append(cylinder(f"lid_post_hole_{i}", 1.4, 22.0, (x, 0.0, 10.0)))

    spider = subtract_all(spider, cutters, "spider_holes_and_pockets")
    spider.name = "01_aranha"
    return spider


def build_lid() -> bpy.types.Object:
    q = P["lid"]
    spider = P["spider"]
    skin = cylinder("lid_skin", q["diameter"] / 2, q["skin_thickness"], (0.0, 0.0, q["skin_thickness"] / 2))
    rim = ring(
        "lid_rim",
        q["diameter"] / 2,
        q["diameter"] / 2 - q["rim_wall"],
        q["skin_thickness"] - 0.1,
        q["height"],
    )
    lid = union_all([skin, rim], "tampa")
    cutters = [
        cylinder(
            f"lid_access_hole_{i}",
            q["screw_hole_diameter"] / 2,
            q["height"] + 0.4,
            (x, 0.0, q["height"] / 2),
        )
        for i, x in enumerate((-spider["lid_screw_spacing"] / 2, spider["lid_screw_spacing"] / 2))
    ]
    lid = subtract_all(lid, cutters, "lid_access_holes")
    lid.name = "03_tampa_baia"
    return lid


def build_base_tower() -> bpy.types.Object:
    q = P["base_tower"]
    central_outer = cylinder("central_bay_outer", q["central_bay_od"] / 2, q["central_bay_height"], (0.0, 0.0, q["central_bay_height"] / 2))
    central_inner = cylinder(
        "central_bay_inner",
        q["central_bay_od"] / 2 - q["central_bay_wall"],
        q["central_bay_height"] - q["central_floor_thickness"] + 0.2,
        (0.0, 0.0, (q["central_bay_height"] + q["central_floor_thickness"]) / 2 + 0.05),
    )
    central_bay = boolean(central_outer, central_inner, "DIFFERENCE", "central_bay_hollow")

    outer_ring = ring(
        "base_outer_ring",
        q["footprint_diameter"] / 2,
        q["outer_ring_inner_diameter"] / 2,
        0.0,
        q["outer_ring_height"],
    )
    rib_start = q["central_bay_od"] / 2 - 1.0
    rib_end = q["outer_ring_inner_diameter"] / 2 + 1.0
    rib_length = rib_end - rib_start
    rib_center = (rib_start + rib_end) / 2
    ribs = [
        cube(
            f"base_radial_rib_{i}",
            (rib_length, q["radial_rib_width"], q["radial_rib_height"] + 0.2),
            (rib_center, 0.0, q["radial_rib_height"] / 2),
            rotation_z_deg=i * 360.0 / q["radial_rib_count"],
        )
        for i in range(q["radial_rib_count"])
    ]

    floor_z = q["central_floor_thickness"]
    tower_top = floor_z + q["tower_total_height_from_floor"]
    tower_outer = cylinder(
        "tower_outer",
        q["tower_od"] / 2,
        q["tower_total_height_from_floor"] + 0.1,
        (0.0, 0.0, (floor_z + tower_top) / 2 - 0.05),
    )
    tower_inner = cylinder(
        "tower_inner",
        q["tower_od"] / 2 - q["tower_wall"],
        q["tower_total_height_from_floor"] + 0.4,
        (0.0, 0.0, (floor_z + tower_top) / 2),
    )
    tower = boolean(tower_outer, tower_inner, "DIFFERENCE", "tower_hollow")
    lower_flange = cylinder(
        "tower_lower_flange",
        q["flange_diameter"] / 2,
        q["flange_thickness"],
        (0.0, 0.0, floor_z + q["flange_thickness"] / 2),
    )
    upper_flange = cylinder(
        "tower_upper_flange",
        q["flange_diameter"] / 2,
        q["flange_thickness"],
        (0.0, 0.0, tower_top - q["flange_thickness"] / 2),
    )
    base = union_all(
        [central_bay, outer_ring, *ribs, tower, lower_flange, upper_flange],
        "base_torre",
    )
    # As nervuras cruzam as peças adjacentes 0,1 mm em Z para evitar faces
    # coplanares internas. Este corte devolve uma única face de apoio plana.
    bottom_trim = cube("base_bottom_trim", (340.0, 340.0, 20.0), (0.0, 0.0, -9.9999))
    base = boolean(base, bottom_trim, "DIFFERENCE", "base_flatten_bottom")

    cutters: list[bpy.types.Object] = []
    cutters.append(
        cylinder(
            "tower_wire_bore",
            q["tower_od"] / 2 - q["tower_wall"],
            tower_top + 2.0,
            (0.0, 0.0, tower_top / 2),
        )
    )
    # Janela lateral para que a fiação da baia alcance o interior do tubo.
    cutters.append(cube("tower_wire_window", (20.0, 12.0, 12.0), (10.0, 0.0, 20.0)))

    flange_radius = q["flange_hole_pcd"] / 2
    for i in range(4):
        angle = math.radians(45.0 + i * 90.0)
        cutters.append(
            cylinder(
                f"flange_hole_{i}",
                q["flange_hole_diameter"] / 2,
                tower_top + 2.0,
                (flange_radius * math.cos(angle), flange_radius * math.sin(angle), tower_top / 2),
            )
        )

    peripheral_radius = q["peripheral_hole_pcd"] / 2
    for i in range(4):
        angle = math.radians(i * 90.0)
        cutters.append(
            cylinder(
                f"peripheral_hole_{i}",
                q["peripheral_hole_diameter"] / 2,
                q["outer_ring_height"] + 0.4,
                (peripheral_radius * math.cos(angle), peripheral_radius * math.sin(angle), q["outer_ring_height"] / 2),
            )
        )

    vent_radius = q["vent_hole_pcd"] / 2
    for i in range(4):
        angle = math.radians(45.0 + i * 90.0)
        cutters.append(
            cylinder(
                f"base_vent_{i}",
                q["vent_hole_diameter"] / 2,
                q["central_floor_thickness"] + 0.4,
                (vent_radius * math.cos(angle), vent_radius * math.sin(angle), q["central_floor_thickness"] / 2),
            )
        )

    base = subtract_all(base, cutters, "base_tower_openings")
    base.name = "04_05_base_torre_integradas"
    return base


def build_damper() -> bpy.types.Object:
    q = P["damper"]
    outer = cylinder("damper_outer", q["diameter"] / 2, q["height"], (0.0, 0.0, q["height"] / 2))
    hole = cylinder("damper_hole", q["hole_diameter"] / 2, q["height"] + 0.4, (0.0, 0.0, q["height"] / 2))
    result = boolean(outer, hole, "DIFFERENCE", "damper_bore")
    result.name = "07_coxim_tpu_95a"
    return result


def build_containment_ring() -> bpy.types.Object:
    q = P["containment_ring"]
    result = ring(
        "containment_ring",
        q["outer_diameter"] / 2,
        q["inner_diameter"] / 2,
        0.0,
        q["height"],
    )
    result.name = "08_anel_contencao_tpu_referencia"
    return result


def build_joint_coupon() -> bpy.types.Object:
    panel = P["panel"]
    spider = P["spider"]
    block = cube("joint_coupon_block", (34.0, 24.0, 12.0), (0.0, 0.0, 6.0))
    socket_internal_end = 17.0 - panel["socket_depth"] - P["quality"]["joint_bottom_clearance"]
    socket_open_end = 17.2
    socket = cube(
        "joint_coupon_socket",
        (socket_open_end - socket_internal_end, panel["socket_width"], panel["socket_height"]),
        ((socket_open_end + socket_internal_end) / 2.0, 0.0, 6.0),
    )
    socket_coupon = boolean(block, socket, "DIFFERENCE", "coupon_socket")
    tenon = cube(
        "joint_coupon_tenon",
        (panel["socket_depth"], spider["tenon_width"], spider["tenon_height"]),
        (30.0, 0.0, 3.0),
    )
    # Ponte fina destacável mantém as duas metades como um único STL de calibração.
    bridge = cube("coupon_breakaway_bridge", (3.2, 3.0, 0.6), (17.6, 0.0, 0.3))
    coupon = union_all([socket_coupon, tenon, bridge], "cupom_junta")
    coupon.name = "C01_cupom_junta_11x6"
    return coupon


def build_led_coupon() -> bpy.types.Object:
    panel = P["panel"]
    block = cube("led_coupon_block", (8.0, 30.0, 30.0), (0.0, 0.0, 15.0))
    channel = cube(
        "led_coupon_channel",
        (panel["led_channel_depth"] + 0.5, panel["led_channel_width"], 24.0),
        (4.0 - panel["led_channel_depth"] / 2 + 0.2, 0.0, 18.0),
    )
    coupon = boolean(block, channel, "DIFFERENCE", "coupon_led_channel")
    coupon.name = "C02_cupom_canal_led_13x1p8"
    return coupon


def build_motor_plate_reference() -> bpy.types.Object:
    q = P["reference_parts"]
    motor = P["unverified_interfaces"]["motor_base_mount"]
    plate = cube(
        "motor_plate_reference",
        (q["motor_plate_width"], q["motor_plate_depth"], q["motor_plate_thickness"]),
        (0.0, 0.0, q["motor_plate_thickness"] / 2),
    )
    cutters = []
    pcd_radius = motor["pcd"] / 2
    for i in range(motor["hole_count"]):
        angle = math.radians(i * 360.0 / motor["hole_count"])
        cutters.append(
            cylinder(
                f"motor_plate_center_hole_{i}",
                motor["hole_diameter"] / 2,
                q["motor_plate_thickness"] + 0.4,
                (pcd_radius * math.cos(angle), pcd_radius * math.sin(angle), q["motor_plate_thickness"] / 2),
            )
        )
    flange_radius = P["base_tower"]["flange_hole_pcd"] / 2
    for i in range(4):
        angle = math.radians(45.0 + i * 90.0)
        cutters.append(
            cylinder(
                f"plate_cushion_hole_{i}",
                2.0,
                q["motor_plate_thickness"] + 0.4,
                (flange_radius * math.cos(angle), flange_radius * math.sin(angle), q["motor_plate_thickness"] / 2),
            )
        )
    plate = subtract_all(plate, cutters, "motor_plate_holes")
    plate.name = "R01_suporte_motor_aluminio_NAO_IMPRIMIR"
    return plate


def world_bounds(obj: bpy.types.Object) -> tuple[Vector, Vector]:
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (
        Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords))),
        Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords))),
    )


def object_stats(obj: bpy.types.Object, density_g_cm3: float) -> dict:
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    volume = abs(bm.calc_volume(signed=True))
    non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
    triangles = sum(max(1, len(face.verts) - 2) for face in bm.faces)
    bm.free()
    low, high = world_bounds(obj)
    dims = high - low
    return {
        "dimensions_mm": [round(dims.x, 3), round(dims.y, 3), round(dims.z, 3)],
        "volume_cm3": round(volume / 1000.0, 3),
        "estimated_mass_g": round(volume / 1000.0 * density_g_cm3, 2),
        "triangles": int(triangles),
        "non_manifold_edges": int(non_manifold),
    }


def export_stl(
    source: bpy.types.Object,
    filepath: Path,
    rotate_y_deg: float = 0.0,
    copies: list[tuple[float, float, float]] | None = None,
) -> list[bpy.types.Object]:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    clones = []
    placements = copies or [(0.0, 0.0, 0.0)]
    for index, placement in enumerate(placements):
        clone = duplicate(source, f"EXPORT_{source.name}_{index}")
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
    return clones


def material(name: str, color: tuple[float, float, float, float], metallic: float = 0.0) -> bpy.types.Material:
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
    return mat


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def aim_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_guard_reference(z0: float, height: float) -> list[bpy.types.Object]:
    q = P["reference_parts"]
    inner = q["acrylic_guard_inner_diameter"] / 2
    outer = inner + q["acrylic_guard_wall"]
    parts = [
        ring("guard_bottom_reference", outer, inner, z0, z0 + 1.0),
        ring("guard_top_reference", outer, inner, z0 + height - 1.0, z0 + height),
    ]
    mean_r = (inner + outer) / 2
    for i in range(16):
        angle = math.radians(i * 360.0 / 16)
        parts.append(
            cylinder(
                f"guard_stave_{i}",
                0.65,
                height,
                (mean_r * math.cos(angle), mean_r * math.sin(angle), z0 + height / 2),
            )
        )
    return parts


def configure_render(scene: bpy.types.Scene, filepath: Path) -> None:
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(filepath)
    scene.render.film_transparent = False
    scene.view_settings.exposure = 1.2
    scene.world.color = (0.11, 0.12, 0.15)

    bpy.ops.object.light_add(type="AREA", location=(250.0, -250.0, 420.0))
    key = bpy.context.object
    key.data.energy = 2800.0
    key.data.shape = "DISK"
    key.data.size = 240.0
    bpy.ops.object.light_add(type="AREA", location=(-250.0, -80.0, 280.0))
    fill = bpy.context.object
    fill.data.energy = 1800.0
    fill.data.size = 200.0

    bpy.ops.object.camera_add(location=(520.0, -650.0, 390.0))
    camera = bpy.context.object
    camera.data.lens = 48.0
    aim_camera(camera, (0.0, 0.0, 145.0))
    scene.camera = camera

    ground = cylinder("preview_ground", 210.0, 2.0, (0.0, 0.0, -2.0), vertices=96)
    assign_material(ground, material("Ground", (0.055, 0.06, 0.075, 1.0)))


def assemble_and_save(
    parts: dict[str, bpy.types.Object], output_dir: Path, render_preview: bool
) -> None:
    base_q = P["base_tower"]
    rotor_z = base_q["expected_rotor_datum_from_ground"]
    abs_mat = material("ABS preto", (0.075, 0.09, 0.12, 1.0))
    panel_mat = material("ABS painéis", (0.035, 0.16, 0.42, 1.0))
    tpu_mat = material("TPU", (0.06, 0.06, 0.07, 1.0))
    metal_mat = material("Alumínio", (0.42, 0.45, 0.5, 1.0), metallic=0.75)
    guard_mat = material("Acrílico referência", (0.06, 0.35, 0.55, 1.0), metallic=0.1)

    # Mantém os objetos-fonte ocultos e monta cópias limpas.
    for obj in parts.values():
        obj.hide_render = True
        obj.hide_viewport = True

    base = duplicate(parts["base_tower"], "MONTAGEM_base_torre")
    assign_material(base, abs_mat)
    spider = duplicate(parts["spider"], "MONTAGEM_aranha")
    spider.location.z = rotor_z
    assign_material(spider, abs_mat)
    lid = duplicate(parts["lid"], "MONTAGEM_tampa")
    lid.location.z = rotor_z + P["spider"]["electronics_bay_height"]
    assign_material(lid, abs_mat)

    # A rotacao do objeto e aplicada em torno da propria origem ANTES da
    # translacao, entao a posicao tambem precisa ser rotacionada. Sem isso os
    # tres paineis caem todos em (130, 0, z) e a montagem fica invalida.
    panel_radius = 130.0
    for i in range(3):
        panel = duplicate(parts["panel"], f"MONTAGEM_painel_{i + 1}")
        angle = math.radians(i * 120.0)
        panel.rotation_euler[2] = angle
        panel.location = (
            panel_radius * math.cos(angle),
            panel_radius * math.sin(angle),
            rotor_z + 3.0,
        )
        assign_material(panel, panel_mat)

    plate_ref = duplicate(parts["motor_plate"], "MONTAGEM_suporte_motor_ref")
    plate_ref.location.z = P["base_tower"]["central_floor_thickness"] + P["base_tower"]["tower_total_height_from_floor"]
    assign_material(plate_ref, metal_mat)

    # Representação apenas visual do motor, pois as interfaces ainda não foram medidas.
    motor_h = P["unverified_interfaces"]["motor_stack_height"]["bracket_to_rotor_datum"]
    motor_ref = cylinder("MONTAGEM_motor_2212_ref", 14.0, motor_h, (0.0, 0.0, rotor_z - motor_h / 2))
    assign_material(motor_ref, metal_mat)

    guard_height = P["reference_parts"]["acrylic_guard_height"]
    # Mantém a altura publicada (260 mm) a partir do solo para tornar visível,
    # na montagem, a interferência vertical detectada com o rotor.
    guard_z0 = 0.0
    for obj in build_guard_reference(guard_z0, guard_height):
        assign_material(obj, guard_mat)

    blend_dir = output_dir / "fonte"
    blend_dir.mkdir(parents=True, exist_ok=True)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_dir / "Hologram_Orbiter_v2_1.blend"))

    if render_preview:
        preview_dir = output_dir / "preview"
        preview_dir.mkdir(parents=True, exist_ok=True)
        configure_render(bpy.context.scene, preview_dir / "montagem.png")
        bpy.ops.render.render(write_still=True)


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

    print("[1/8] Modelando painel...")
    panel = build_panel()
    print("[2/8] Modelando aranha...")
    spider = build_spider()
    print("[3/8] Modelando tampa...")
    lid = build_lid()
    print("[4/8] Modelando base + torre...")
    base_tower = build_base_tower()
    print("[5/8] Modelando itens TPU e cupons...")
    damper = build_damper()
    containment = build_containment_ring()
    joint_coupon = build_joint_coupon()
    led_coupon = build_led_coupon()
    motor_plate = build_motor_plate_reference()

    parts = {
        "spider": spider,
        "panel": panel,
        "lid": lid,
        "base_tower": base_tower,
        "damper": damper,
        "containment": containment,
        "joint_coupon": joint_coupon,
        "led_coupon": led_coupon,
        "motor_plate": motor_plate,
    }

    for obj in parts.values():
        cleanup_mesh(obj)

    print("[6/8] Exportando STL...")
    export_stl(spider, stl_dir / "01_aranha_ABS.stl")
    export_stl(panel, stl_dir / "02_painel_LED_ABS_1x.stl", rotate_y_deg=90.0)
    export_stl(
        panel,
        stl_dir / "02_painel_LED_ABS_3x_mesma_mesa.stl",
        rotate_y_deg=90.0,
        copies=[(0.0, -36.0, 0.0), (0.0, 0.0, 0.0), (0.0, 36.0, 0.0)],
    )
    export_stl(lid, stl_dir / "03_tampa_baia_ABS.stl")
    export_stl(base_tower, stl_dir / "04_05_base_torre_ABS_integradas.stl")
    export_stl(damper, stl_dir / "07_coxim_TPU95A_1x.stl")
    export_stl(
        damper,
        stl_dir / "07_coxim_TPU95A_4x_mesma_mesa.stl",
        copies=[(-12.0, -12.0, 0.0), (12.0, -12.0, 0.0), (-12.0, 12.0, 0.0), (12.0, 12.0, 0.0)],
    )
    export_stl(containment, stl_dir / "08_anel_contencao_TPU_REFERENCIA.stl")
    export_stl(joint_coupon, stl_dir / "C01_cupom_junta_11x6.stl")
    export_stl(led_coupon, stl_dir / "C02_cupom_canal_LED_13x1p8.stl")
    export_stl(motor_plate, stl_dir / "R01_suporte_motor_aluminio_NAO_IMPRIMIR.stl")

    print("[7/8] Calculando relatório geométrico...")
    abs_density = P["material"]["abs_density_g_cm3"]
    tpu_density = P["material"]["tpu_density_g_cm3"]
    stats = {
        "spider": object_stats(spider, abs_density),
        "panel_each": object_stats(panel, abs_density),
        "lid": object_stats(lid, abs_density),
        "base_tower": object_stats(base_tower, abs_density),
        "damper_each": object_stats(damper, tpu_density),
        "containment_ring": object_stats(containment, tpu_density),
        "joint_coupon": object_stats(joint_coupon, abs_density),
        "led_coupon": object_stats(led_coupon, abs_density),
    }
    rotor_mass = (
        stats["spider"]["estimated_mass_g"]
        + 3.0 * stats["panel_each"]["estimated_mass_g"]
        + stats["lid"]["estimated_mass_g"]
    )
    rotor_datum = P["base_tower"]["expected_rotor_datum_from_ground"]
    rotor_min_z = rotor_datum + 3.0 - P["panel"]["height"] / 2
    rotor_max_z = rotor_datum + 3.0 + P["panel"]["height"] / 2
    guard_height = P["reference_parts"]["acrylic_guard_height"]
    radial_static = 130.0 + P["panel"]["max_thickness"] / 2
    radial_deflected = radial_static + 3.5
    containment_radius = P["containment_ring"]["inner_diameter"] / 2
    report = {
        "project": P["project"],
        "manufacturing_status": P["manufacturing_status"],
        "geometry": stats,
        "mass_budget": {
            "estimated_rotor_mass_g_at_abs_density": round(rotor_mass, 2),
            "spec_limit_g": 120.0,
            "passes_published_total_limit": rotor_mass <= 120.0,
            "note": "Estimativa geométrica em densidade maciça; o fatiador altera peças volumétricas conforme infill, mas paredes finas permanecem quase maciças.",
        },
        "envelope_checks": {
            "rotor_vertical_min_mm": round(rotor_min_z, 2),
            "rotor_vertical_max_mm": round(rotor_max_z, 2),
            "specified_guard_height_mm": guard_height,
            "guard_if_started_at_ground_shortfall_mm": round(max(0.0, rotor_max_z - guard_height), 2),
            "rotor_static_radius_mm": radial_static,
            "rotor_radius_with_3p5mm_deflection_mm": radial_deflected,
            "containment_inner_radius_mm": containment_radius,
            "radial_clearance_deflected_mm": round(containment_radius - radial_deflected, 2),
        },
        "unverified_interfaces": P["unverified_interfaces"],
    }
    with (report_dir / "geometry_report.json").open("w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

    print("[8/8] Salvando BLEND e renderizando prévia...")
    assemble_and_save(parts, output_dir, render_preview=not ARGS.no_render)
    print(f"Concluído: {output_dir}")
    # Alguns ambientes carregam add-ons com threads persistentes mesmo em
    # background. Encerrar explicitamente mantém scripts CI/build reproduzíveis.
    sys.stdout.flush()
    sys.stderr.flush()
    if bpy.app.background:
        os._exit(0)


if __name__ == "__main__":
    main()
