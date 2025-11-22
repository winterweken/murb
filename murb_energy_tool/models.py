"""
The ``models`` module contains functions for modeling lighting energy use, domestic hot water, plug loads, space heating
and space cooling.
"""

from murb_energy_tool import static


def lighting_energy(gfa, hours, lpd, fraction_lighting):
    """
Calculates the interior lighting energy use.
    Parameters
    ----------
    gfa : float
        Gross floor area. [m2]
    hours : array
        Hours per each month. [h]
    lpd : float
        Peak lighting power density/ [W/m2]
    fraction_lighting : float
        Effective monthly lighting utilisation.

    Returns
    -------
        Lighting energy use. [kWh]
    """
    return (lpd / 1000) * gfa * hours * fraction_lighting


def domestic_hot_water(gfa, hours, occupancy, cop_dhw, service_water_heating_load):
    """
Calculates the domestic hot water energy use.
    Parameters
    ----------
    gfa : float
        Gross floor area. [m2]
    hours : array
        Hours per each month. [h]
    cop_dhw: float
        Seasonal COP of the domestic how water heater.
    service_water_heating_load : float
        Peak DHW heating load. [W/person]

    Returns
    -------
        Domestic hot water energy use. [kWh]
    """
    return ((service_water_heating_load / 1000) * (gfa / occupancy) * hours *
            static.necb['fraction_service_water_heating_load']) / cop_dhw


def plug_loads(gfa, hours, peak_receptacle_load, fraction_receptacle_load):
    """
Calculates the energy used by plug loads (e.g. computers).
    Parameters
    ----------
    gfa : float
        Gross floor area. [m2]
    hours : array
        Hours per each month. [h]
    peak_receptacle_load : float
        Peak plug loads. [W/m2]
    fraction_receptacle_load : float
        Effective monthly lighting utilisation.

    Returns
    -------
        Plug loads energy use [kWh].
    """
    return (peak_receptacle_load / 1000) * gfa * hours * fraction_receptacle_load


def space_heating_energy_use(heating_demand, cop_heating):
    """
Calculates the space heating energy use from the heating demand.
    Parameters
    ----------
    heating_demand : float
        Space heating demand.
    cop_heating : float
        Seasonal COP of the space heating plant.

    Returns
    -------
        Space heating energy use.
    """
    return heating_demand / cop_heating


def cooling_energy_use(cooling_demand, cop_cooling):
    """
Calculates the space cooling energy use from the cooling demand.
    Parameters
    ----------
    cooling_demand : float
        Space cooling demand.
    cop_cooling : float
        Seasonal COP of the space cooling plant.

    Returns
    -------
        Space cooling energy use.
    """
    return cooling_demand / cop_cooling
