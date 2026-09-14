"""Load source dimensions and resolve derived joint dimensions in one place."""
from copy import deepcopy
import json
import math
from pathlib import Path


def resolve_parameters(raw: dict) -> dict:
    p = deepcopy(raw)
    quality = p['quality']
    arm = p['spider']['arm']
    sp = p['spider']
    inner = sp['electronics_bay_id'] / 2
    outer = sp['electronics_bay_od'] / 2
    if not inner <= arm['root_radius'] < outer:
        raise ValueError('A raiz do braço deve começar na parede da baia, entre seus raios interno e externo')
    wr = sp['wire_route']
    y_max = max(abs(v) for v in wr['bay_window_y'])
    inscribed = inner * math.cos(math.pi / quality['curve_segments'])
    if y_max >= inscribed or wr['bay_window_radial'][0] >= math.sqrt(inscribed**2 - y_max**2):
        raise ValueError('O corte da entrada de fios deve começar dentro da baia em toda a largura da janela')
    boss = p['panel']['boss']
    side = quality['joint_xy_clearance_each_side']
    bottom = quality['joint_bottom_clearance']
    if not all(math.isfinite(v) and v >= 0 for v in (side, bottom)):
        raise ValueError('As folgas da junta devem ser finitas e não negativas')
    dimensions = {
        'socket_width': arm['tenon_width'] + 2 * side,
        'socket_height': arm['tenon_height'] + 2 * side,
        'socket_depth': arm['tenon_tip_radius'] - arm['shoulder_radius'] + bottom,
    }
    for key, value in dimensions.items():
        if key in boss and not math.isclose(boss[key], value, abs_tol=1e-8):
            raise ValueError(f'panel.boss.{key} contradiz a espiga/folga; remova a cota derivada')
        boss[key] = value
    bed = p['fdm_rules']['printer_bed_mm']
    if len(bed) != 2 or not all(math.isfinite(v) and v > 0 for v in bed):
        raise ValueError('printer_bed_mm exige duas dimensões positivas')
    if not 0 < p['panel']['mass_limit_assembled_g'] <= p['requirements']['panel_mass_max_g']:
        raise ValueError('Limite de massa do painel não pode exceder o requisito')
    return p


def load_parameters(path: str | Path) -> dict:
    return resolve_parameters(json.loads(Path(path).read_text(encoding='utf-8')))
