/**
 * Static constants, unit conversions, and standard assumptions.
 * Direct port of murb_energy_tool/static.py
 */

// ASHRAE Handbook of Fundamentals 2017
export const constants = {
    cp_air: 0.33,        // Volumetric heat capacity of air [Wh/m³K]
    ed_gas: 10.28,       // Energy density of natural gas [kWh/m³]
    h_i_roof: 9.26,      // Interior surface film coefficient - roof [W/m²K]
    h_i_wall: 8.29,      // Interior surface film coefficient - wall [W/m²K]
    h_o: 34              // Exterior surface film coefficient [W/m²K]
};

// Unit conversions
export const conversions = {
    l_per_second_to_m3_per_hour: 3.6
};

// NECB 2017 Data - Table A-8.4.3.2.(2)-A
export const necb = {
    occupant_density: 25,                      // m²/occupant
    peak_receptacle_load: 5,                   // W/m²
    service_water_heating_load: 500,           // W/occupant
    lpd: 7.3,                                  // W/m² (Table 4.2.1.5)
    fraction_occupied: 0.677,                  // Schedule G weekly average
    fraction_lighting: 0.233,
    fraction_receptacle_load: 0.442,
    cooling_setpoint: 24,                      // °C
    heating_setpoint: 21,                      // °C
    fraction_service_water_heating_load: 0.308
};

// ASHRAE 62.1-2019 - Table 6-1
export const ashrae62 = {
    people_outdoor_air_rate: 2.5,   // L/s/person
    area_outdoor_air_rate: 0.3      // L/s/m²
};

// ASHRAE Handbook of Fundamentals 2017 - Chapter 9 Table 4
export const ashraeHof = {
    ppl_met_heat: 1.8 * 60   // Seated, quiet metabolic heat [W/person]
};

// Canada's National Inventory Report 2021 Edition
// Part 3 - Annex 13, 2018 Data
export const ghgElectricity = {  // kgCO2e/kWh
    QC: 1.6 / 1000,
    MB: 1.4 / 1000,
    BC: 13.1 / 1000,
    PE: 290 / 1000,
    NL: 27 / 1000,
    ON: 30 / 1000,
    YT: 79 / 1000,
    NB: 290 / 1000,
    NT: 160 / 1000,
    NS: 740 / 1000,
    SK: 750 / 1000,
    NU: 890 / 1000,
    AB: 690 / 1000
};

// Part 2 - Annex 6, Table A6.1-1 CO2 Emission Factors for Natural Gas
export const ghgNaturalGas = {  // kgCO2e/kWh
    QC: 1887 / 1000 / constants.ed_gas,
    MB: 1886 / 1000 / constants.ed_gas,
    BC: 1926 / 1000 / constants.ed_gas,
    PE: 1901 / 1000 / constants.ed_gas,
    NL: 1901 / 1000 / constants.ed_gas,
    ON: 1888 / 1000 / constants.ed_gas,
    YT: 1901 / 1000 / constants.ed_gas,
    NB: 1901 / 1000 / constants.ed_gas,
    NT: 1901 / 1000 / constants.ed_gas,
    NS: 1901 / 1000 / constants.ed_gas,
    SK: 1829 / 1000 / constants.ed_gas,
    NU: 1901 / 1000 / constants.ed_gas,
    AB: 1928 / 1000 / constants.ed_gas
};

// Province names for display
export const provinceNames = {
    AB: 'Alberta',
    BC: 'British Columbia',
    MB: 'Manitoba',
    NB: 'New Brunswick',
    NL: 'Newfoundland and Labrador',
    NS: 'Nova Scotia',
    NT: 'Northwest Territories',
    NU: 'Nunavut',
    ON: 'Ontario',
    PE: 'Prince Edward Island',
    QC: 'Quebec',
    SK: 'Saskatchewan',
    YT: 'Yukon'
};
