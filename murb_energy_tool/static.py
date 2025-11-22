"""
This file contains constants, unit conversions and standard assumptions used throughout the murb_energy_tool library.
"""

# CONSTANTS
constants = dict(
    # Volumetric heat capacity of air
    cp_air=0.33,  # Wh/m3K

    # Energy density of natural gas
    ed_gas=10.28,  # kWh/m3

    # ASHRAE Handbook of Fundamentals 2017 ch.26
    # Table 10 - Surface Film Coefficients/Resistances
    h_i_roof=9.26,  # W/m2K
    h_i_wall=8.29,  # W/m2K
    h_o=34)  # W/m2K

# CONVERSIONS
conversions = dict(
    #  L/s >> m3/h
    l_per_second_to_m3_per_hour=3.6)

# NECB 2017 DATA
necb = dict(
    # Table A-8.4.3.2.(2)-A
    # Modeling Guidance for Loads, Operating Schedules and Illuminance Levels by Building Type
    occupant_density=25,  # m2/occupant
    peak_receptacle_load=5,  # W/m2
    service_water_heating_load=500,  # W/occupant

    # Table 4.2.1.5
    # Lighting Power Density by Building Type
    lpd=7.3,  # W/m2

    # Table A-8.4.3.2.(1)-G
    # Operating Schedule G
    # Weekly-averaged by Jonathan Graham
    fraction_occupied=0.677,
    fraction_lighting=0.233,
    fraction_receptacle_load=0.442,
    cooling_setpoint=24,  # C
    heating_setpoint=21,  # C
    fraction_service_water_heating_load=0.308)

# ASHRAE 62.1-2019 DATA
ashrae_62 = dict(
    # Table 6-1
    # Minimum Ventilation Rates in Breathing Zone
    people_outdoor_air_rate=2.5,  # L/s person
    area_outdoor_air_rate=0.3)  # L/s m2

# ASHRAE Handbook of Fundamentals 2017
ashrae_hof = dict(
    # Chapter 9 Thermal Comfort
    # Table 4 - Typical Metabolic Heat Generation for Various Activities
    ppl_met_heat=1.8 * 60)  # Resting - Seated, quiet

# CANADA'S NATIONAL INVENTORY REPORT 2021 EDITION
# Part 3 - Annex 13, 2018 Data
ghg_electricity = {  # kgCO2e/kWh
    'QC': 1.6/1000,
    'MB': 1.4/1000,
    'BC': 13.1/1000,
    'PE': 290./1000,  # PEI imports much of their electricity from New Brunswick, and as such New Brunswick emissions
    # factors for electricity are used.
    'NL': 27./1000,
    'ON': 30./1000,
    'YT': 79./1000,
    'NB': 290./1000,
    'NT': 160./1000,
    'NS': 740./1000,
    'SK': 750./1000,
    'NU': 890./1000,
    'AB': 690./1000
}
# Part 2- Annex 6, Table A6.1-1 CO2 Emission Factors for Natural Gas
ghg_natural_gas = {  # kgCO2e/kWh
    'QC': 1887/1000/constants['ed_gas'],
    'MB': 1886/1000/constants['ed_gas'],
    'BC': 1926/1000/constants['ed_gas'],
    'PE': 1901/1000/constants['ed_gas'],  # Not shown in NIR. Took mode of the provinces.
    'NL': 1901/1000/constants['ed_gas'],
    'ON': 1888/1000/constants['ed_gas'],
    'YT': 1901/1000/constants['ed_gas'],
    'NB': 1901/1000/constants['ed_gas'],
    'NT': 1901/1000/constants['ed_gas'],
    'NS': 1901/1000/constants['ed_gas'],
    'SK': 1829/1000/constants['ed_gas'],
    'NU': 1901/1000/constants['ed_gas'],
    'AB': 1928/1000/constants['ed_gas']
}
