import math

from murb_energy_tool.vec import Vec


def get_solar_gains(window_groups, area_windows, epw):
    """Monthly solar gains [kWh] per pvlib's isotropic model with albedo=0:
    poa_global = dni * max(cos(aoi), 0) + dhi * (1 + cos(tilt)) / 2
    For vertical surfaces (tilt=90): sky-diffuse term = dhi / 2, and
    cos(aoi) = cos(sun_elevation) * cos(sun_azimuth - surface_azimuth)."""
    tot_q_solar = Vec.zeros(12)
    for wg in window_groups:
        scale = (area_windows * wg.pct_window_area * wg.shgc
                 * (1 - wg.shading) * 0.93 / 1000.0)
        # 0.93 is an attenuation factor for non-normal incidence
        # (source: RETScreen Passive Solar).
        hourly = []
        for i in range(len(epw.dni)):
            elev_r = math.radians(epw.sun_elevation[i])
            cos_aoi = math.cos(elev_r) * math.cos(
                math.radians(epw.sun_azimuth[i] - wg.window_azimuth))
            beam = epw.dni[i] * cos_aoi if cos_aoi > 0 else 0.0
            poa = beam + epw.dhi[i] * 0.5
            hourly.append(poa * scale)
        tot_q_solar = tot_q_solar + epw.monthly_sum(hourly)
    return tot_q_solar


def utilisation_factors(solar_gains, heat_losses, internal_gains, mass_level):
    coeff = {'a': [1.156, 1., 1.],
             'b': [-0.3479, 4.8380, 0.2792],
             'c': [1.117, 4.533, 0.245],
             'd': [-0.4476, 3.6320, 0.4230]}
    if mass_level == 'low':
        a = coeff['a'][0]
        b = coeff['b'][0]
        c = coeff['c'][0]
        d = coeff['d'][0]
    elif mass_level == 'medium':
        a = coeff['a'][1]
        b = coeff['b'][1]
        c = coeff['c'][1]
        d = coeff['d'][1]
    else:
        a = coeff['a'][2]
        b = coeff['b'][2]
        c = coeff['c'][2]
        d = coeff['d'][2]

    glr = solar_gains / (heat_losses - internal_gains)
    f_i = (a + (b * glr)) / (1 + (c * glr) + (d * glr ** 2))
    return f_i
