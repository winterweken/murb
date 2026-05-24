import pvlib.irradiance
import numpy as np


def get_solar_gains(window_groups, area_windows, epw):
    tot_q_solar = np.zeros([12])
    for window_group in window_groups:
        epw_copy = epw.copy()
        q_solar = pvlib.irradiance.get_total_irradiance(surface_tilt=90,
                                                        surface_azimuth=window_group.window_azimuth,
                                                        solar_zenith=90 - epw_copy.elevation.values,
                                                        solar_azimuth=epw_copy.azimuth.values,
                                                        dni=epw_copy.dni.values,
                                                        ghi=epw_copy.ghi.values,
                                                        dhi=epw_copy.dhi.values,
                                                        albedo=0,  # eliminates ground diffuse
                                                        surface_type=None)['poa_global']
        epw_copy['q_solar'] = q_solar * area_windows * window_group.pct_window_area * window_group.shgc * (
                    1 - window_group.shading) * 0.93 / 1000
        # 0.93 is an attenuation factor for non-normal incidence (source: RETScreen Passive Solar).

        epw_copy = epw_copy.resample('ME').sum()

        q_solar = epw_copy['q_solar'].values

        tot_q_solar = tot_q_solar + q_solar

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
