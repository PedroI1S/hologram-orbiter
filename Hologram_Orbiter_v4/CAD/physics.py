"""Reproducible engineering estimates for the Hologram Orbiter v4 rotor (mm, g, N, MPa).

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


def _kick_start(schedule, inputs, kt, inertia, drag_torque, omega_design,
                source_voltage, dt=1e-3, settle_s=30.):
    """Integrate the firmware kick start (05 §8.2) on an averaged ESC/motor model.

    Duty is linear in the pulse between the ESC PPM limits; the winding sees
    duty*bus = Kt*omega + R*I. A current-limited bench supply lets the bus sag,
    so at the limit I = efficiency*limit/duty: the phase current RISES while the
    pulse falls and the supply is still limiting. The rotor is held still until
    the kick (on 19/10/2026 nothing below it started), drag scales with omega²
    and the fixed losses are left out of the transient, as in plan 04.
    """
    s = schedule
    resistance, efficiency = inputs["effective_resistance_ohm"], inputs["esc_efficiency"]
    limit = inputs["source_current_limit_a"]
    span = s["ppm_max_us"]-s["ppm_min_us"]
    hold_end = s["rise_s"]+s["kick_hold_s"]
    fall_end = hold_end+(s["kick_us"]-s["target_us"])/s["fall_us_per_s"]
    speed = 0.
    peak = {"rpm": 0., "time_s": s["rise_s"], "pulse_us": s["kick_us"]}
    current_peak = power_peak = 0.
    bus_min = source_voltage
    for step in range(round((fall_end+settle_s-s["rise_s"])/dt)):
        t = s["rise_s"]+step*dt
        pulse = s["kick_us"] if t < hold_end else max(
            s["target_us"], s["kick_us"]-s["fall_us_per_s"]*(t-hold_end))
        duty = (pulse-s["ppm_min_us"])/span
        bus = source_voltage
        current = (duty*bus-kt*speed)/resistance
        if duty*current/efficiency > limit:
            current = efficiency*limit/duty
            bus = (resistance*current+kt*speed)/duty
        current_peak = max(current_peak, current)
        power_peak = max(power_peak, duty*bus*current/efficiency)
        bus_min = min(bus_min, bus)
        if speed*30/math.pi > peak["rpm"]:
            peak = {"rpm": speed*30/math.pi, "time_s": t, "pulse_us": pulse}
        speed += (kt*current-drag_torque*(speed/omega_design)**2)/inertia*dt
    # Steady speed at the target: duty*V = Kt*omega + R*I_drag*(omega/omega_design)².
    a = resistance*drag_torque/kt/omega_design**2
    duty = (s["target_us"]-s["ppm_min_us"])/span
    target_speed = (-kt+math.sqrt(kt*kt+4*a*duty*source_voltage))/(2*a)
    return {"source_voltage_v": source_voltage, "peak_rpm": peak["rpm"],
            "peak_rpm_time_s": peak["time_s"], "peak_rpm_pulse_us": peak["pulse_us"],
            "peak_phase_current_a": current_peak, "peak_input_power_w": power_peak,
            "min_bus_voltage_v": bus_min, "fall_end_s": fall_end,
            "target_rpm": target_speed*30/math.pi, "time_step_s": dt}


def calculate_physics(parameters, panel_triangles=None):
    """Return JSON-serializable section, flexure and drive estimates.

    Optional ``physics_assumptions`` explicitly overrides Kv, resistance, fixed motor
    losses, ESC efficiency, ambient temperature, thermal resistance, the bench
    supply (voltages and current limit), the 8 A phase ceiling and the shaft
    friction clamp. Defaults reproduce the documented assumptions and remain
    unvalidated inputs. ``startup_kick`` is the firmware start schedule.
    """
    p = parameters
    q = p["panel"]
    operating = p["operating_point"]
    loads = p["loads_from_spec"]
    inputs = {"motor_kv": 750., "effective_resistance_ohm": .225,
              "extra_loss_w": .7, "esc_efficiency": .95,
              "ambient_c": 25., "thermal_resistance_k_w": 3.5,
              "source_voltages_v": [10., 12.], "source_current_limit_a": 30.,
              "phase_current_ceiling_a": 8., "shaft_friction_mu": .3,
              "shaft_friction_radius_mm": 7., "nut_factor": .2,
              "abs_strength_mpa": 30.}
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

    voltages = inputs["source_voltages_v"]

    def drive_case(phase_current, speed):
        copper = phase_current**2*inputs["effective_resistance_ohm"]
        loss = copper+inputs["extra_loss_w"]
        power = (kt*phase_current*speed+loss)/inputs["esc_efficiency"]
        return {"phase_current_a": phase_current, "input_power_w": power,
                "source_currents": [{"voltage_v": v, "current_a": power/v} for v in voltages],
                "copper_loss_w": copper,
                "steady_motor_temperature_c": inputs["ambient_c"]
                    + inputs["thermal_resistance_k_w"]*loss}

    kick = p["startup_kick"]
    limit = inputs["source_current_limit_a"]
    duty = (kick["kick_us"]-kick["ppm_min_us"])/(kick["ppm_max_us"]-kick["ppm_min_us"])
    stall = []
    for v in voltages:
        # Stalled: I = duty*V/R, unless the supply limit caps it at efficiency*limit/duty.
        unlimited = duty*v/inputs["effective_resistance_ohm"]
        stall_current = min(unlimited, inputs["esc_efficiency"]*limit/duty)
        stall.append({"source_voltage_v": v, "duty": duty, "phase_current_a": stall_current,
                      "bus_voltage_v": inputs["effective_resistance_ohm"]*stall_current/duty,
                      "source_current_a": duty*stall_current/inputs["esc_efficiency"],
                      "input_power_w": inputs["effective_resistance_ohm"]*stall_current**2
                          / inputs["esc_efficiency"],
                      "torque_nm": kt*stall_current,
                      "supply_limiting": stall_current < unlimited})
    ceiling = drive_case(inputs["phase_current_ceiling_a"], omega)
    ceiling.pop("steady_motor_temperature_c")  # A start transient is not a thermal equilibrium.
    ceiling["torque_nm"] = kt*inputs["phase_current_ceiling_a"]
    trajectories = []
    for v in voltages:
        case = _kick_start(kick, inputs, kt, inertia, drag_torque, omega, v)
        case["exceeds_phase_ceiling"] = case["peak_phase_current_a"] > ceiling["phase_current_a"]
        case["exceeds_start_power_ceiling"] = case["peak_input_power_w"] > ceiling["input_power_w"]
        case["exceeds_operating_rpm"] = case["peak_rpm"] > operating["rpm"]
        trajectories.append(case)
    startup = {"schedule": kick, "source_current_limit_a": limit,
               "stall_at_kick": stall, "trajectories": trajectories,
               "phase_ceiling": ceiling,
               "model": "averaged DC model: duty linear in pulse, a supply at its current limit "
                        "lets the bus sag, rotor still until the kick, drag ~ omega², fixed "
                        "losses ignored in the transient; ignores the ESC Startup Power limit "
                        "and the supply/lead resistance; not a measurement"}
    shaft = p["unverified_interfaces"]["shaft"]
    preload = (p["unverified_interfaces"]["m6_nut"]["torque_nm"]
               / (inputs["nut_factor"]*float(shaft["thread"].lstrip("M"))/1000))
    friction = inputs["shaft_friction_mu"]*inputs["shaft_friction_radius_mm"]/1000

    def clamp_case(torque):
        return {"torque_nm": torque, "required_clamp_force_n": torque/friction,
                "preload_margin": preload*friction/torque}

    shaft_clamp = {
        "preload_estimate_n": preload,
        "preload_basis": "nut torque/(nut_factor*thread diameter); not measured",
        "steady": clamp_case(drag_torque),
        "kick_stall": [dict(clamp_case(c["torque_nm"]), source_voltage_v=c["source_voltage_v"])
                       for c in stall],
        "phase_ceiling": clamp_case(ceiling["torque_nm"]),
        "kick_trajectory_peaks": [dict(clamp_case(kt*c["peak_phase_current_a"]),
                                       source_voltage_v=c["source_voltage_v"])
                                  for c in trajectories],
    }
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
                  "steady": drive_case(current, omega), "startup_kick": startup,
                  "shaft_clamp": shaft_clamp, "stretch": stretch},
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


def section_cut(triangles, axis, value):
    """Section of a closed mesh on the plane ``axis = value``.

    In-plane coordinates are the two remaining axes in cyclic order (u, v), so
    a cut at x = const returns u = y and v = z. ``Ixx_mm4`` is the second moment
    about the u axis (bending by a load along v). Cut away from vertices.
    """
    order = [(axis+1) % 3, (axis+2) % 3, axis]
    tri = np.asarray(triangles, dtype=float)[:, :, order]
    result = section_from_triangles(tri, value)
    points = []
    for t3 in tri:
        for a, b in zip(t3, np.roll(t3, -1, axis=0)):
            if min(a[2], b[2]) < value < max(a[2], b[2]):
                points.append((a+(value-a[2])/(b[2]-a[2])*(b-a))[:2])
    result["boundary_uv"] = np.asarray(points)
    return result


def arm_root_estimate(parameters, spider_triangles, cut_radius_mm=47.5,
                      tilts_deg=(4., 10.)):
    """Vertical bending of one spider arm root when the spin axis is tilted.

    A panel of mass m at radius r pulls with m*omega²*r perpendicular to the
    TRUE spin axis; with the rotor tilted by theta the component across the arm
    is m*omega²*r*sin(theta), applied at the panel mid-plane. Steady synchronous
    whirl is assumed: an oscillating tilt reverses the same load every cycle.
    Geometry is measured on the mesh (arm 1 along +x); FDM strength, layer
    adhesion and the stress raiser at the hub wall are NOT represented.
    """
    p = parameters
    section = section_cut(spider_triangles, 0, cut_radius_mm)
    boundary = section.pop("boundary_uv")
    ixx, iyy, ixy = section["Ixx_mm4"], section["Iyy_mm4"], section["Ixy_mm4"]
    cu, cv = section["centroid_x_mm"], section["centroid_y_mm"]
    det = ixx*iyy-ixy*ixy
    # Unit moment about u (vertical load): unsymmetric bending.
    unit = max(abs((iyy*(v-cv)-ixy*(u-cu))/det) for u, v in boundary)
    omega = p["operating_point"]["rpm"]*2*math.pi/60
    radius = p["operating_point"]["panel_mid_plane_radius_mm"]
    mass = p["panel"]["mass_limit_assembled_g"]/1000
    force = mass*omega**2*radius/1000
    cases = []
    for tilt in tilts_deg:
        moment = force*math.sin(math.radians(tilt))*(radius-cut_radius_mm)
        cases.append({"tilt_deg": tilt, "cross_force_n": force*math.sin(math.radians(tilt)),
                      "moment_n_mm": moment, "max_bending_stress_mpa": moment*unit})
    return {"status": "ESTIMATE_NOT_STRUCTURAL_APPROVAL", "cut_radius_mm": cut_radius_mm,
            "area_mm2": section["area_mm2"], "I_vertical_bending_mm4": ixx,
            "I_chordwise_bending_mm4": iyy, "Ixy_mm4": ixy,
            "section_modulus_vertical_mm3": 1/unit,
            "z_extent_mm": [float(boundary[:, 1].min()), float(boundary[:, 1].max())],
            "panel_mass_g": mass*1000, "rpm": p["operating_point"]["rpm"],
            "centrifugal_force_n": force, "tilt_cases": cases}


def inertia_about_z(triangles, density_g_cm3):
    """Polar moment of inertia about the Z axis of a closed mesh, in kg·m²."""
    tri = np.asarray(triangles, dtype=float)
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    volume = np.einsum("ij,ij->i", a, np.cross(b, c))/6
    total = 0.
    for k in (0, 1):
        x, y, z = a[:, k], b[:, k], c[:, k]
        total += (volume/10*(x*x+y*y+z*z+x*y+x*z+y*z)).sum()
    return abs(total)*density_g_cm3*1e-12  # mm^5 * g/cm³ -> kg·m²


def suspension_estimate(parameters, rotor_mass_g, stage_mass_g, stage_centroid_z_mm,
                        datum_b_z_mm, stage_yaw_inertia_kg_m2=None):
    """Rigid-body estimates for the hanging parallelogram base (variant 3.1-P).

    Eight square rods, built in at both ends, carry the stage in tension. They
    bend in an S, so the stage translates without tilting; gravity adds the
    geometric stiffness 6W/(5L). Rocking is resisted by the rods' axial stiffness
    in series with the stage fins. Printed-PETG modulus, damping, joint
    compliance, gyroscopic coupling and cable stiffness are NOT represented:
    confirm by tap test (plan 04, C0) before spinning.
    """
    bt = parameters["base_tower"]
    s = bt["suspension"]
    rod, fin, stops = s["rod"], s["fin"], s["stops"]
    modulus, count = rod["modulus_mpa"], rod["count"]
    # Each blend stiffens the rod end: count the thin section as free length
    # minus one blend length (independent FE check, review of 11/11/2026).
    span = rod["free_length"]
    length = span-rod.get("blend_length", 0.)
    radius = rod["seat_face_radius"]
    extra = sum(s["moving_mass_extra_g"].values())
    stage = stage_mass_g*s.get("infill_mass_factor", 1.)
    mass = (rotor_mass_g+stage+extra)/1000
    weight = mass*9.80665
    geometric = 1.2*weight/span  # N/mm

    # Fin as a tapered cantilever from the tower wall to the rod.
    r0 = bt["tower_od"]/2
    zb = s["stage_bottom_z"]
    slope = (fin["tip_z"]-fin["top_z_at_tower"])/(fin["tip_radius"]-fin["inner_radius"])
    steps = 400
    compliance = 0.
    for i in range(steps):
        r = r0+(radius-r0)*(i+.5)/steps
        top = fin["top_z_at_tower"]+slope*(min(r, fin["tip_radius"])-fin["inner_radius"])
        inertia = fin["thickness"]*(top-zb)**3/12
        compliance += (radius-r)**2/(modulus*inertia)*(radius-r0)/steps
    fin_stiffness = 1/compliance

    # Transverse inertia about the moving body's own centre of mass: with the
    # translation this soft, rocking happens about the CG, not about the base.
    tower_top = s["stage_top_z"]+bt["tower_total_height_from_floor"]
    rotor_z = datum_b_z_mm+s["rotor_cg_above_tower_top_mm"]-(datum_b_z_mm-tower_top)
    items = [(rotor_mass_g/1000, rotor_z), (stage/1000, stage_centroid_z_mm),
             (extra/1000, tower_top+10.)]
    cg = sum(m*z for m, z in items)/mass
    polar = parameters["loads_from_spec"]["rotor_inertia_g_m2"]/1000
    panel = parameters["panel"]
    own = polar/2+3*panel["mass_limit_assembled_g"]/1000*(panel["height"]/1000)**2/12
    own += stage/1000*(tower_top/1000)**2/12
    transverse = sum(m*((z-cg)/1000)**2 for m, z in items)+own

    # Tower above the fins: tube cantilever with the rotor CG overhung.
    od, wall = bt["tower_od"], bt["tower_wall"]
    tube = math.pi*(od**4-(od-2*wall)**4)/64
    free = tower_top-fin["top_z_at_tower"]
    overhang = rotor_z-tower_top
    factor = 1+3*overhang/free+3*(overhang/free)**2
    tower_stiffness = 3*modulus*tube/(free**3*factor)
    top_mass = (rotor_mass_g+extra)/1000
    tower_frequency = math.sqrt(tower_stiffness*1000/top_mass)/(2*math.pi)
    # Slope at the tower top for 10 N applied `overhang` above it.
    tower_tilt_per_10n = math.degrees(10*(free**2/2+overhang*free)/(modulus*tube))
    low, high = s["operating_rpm_range"]

    variants = []
    for name, side in rod["variants"].items():
        inertia = side**4/12
        elastic = count*12*modulus*inertia/length**3
        lateral = elastic+geometric
        f_lat = math.sqrt(lateral*1000/mass)/(2*math.pi)
        axial = modulus*side*side/length
        series = 1/(1/axial+1/fin_stiffness)
        rocking = count/2*radius**2*series/1000  # N·m/rad
        f_rock = math.sqrt(rocking/transverse)/(2*math.pi)
        # Gravity stiffens yaw exactly as it stiffens translation (review of 11/11/2026).
        yaw = lateral*radius**2/1000  # N·m/rad
        yaw_inertia = (stage_yaw_inertia_kg_m2 or stage/1000*(radius/1000)**2/2)*s.get("infill_mass_factor", 1.)
        # Static lever: lateral force at the rotor reacted at mid-height of the rods.
        rod_mid = s["rim"]["z_range"][1]+span/2
        lever = (rotor_z-rod_mid)/1000
        buckling = 4*math.pi**2*modulus*inertia/length**2
        preload = weight/count
        variants.append({
            "name": name, "rod_side_mm": side,
            "lateral_stiffness_n_per_mm": lateral,
            "lateral_elastic_n_per_mm": elastic, "lateral_gravity_n_per_mm": geometric,
            "translation_frequency_hz": f_lat, "translation_critical_rpm": f_lat*60,
            "lowest_operating_to_critical_ratio": low/(f_lat*60),
            "orbit_amplification_at_lowest_rpm": (low/(f_lat*60))**2/((low/(f_lat*60))**2-1)
                if low > f_lat*60 else None,
            "rod_axial_stiffness_n_per_mm": axial,
            "rod_plus_fin_axial_stiffness_n_per_mm": series,
            "rocking_stiffness_nm_per_rad": rocking, "rocking_frequency_hz": f_rock,
            "rocking_to_top_1x_ratio": f_rock/(high/60),
            "tilt_deg_per_10n_at_rotor": math.degrees(10*lever/rocking)+tower_tilt_per_10n,
            "stage_tilt_deg_per_10n_at_rotor": math.degrees(10*lever/rocking),
            # Rocking and tower bending act in series: Dunkerley estimate of the real lowest mode.
            "coupled_rocking_tower_frequency_hz": 1/math.sqrt(1/f_rock**2+1/tower_frequency**2),
            "rod_buckling_load_n": buckling,
            "rotor_side_force_at_first_buckling_n": (buckling+preload)*4*radius/1000/lever,
            "yaw_frequency_hz": math.sqrt(yaw/yaw_inertia)/(2*math.pi),
            "rod_bending_stress_at_stop_mpa": 3*modulus*side*stops["travel"]/length**2,
            "rod_tension_stress_mpa": weight/count/side**2,
            "yaw_stiffness_nm_per_rad": yaw,
            "yaw_deg_per_0p1_nm": math.degrees(.1/yaw),
        })
    damper = None
    od = s.get("oil_damper", {})
    if od.get("enabled"):
        # Four paddles in oil cups, each with its plane normal to the radius.
        # Normal motion squeezes oil around the plate (~ mu*depth*(width/gap)^3);
        # in-plane motion shears it (mu*area*(1/g1+1/g2)). Order of magnitude only.
        pd, cup = od["paddle"], od["cup"]
        mu = od["oil_viscosity_pa_s"]
        depth = (cup["oil_level_z"]-s["rim"]["z_range"][0])/1000
        width = pd["width"]/1000
        g_in = (pd["inner_radius"]-cup["cavity_radial"][0])/1000
        g_out = (cup["cavity_radial"][1]-pd["inner_radius"]-pd["thickness"])/1000
        gap = (g_in+g_out)/2
        normal = mu*depth*(width/gap)**3
        shear = mu*depth*width*(1/g_in+1/g_out)
        n = len(od["azimuths_deg"])
        c_lat = n/2*(normal+shear)  # two paddles normal, two in-plane, any direction
        r_p = (pd["inner_radius"]+pd["thickness"]/2)/1000
        c_yaw = n*shear*r_p**2
        first = variants[0]
        yaw_inertia = (stage_yaw_inertia_kg_m2 or 0.)*s.get("infill_mass_factor", 1.)
        damper = {
            "status": "ORDER_OF_MAGNITUDE_ONLY (factor ~3 either way); zero without oil",
            "oil_viscosity_pa_s": mu, "immersed_depth_mm": depth*1000,
            "min_radial_gap_mm": min(g_in, g_out)*1000,
            "oil_volume_ml_per_cup": (cup["cavity_radial"][1]-cup["cavity_radial"][0])
                * 2*cup["cavity_half_width"]*(cup["oil_level_z"]-cup["floor"])/1000,
            "lateral_damping_n_s_per_m": c_lat,
            "translation_damping_ratio": c_lat/(2*math.sqrt(first["lateral_stiffness_n_per_mm"]*1000*mass)),
            "yaw_damping_nm_s_per_rad": c_yaw,
            "yaw_damping_ratio": c_yaw/(2*math.sqrt(first["yaw_stiffness_nm_per_rad"]*yaw_inertia))
                if yaw_inertia else None,
        }
    return {
        "status": "ESTIMATE_NOT_MEASURED",
        "oil_damper": damper,
        "moving_mass_kg": mass, "moving_cg_z_mm": cg,
        "moving_mass_breakdown_g": {"rotor": rotor_mass_g, "stage_and_tower": stage,
                                    "motor_plate_fasteners": extra},
        "transverse_inertia_kg_m2": transverse,
        "fin_tip_stiffness_n_per_mm": fin_stiffness,
        "tower_free_length_mm": free, "tower_tube_inertia_mm4": tube,
        "tower_bending_frequency_hz": tower_frequency,
        "operating_rpm_range": [low, high],
        "selected_variant_side_mm": rod["side"],
        "variants": variants,
        "limits": "rigid body, linear rods, no damping, no gyroscopic coupling; printed-PETG "
                  "modulus assumed; motor cables and EVA pads add stiffness when they touch",
    }
