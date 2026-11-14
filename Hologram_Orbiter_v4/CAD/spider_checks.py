"""Functional checks of the arm roots and wire entries on the final mesh."""
import math

import numpy as np

from probe import MeshProbe


def measure_bay_entries(triangles, parameters, hub_z=0.0):
    """Probe all three entries; hub_z is 0 in CAD and 6 in the print STL.

    Rays start in the empty bay next to its wall. Stay inside the polygon's
    inscribed circle for the root check, so cylinder tessellation is allowed.
    Probe both the full window and its overlap with the external wire pocket.
    These checks complement topology tests, which accept a blocked passage.
    """
    sp = parameters["spider"]
    wr = sp["wire_route"]
    pr = MeshProbe(triangles)
    inner = sp["electronics_bay_id"] / 2
    inscribed = inner * math.cos(math.pi / parameters["quality"]["curve_segments"])
    z0, z1 = wr["bay_window_z"]
    y0, y1 = wr["bay_window_y"]
    arms = []
    for i in range(3):
        angle = math.radians(i * 120)
        c, s = math.cos(angle), math.sin(angle)

        def clear(x0, x1, y, z):
            return pr.is_void((x0*c - y*s, x0*s + y*c, z + hub_z),
                              (c, s, 0.0), x1 - x0)

        root_blocked = window_blocked = root_rays = window_rays = 0
        # Central strip of each root. The lateral bay region also contains
        # legitimate buck guides; it must not be assumed entirely empty.
        for y in np.linspace(-2.0, 2.0, 9):
            end = math.sqrt(inscribed**2 - y*y) - .05
            for z in np.linspace(.15, sp["arm"]["height"] - .15, 9):
                root_rays += 1
                root_blocked += not clear(end - 1.5, end, y, z)
        for y in np.linspace(y0 + .15, y1 - .15, 11):
            start = math.sqrt(inscribed**2 - y*y) - 1.5
            for z in np.linspace(z0 + .15, z1 - .15, 11):
                # Below the pocket floor only the wall opening must be free.
                # Above it, continue through the overlap into the pocket.
                end = wr["root_pocket_radial"][0] - .05
                if z > wr["groove_floor_z"] + .1:
                    end = wr["bay_window_radial"][1] + .1
                window_rays += 1
                window_blocked += not clear(start, end, y, z)
        arms.append({"arm": i + 1, "root_rays": root_rays,
                     "root_blocked_rays": root_blocked,
                     "window_rays": window_rays,
                     "window_blocked_rays": window_blocked})
    return {"arms": arms,
            "roots_clear": all(r["root_blocked_rays"] == 0 for r in arms),
            "windows_clear": all(r["window_blocked_rays"] == 0 for r in arms)}
