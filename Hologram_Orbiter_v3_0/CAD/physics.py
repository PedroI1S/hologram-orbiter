"""Reproducible engineering estimates for the v3 rotor (mm, g, N, MPa).

This module does not certify FDM strength, creep, the blade/boss load path,
motor cooling, or drag coefficients. ``panel_triangles`` must use the local
panel coordinates BEFORE the STL print rotation: x radial, y chord, z height.
The 1.55 g m² design inertia remains a conservative, unmeasured input.
"""

from __future__ import annotations

import math

import numpy as np


def polygon_integrals(points):
    """Return positive A, integral x/y/x²/y²/xy for a simple polygon."""
    p = np.asarray(points, dtype=float)
    if len(p) < 3:
        return np.zeros(6)
    q = np.roll(p, -1, axis=0)
    x, y = p.T
    u, v = q.T
    cross = x * v - u * y
    result = np.array([
        cross.sum() / 2,
        ((x + u) * cross).sum() / 6,
        ((y + v) * cross).sum() / 6,
        ((x*x + x*u + u*u) * cross).sum() / 12,
        ((y*y + y*v + v*v) * cross).sum() / 12,
        ((2*x*y + x*v + u*y + 2*u*v) * cross).sum() / 24,
    ])
    return result * np.sign(result[0])


def _clip(points, axis, value, keep_greater):
    result = []
    for a, b in zip(points, points[1:] + points[:1]):
        inside_a = a[axis] >= value if keep_greater else a[axis] <= value
        inside_b = b[axis] >= value if keep_greater else b[axis] <= value
        if inside_a:
            result.append(a)
        if inside_a != inside_b:
            t = (value - a[axis]) / (b[axis] - a[axis])
            result.append([a[0] + t*(b[0]-a[0]), a[1] + t*(b[1]-a[1])])
    return result


def _rectangle_intersection(points, x0, x1, y0, y1):
    points = [list(p) for p in points]
    for axis, value, greater in [(0, x0, True), (0, x1, False),
                                  (1, y0, True), (1, y1, False)]:
        points = _clip(points, axis, value, greater)
    return points


def _centroidal(integrals):
    area, qx, qy, yy, xx, xy = map(float, integrals)
    if area <= 0:
        raise ValueError("Section must have positive signed area")
    cx, cy = qx / area, qy / area
    yy, xx, xy = yy - qx*qx/area, xx - qy*qy/area, xy - qx*qy/area
    effective = yy - xy*xy/xx
    if effective <= 0:
        raise ValueError("Section has nonpositive flexural rigidity")
    return {"area_mm2": area, "centroid_x_mm": cx, "centroid_y_mm": cy,
            "Iyy_mm4": yy, "Ixx_mm4": xx, "Ixy_mm4": xy,
            "I_effective_radial_mm4": effective}


def panel_section(parameters):
    """Integrate the ordinary blade section, away from ribs, boss and end caps."""
    q = parameters["panel"]
    channel = q["led_channel"]
    outer, cavity = q["profile_outer_xy"], q["profile_cavity_xy"]
    x_out = q["max_thickness"] / 2
    half = channel["width"] / 2
    band_half = half + channel["local_wall_band_margin"]
    added_wall = _rectangle_intersection(
        cavity, x_out-channel["local_wall"], x_out, -band_half, band_half)
    removed_channel = _rectangle_intersection(
        outer, x_out-channel["depth"], x_out, -half, half)
    result = _centroidal(polygon_integrals(outer) - polygon_integrals(cavity)
                         + polygon_integrals(added_wall)
                         - polygon_integrals(removed_channel))
    result["method"] = "outer minus cavity plus local wall minus LED channel"
    result["scope"] = "continuous blade only; no structural credit for LED strip"
    result["extreme_outer_x_mm"] = max(p[0] for p in outer)
    result["extreme_inner_x_mm"] = min(p[0] for p in outer)
    return result


def section_from_triangles(panel_triangles, z_mm):
    """Independently integrate an oriented horizontal cut through local triangles.

    Use a plane away from mesh vertices and coplanar faces. Boundary orientation
    comes from the triangle normal, so interior cavities subtract automatically.
    """
    result = np.zeros(6)
    for tri in np.asarray(panel_triangles, dtype=float):
        intersections = []
        for a, b in zip(tri, np.roll(tri, -1, axis=0)):
            if min(a[2], b[2]) < z_mm < max(a[2], b[2]):
                t = (z_mm-a[2]) / (b[2]-a[2])
                intersections.append(a+t*(b-a))
        if len(intersections) != 2:
            continue
        a, b = intersections
        tangent = np.cross([0., 0., 1.], np.cross(tri[1]-tri[0], tri[2]-tri[0]))
        if np.dot(b-a, tangent) < 0:
            a, b = b, a
        x, y = a[:2]
        u, v = b[:2]
        cross = x*v-u*y
        result += np.array([cross/2, (x+u)*cross/6, (y+v)*cross/6,
                            (x*x+x*u+u*u)*cross/12,
                            (y*y+y*v+v*v)*cross/12,
                            (2*x*y+x*v+u*y+2*u*v)*cross/24])
    return _centroidal(result)


def _flexure_case(section, vertices, load, length, modulus):
    moment = load*length**2/2
    ixx, iyy, ixy = section["Ixx_mm4"], section["Iyy_mm4"], section["Ixy_mm4"]
    determinant = ixx*iyy-ixy*ixy
    cx, cy = section["centroid_x_mm"], section["centroid_y_mm"]
    # Unsymmetric bending with applied radial load: zero moment about x.
    stress = max(abs(moment*(ixx*(x-cx)-ixy*(y-cy))/determinant)
                 for x, y in vertices)
    return {"unsupported_length_mm": length, "modulus_mpa": modulus,
            "distributed_load_n_per_mm": load,
            "tip_deflection_mm": load*length**4/(8*modulus*section["I_effective_radial_mm4"]),
            "max_bending_stress_mpa": stress,
            "nominal_strength_ratio_at_30_mpa": 30/stress,
            "strength_certified": False}


def calculate_physics(parameters, panel_triangles=None):
    """Return JSON-serializable section, flexure and drive estimates.

    Optional ``physics_assumptions`` explicitly overrides Kv, resistance, fixed motor
    losses, ESC efficiency, ambient temperature and thermal resistance. Defaults
    reproduce the documented assumptions and remain unvalidated inputs.
    """
    p = parameters
    q = p["panel"]
    operating = p["operating_point"]
    loads = p["loads_from_spec"]
    inputs = {"motor_kv": 920., "effective_resistance_ohm": .221,
              "extra_loss_w": .7, "esc_efficiency": .95,
              "ambient_c": 25., "thermal_resistance_k_w": 3.5,
              "source_voltage_v": 7., "abs_strength_mpa": 30.}
    inputs.update(p.get("physics_assumptions", {}))
    omega = operating["rpm"]*2*math.pi/60
    radius_mm = operating["panel_mid_plane_radius_mm"]
    section = panel_section(p)
    force = loads["panel_assembled_mass_g"]/1000*omega**2*radius_mm/1000
    w_envelope = force/q["height"]
    envelope = [_flexure_case(section, q["profile_outer_xy"], w_envelope, length, modulus)
                for length, modulus in [(86., 2300.), (86., 2000.), (99., 2000.)]]
    rho = p["material"]["abs_density_g_cm3"]/1000  # g/mm³
    shell_mass_per_mm = section["area_mm2"]*rho
    strip = p["unverified_interfaces"]["led_strip"]
    led_mass_per_mm = p["non_cad_masses_g"]["led_strip_per_panel"]/strip["strip_length"]
    led_x = q["max_thickness"]/2-q["led_channel"]["depth"]+strip["thickness"]/2
    w_estimate = omega**2/1e6*(shell_mass_per_mm*(radius_mm+section["centroid_x_mm"])
                              + led_mass_per_mm*(radius_mm+led_x))
    kt = 60/(2*math.pi*inputs["motor_kv"])
    current = operating["phase_current_a"]
    drag_torque = kt*current
    inertia = loads["rotor_inertia_g_m2"]/1000

    def drive_case(phase_current, speed):
        copper = phase_current**2*inputs["effective_resistance_ohm"]
        loss = copper+inputs["extra_loss_w"]
        power = (kt*phase_current*speed+loss)/inputs["esc_efficiency"]
        return {"phase_current_a": phase_current, "input_power_w": power,
                "source_current_a": power/inputs["source_voltage_v"],
                "source_voltage_v": inputs["source_voltage_v"],
                "copper_loss_w": copper,
                "steady_motor_temperature_c": inputs["ambient_c"]
                    + inputs["thermal_resistance_k_w"]*loss}

    startup = []
    for seconds in [8., 12.]:
        acceleration_torque = inertia*omega/seconds
        case = drive_case((drag_torque+acceleration_torque)/kt, omega)
        case.pop("steady_motor_temperature_c")  # A transient is not a thermal equilibrium.
        case.update({"ramp_s": seconds, "acceleration_torque_nm": acceleration_torque})
        startup.append(case)
    stretch_rpm = operating["stretch_rpm_not_target"]
    stretch = drive_case(current*(stretch_rpm/operating["rpm"])**2,
                         stretch_rpm*2*math.pi/60)
    stretch["rpm"] = stretch_rpm
    stretch["released_for_operation"] = False
    result = {
        "status": "ESTIMATE_NOT_STRUCTURAL_OR_OPERATIONAL_APPROVAL",
        "operation_released": False,
        "section": section,
        "flexure": {
            "design_panel_mass_g": loads["panel_assembled_mass_g"],
            "design_centrifugal_force_n": force,
            "envelope_cases": envelope,
            "acceptance_mass_limit_g": q["mass_limit_assembled_g"],
            "acceptance_limit_cases": [
                _flexure_case(section, q["profile_outer_xy"],
                              w_envelope*q["mass_limit_assembled_g"]/loads["panel_assembled_mass_g"],
                              length, modulus)
                for length, modulus in [(86., 2300.), (86., 2000.), (99., 2000.)]],
            "envelope_assumption": "whole panel mass uniformly distributed over height; ideal clamp",
            "distributed_load_estimate": {
                "shell_mass_g_per_mm": shell_mass_per_mm,
                "led_mass_g_per_mm": led_mass_per_mm,
                "load_n_per_mm": w_estimate,
                "cases": [_flexure_case(section, q["profile_outer_xy"], w_estimate, length, 2000.)
                          for length in [86., 99.]],
                "limitations": "continuous solid ABS shell and uniform LED mass only; excludes ribs, end caps, wiring and boss compliance; not an acceptance bound",
            },
            "required_before_final_panel_print": ["blade/boss load transfer", "actual FDM section and modulus", "loaded creep test"],
        },
        "drive": {"inputs_unvalidated": inputs, "omega_rad_s": omega,
                  "torque_constant_nm_per_a": kt, "design_drag_torque_nm": drag_torque,
                  "inertia_g_m2": inertia*1000,
                  "inertia_status": "conservative unmeasured design premise",
                  "rotor_energy_j": .5*inertia*omega**2,
                  "steady": drive_case(current, omega), "startup": startup,
                  "stretch": stretch},
    }
    if panel_triangles is not None:
        checks = []
        for z in [20.23, 50.23, 90.23]:
            measured = section_from_triangles(panel_triangles, z)
            keys = ["area_mm2", "centroid_x_mm", "centroid_y_mm", "Iyy_mm4", "Ixx_mm4", "Ixy_mm4"]
            matches = all(math.isclose(measured[key], section[key], abs_tol=.001, rel_tol=1e-6)
                          for key in keys)
            checks.append({"z_mm": z, "measured": measured, "matches_parameters": matches})
        result["stl_section_checks"] = checks
    return result
