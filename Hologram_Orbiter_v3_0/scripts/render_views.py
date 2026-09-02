#!/usr/bin/env python3
"""Renders de inspeção das peças v3.0 (Blender headless, motor Workbench).

    blender -b --python scripts/render_views.py -- --output-dir exports/preview

Importa os STL exportados e renderiza vistas de detalhe para conferência
visual: boss/carenagem do painel, aranha por cima e por baixo, base, tampa e
poste do ímã. Não altera nenhum STL.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--stl-dir", type=Path, default=ROOT / "exports" / "stl")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "exports" / "preview")
    return parser.parse_args(argv)


ARGS = parse_args()


def clear() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def import_stl(path: Path) -> bpy.types.Object:
    bpy.ops.wm.stl_import(filepath=str(path), global_scale=1.0, use_scene_unit=False)
    obj = bpy.context.selected_objects[0]
    obj.hide_render = True
    return obj


def bounds(obj):
    coords = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(v.x for v in coords), min(v.y for v in coords), min(v.z for v in coords)))
    hi = Vector((max(v.x for v in coords), max(v.y for v in coords), max(v.z for v in coords)))
    return lo, hi


def setup_scene() -> None:
    scene = bpy.context.scene
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1000
    scene.render.image_settings.file_format = "PNG"
    try:
        scene.render.engine = "BLENDER_WORKBENCH"
        sh = scene.display.shading
        sh.light = "STUDIO"
        sh.color_type = "SINGLE"
        sh.single_color = (0.62, 0.66, 0.72)
        sh.show_cavity = True
        sh.cavity_type = "BOTH"
        sh.show_object_outline = True
        sh.show_shadows = True
        scene.display.render_aa = "8"
    except Exception as exc:  # pragma: no cover
        print("Workbench indisponível, usando EEVEE:", exc)
        scene.render.engine = "BLENDER_EEVEE"
        if scene.world is None:
            scene.world = bpy.data.worlds.new("World")
        scene.world.color = (0.9, 0.9, 0.9)
        for loc, energy in (((300, -300, 500), 6000.0), ((-300, -100, 300), 3000.0)):
            bpy.ops.object.light_add(type="AREA", location=loc)
            light = bpy.context.object
            light.data.energy = energy
            light.data.size = 300.0


def render(name: str, cam_pos, target, lens=50.0, ortho_scale=None) -> None:
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=cam_pos)
    cam = bpy.context.object
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    if ortho_scale:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho_scale
    else:
        cam.data.lens = lens
    cam.data.clip_start = 1.0
    cam.data.clip_end = 5000.0
    scene.camera = cam
    ARGS.output_dir.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(ARGS.output_dir / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)


def show_only(obj) -> None:
    for o in bpy.data.objects:
        if o.type == "MESH":
            o.hide_render = o is not obj


def main() -> None:
    clear()
    setup_scene()
    stl = ARGS.stl_dir
    panel = import_stl(stl / "02_painel_LED_ABS_1x.stl")
    spider = import_stl(stl / "01_aranha_ABS.stl")
    base = import_stl(stl / "04_05_base_torre_ABS_integradas.stl")
    lid = import_stl(stl / "03_tampa_baia_ABS.stl")
    post = import_stl(stl / "06_poste_ima_ABS.stl")
    coupon = import_stl(stl / "C02_cupom_canal_LED.stl")
    cap_path = stl / "07_tampa_contencao_ABS.stl"
    cap = import_stl(cap_path) if cap_path.exists() else None

    # Painel como impresso: boss para cima (+Z), 208 mm em X, canal contra a mesa.
    # Em coordenadas do STL: x = altura do painel, y = corda (+y = bordo de ataque), z = -x_radial + 30.
    show_only(panel)
    lo, hi = bounds(panel)
    c = (lo + hi) / 2
    boss = Vector((c.x, -5.0, hi.z - 8.0))
    render("painel_boss_nariz", (c.x + 60, boss.y + 90, hi.z + 55), boss, lens=70)
    render("painel_boss_cauda", (c.x - 60, boss.y - 95, hi.z + 50), boss, lens=70)
    render("painel_boss_face_contato", (c.x, boss.y, hi.z + 160), (c.x, boss.y, hi.z), ortho_scale=70)
    render("painel_boss_lado", (c.x + 140, boss.y + 5, hi.z - 5), (c.x, boss.y + 5, hi.z - 12), ortho_scale=64)
    render("painel_completo", (c.x, c.y - 330, hi.z + 240), (c.x, c.y, c.z), lens=45)
    render("painel_ponta_inferior_canal", (lo.x + 30, c.y - 40, lo.z - 40), (lo.x + 6, c.y, lo.z + 2), lens=70)

    show_only(spider)
    render("aranha_topo", (0, 0, 400), (0, 0, 0), ortho_scale=205)
    render("aranha_perspectiva", (140, -190, 150), (0, 0, 8), lens=45)
    render("aranha_raiz_fiacao", (75, -70, 55), (48, -4, 8), lens=85)
    render("aranha_berco", (40, -80, 70), (0, 0, 10), lens=60)
    spider.rotation_euler[0] = math.pi
    render("aranha_baixo", (0, 0, 400), (0, 0, 0), ortho_scale=205)
    render("aranha_baixo_perspectiva", (120, -160, 150), (0, 0, -10), lens=45)
    spider.rotation_euler[0] = 0.0

    show_only(base)
    render("base_perspectiva", (300, -380, 260), (0, 0, 60), lens=40)
    render("base_topo", (0, 0, 900), (0, 0, 0), ortho_scale=300)
    render("base_baia_torre", (140, -170, 150), (0, 0, 70), lens=50)

    show_only(lid)
    render("tampa_topo", (30, -50, 80), (0, 0, 2), lens=60)

    show_only(post)
    render("poste_ima", (60, -25, 40), (22, 14, 10), lens=70)

    show_only(coupon)
    render("cupom_canal_led", (25, -30, 40), (0, 0, 15), lens=70)

    if cap is not None:
        show_only(cap)
        render("tampa_contencao_como_impressa", (260, -330, 260), (0, 0, 3), lens=45)
        render("tampa_contencao_canaleta", (150, -60, 40), (135, 0, 3), lens=80)
    print("Renders em", ARGS.output_dir)


if __name__ == "__main__":
    main()
