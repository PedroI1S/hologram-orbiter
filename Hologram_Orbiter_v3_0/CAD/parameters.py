"""Load source dimensions and resolve derived joint dimensions in one place."""
from copy import deepcopy
import json
import math
from pathlib import Path


def resolve_parameters(raw: dict) -> dict:
    p = deepcopy(raw)
    quality = p['quality']
    arm = p['spider']['arm']
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
