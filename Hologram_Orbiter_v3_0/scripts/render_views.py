#!/usr/bin/env python3
"""Renders de inspeção das peças v3.0 (Blender headless, motor Workbench).

    blender -b --python scripts/render_views.py -- --output-dir exports/preview

Importa os STL exportados e renderiza vistas de detalhe para conferência
visual: boss/carenagem do painel, aranha por cima e por baixo, base, tampa,
suporte do ímã e cupom do canal. Não altera nenhum STL.
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
    bracket = import_stl(stl / "06_suporte_ima_ABS.stl")
    coupon = import_stl(stl / "C02_cupom_canal_LED.stl")
    cap_path = stl / "07_tampa_contencao_ABS.stl"
    cap = import_stl(cap_path) if cap_path.exists() else None

    # Remove renders de peças que não existem mais nesta revisão.
    for stale in ("poste_ima.png", "tampa_contencao_canaleta.png", "tampa_contencao_como_impressa.png", "tampa_topo.png"):
        p = ARGS.output_dir / stale
        if p.exists() and (stale != "tampa_topo.png") and cap is None:
            p.unlink()

    # Painel como impresso: boss para cima (+Z), 208 mm em X, canal contra a mesa.
    # Em coordenadas do STL: x = altura do painel, y = corda (+y = bordo de ataque), z = 4 - x_radial.
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
    # Seção do canal em degrau vista pela ponta (a fatia do cupom mostra o mesmo).

    show_only(spider)
    render("aranha_topo", (0, 0, 400), (0, 0, 0), ortho_scale=215)
    render("aranha_perspectiva", (150, -200, 160), (0, 0, 10), lens=45)
    render("aranha_raiz_fiacao", (80, -75, 60), (52, -4, 10), lens=85)
    render("aranha_berco", (45, -90, 80), (0, 0, 12), lens=60)
    render("aranha_raiz_gusset", (115, -70, 24), (52, 0, 5), lens=70)
    spider.rotation_euler[0] = math.pi
    render("aranha_baixo", (0, 0, 400), (0, 0, 0), ortho_scale=215)
    render("aranha_baixo_perspectiva", (130, -170, 160), (0, 0, -10), lens=45)
    spider.rotation_euler[0] = 0.0

    show_only(base)
    render("base_perspectiva", (310, -390, 270), (0, 0, 60), lens=40)
    render("base_topo", (0, 0, 900), (0, 0, 0), ortho_scale=330)
    render("base_baia_torre", (140, -170, 150), (0, 0, 70), lens=50)
    tab = Vector((149 * math.cos(math.radians(-45)), 149 * math.sin(math.radians(-45)), 4.0))
    render("base_aba_grampo", (tab.x + 70, tab.y - 70, 60), tab, lens=80)
    render("base_flange_superior", (90, -110, 200), (0, 0, 150), lens=70)

    show_only(lid)
    render("tampa_topo", (35, -60, 90), (0, 0, 2), lens=60)

    show_only(bracket)
    lo, hi = bounds(bracket)
    c = (lo + hi) / 2
    render("suporte_ima", (c.x + 45, c.y - 55, hi.z + 35), (c.x, c.y, hi.z / 2), lens=60)
    render("suporte_ima_topo", (c.x, c.y, 200), (c.x, c.y, 0), ortho_scale=60)

    show_only(coupon)
    lo, hi = bounds(coupon)
    c = (lo + hi) / 2
    render("cupom_canal_led", (c.x + 40, c.y - 45, hi.z + 45), (c.x, c.y, c.z), lens=70)
    # Olhando para dentro da face cortada (z = -74 do painel), de cima e de viés:
    # mostra a seção em degrau, o piso de 0,8 e a cavidade atrás.
    render("cupom_canal_led_secao", (hi.x + 38, c.y - 22, hi.z + 26), (hi.x, c.y, c.z + 1), lens=70)

    if cap is not None:
        show_only(cap)
        render("tampa_contencao_como_impressa", (260, -330, 260), (0, 0, 3), lens=45)
        render("tampa_contencao_canaleta", (150, -60, 40), (135, 0, 3), lens=80)
    print("Renders em", ARGS.output_dir)


if __name__ == "__main__":
    main()
