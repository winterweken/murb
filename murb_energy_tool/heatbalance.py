"""
The ``heatbalance`` module contains functions for modeling heat losses and gains due to transmission, ventilation,
infiltration and internal gains.
"""

from murb_energy_tool import static, models
import math


def transmission(u_walls_ag, u_walls_bg, u_windows, u_roof, f_factor, area_walls_ag, area_walls_bg, area_sog, perim_exp,
                 area_windows, area_roof, degree_hours, degree_hours_ground):
    """
Calculates heat losses/gains due to transmission through the building envelope.
    Parameters
    ----------
    u_walls_ag : float
        Overall surface-to-surface U-value of the above-grade walls. Do not include surface films. [W/m2K]
    u_walls_bg : float
        Overall surface-to-surface U-value of the below-grade walls. Do not include surface films. [W/m2K]
    u_windows : float
        Overall surface-to-surface U-value of the above-grade windows. Should be a product U-value which considers
        thermal bridging through the frame. Do not include surface films. [W/m2K]
    u_roof : float
        Overall surface-to-surface U-value of the roof. Do not include surface films. [W/m2K]
    f_factor : float
        F-factor for exposed slabs on grade. [W/mK]
    area_walls_ag : float
        Area of the above-grade walls. [m2]
    area_walls_bg : float
        Area of the below-grade walls. [m2]
    area_sog : float
        Area of underground slabs on grade. [m2]
    perim_exp : float
        Perimeter of exposed slabs on grade. [m]
    area_windows : float
        Area of the windows. [m2]
    area_roof : float
        Area of the roof. [m2]
    degree_hours : array
        Heating or cooling degree hours with respect to the air temperature. [kKh]
    degree_hours_ground : array
        Heating or cooling degree hours with respect to the ground temperature. [kKh]
    Returns
    -------
        Transmission heat losses or gains. [kWh]
    """
    # Above-grade calculations
    u_air_walls_ag = (u_walls_ag ** -1 + static.constants['h_i_wall'] ** -1 + static.constants['h_o'] ** -1) ** -1
    u_air_windows = (u_windows ** -1 + static.constants['h_i_wall'] ** -1 + static.constants['h_o'] ** -1) ** -1
    u_air_roof = (u_roof ** -1 + static.constants['h_i_roof'] ** -1 + static.constants['h_o'] ** -1) ** -1
    area_envelope_ag = area_walls_ag + area_windows + area_roof
    u_avg_ag = (u_air_walls_ag * area_walls_ag + u_air_windows * area_windows + u_air_roof * area_roof) / area_envelope_ag
    q_ag = u_avg_ag * area_envelope_ag * degree_hours

    # Below-grade calculations
    # Calculate average U-factor for basement walls (ASHRAE Handbook of Fundamentals 2017, Chapter 18, Eq. 38)
    k_soil = 1.4  # Soil conductivity, W/m2K
    z_2 = 2.4  # Bottom depth of wall segment under consideration, m
    z_1 = 0.3  # Top depth of wall segment under consideration, m
    r_other = u_walls_bg ** -1 + static.constants['h_i_wall'] ** -1
    u_avg_bw = 2 * k_soil / (math.pi * (z_2 - z_1)) * (math.log(z_2 + 2 * k_soil * r_other / math.pi) - math.log(z_1 + 2 * k_soil * r_other / math.pi))

    q_bg = u_avg_bw * area_walls_bg * degree_hours_ground

    # Exposed slab-on-grade perimeter calculation
    q_sog_exposed = f_factor * perim_exp * degree_hours

    # Underground slab-on-grade calculation
    # Energy Plus Engineering Reference - Ground Heat Transfer Calculations using C and F Factor Constructions
    q_sog = 177**-1 * area_sog * degree_hours

    return q_ag + q_bg + q_sog_exposed + q_sog


def ventilation(oa_rate, heat_recovery, degree_hours):
    """
Calculates heat losses/gains due to mechanical ventilation. Assumes the ventilation system is constantly providing the
minimum outdoor air.
    Parameters
    ----------
    oa_rate : float
        Minimum outdoor air rate from 'heatbalance.outdoor_air_rate'. [m3/h]
    heat_recovery : float
        Seasonal heat recovery effectiveness (sensible only)
    degree_hours : array
        Heating or cooling degree hours. [kKh]

    Returns
    -------
        Ventilation heat losses or gains. [kWh]
    """
    return oa_rate * (1 - heat_recovery) * degree_hours * static.constants['cp_air']


def infiltration(test_leakage, envelope_area_ag, degree_hours):
    """
Calculates heat losses/gains due to infiltration through the building envelope. Assumes a year-round service pressure
difference of 5 Pa and a flow exponent of 0.60 [1].
    Parameters
    ----------
    test_leakage : float
        Air leakage rate at 75 Pa pressure difference. [L/s/m2 exterior area]
    envelope_area_ag : float
        Above-grade envelope area. [m2]
    degree_hours : array
        Heating or cooling degree hours. [kKh]

    Returns
    -------
        Infiltration heat losses or gains. [kWh]

    References
    -------
        [1] CaGBC. (2020). Zero Carbon Building - Design Version 2: Energy Modelling Guidelines
    """

    infiltration_service = test_leakage * ((5/75)**0.60)  # 0.60 is the flow exponent [1][2]
    return infiltration_service * envelope_area_ag * static.conversions['l_per_second_to_m3_per_hour'] * \
           static.constants['cp_air'] * degree_hours


def outdoor_air_rate(gfa, people_outdoor_air_rate, area_outdoor_air_rate, occupancy, za_dist=0.8):
    """
Determines the minimum outdoor air rate as per ASHRAE 62.1-2019.
    Parameters
    ----------
    gfa : float
        Gross floor area. [m2]
    za_dist : float
        Zone air distribution effectiveness. Default is 0.8 for ceiling supply and return.

    Returns
    -------
        Outdoor air rate. [m3/h]

    References
    -------
        ASHRAE. (2019). ASHRAE 62.1 - Ventilation for Acceptable Indoor Air Quality. ASHRAE.
    """
    occupants = gfa / occupancy
    return ((people_outdoor_air_rate * occupants + area_outdoor_air_rate * gfa)
            * static.conversions['l_per_second_to_m3_per_hour']) / za_dist


def internal_gains(gfa, hours, occupancy, fraction_occupied, lpd, fraction_lighting, peak_receptacle_load,
                   fraction_receptacle_load):
    """
Calculates the total internal heat gains due to people, lights and plug loads. Assumes a sensible heat output of 108 W
per person.
    Parameters
    ----------
    gfa : float
        Gross floor area. [m2]
    hours : array
        Hours per each month. [h]
    fraction_occupied : float
        Effective monthly occupancy.
    lpd : float
        Peak lighting power density. [W/m2]
    fraction_lighting : float
        Effective monthly lighting utilisation.
    peak_receptacle_load : float
        Peak plug loads usage. [W/m2]
    fraction_receptacle_load : float
        Effective monthly plug loads utilisation.

    Returns
    -------
        Internal heat gains. [kWh]
    """
    occupants_heat = static.ashrae_hof['ppl_met_heat'] * (gfa / occupancy) * hours * fraction_occupied / 1000
    lighting_heat = models.lighting_energy(gfa=gfa, hours=hours, lpd=lpd, fraction_lighting=fraction_lighting)
    plug_loads = models.plug_loads(gfa=gfa, hours=hours, peak_receptacle_load=peak_receptacle_load,
                                   fraction_receptacle_load=fraction_receptacle_load)
    return occupants_heat + lighting_heat + plug_loads
