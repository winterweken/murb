"""
The ``routines`` module contains functions for commonly requested feasibility analysis.
"""

from murb_energy_tool import static, simulation
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd


class PerformanceTarget:
    def __init__(self, name, tedi=None, teui=None, ghgi=None):
        """
Performance target object used by various function.
        Parameters
        ----------
        name : str
        Name of the target (e.g. "Toronto Green Standard v4 Tier 2)
        tedi : float
        Thermal energy demand intensity (kWh/m2yr)
        teui : float
        Total energy use intensity (kWh/m2yr)
        ghgi : float
        Greenhouse gas emissions intensity (kgCO2e/m2yr)
        """
        self.name = name
        self.tedi = tedi
        self.teui = teui
        self.ghgi = ghgi


def minimum_facade_performance(
        name,
        province,
        gfa,
        area_walls,
        area_windows,
        area_roof,
        window_groups,
        performance_targets,
        setpoint_htg=21,
        setpoint_clg=24,
        cop_htg=0.85,
        cop_clg=5.2,
        cop_dhw=0.85,
        hrv_efficiency=0.55,
        u_facade_start=0.1,  # ~R-60
        u_facade_stop=2.8,  # ~R-2
        u_facade_num=10,
        u_roof=0.164,
        test_leakage=2,
        **kwargs):
    default_kwargs = {'clg_pct': 1,
                      'occupant_density': static.necb['occupant_density'],
                      'peak_receptacle_load': static.necb['peak_receptacle_load'],
                      'lpd': static.necb['lpd'],
                      'fraction_occupied': static.necb['fraction_occupied'],
                      'fraction_lighting': static.necb['fraction_lighting'],
                      'fraction_receptacle_load': static.necb['fraction_receptacle_load'],
                      'service_water_heating_load': static.necb['service_water_heating_load'],
                      'mass_level': 'medium'}
    kwargs = {**default_kwargs, **kwargs}

    print(f'Running {u_facade_num} simulations to determine maximum U-value\n')

    df = pd.DataFrame(index=np.linspace(u_facade_start, u_facade_stop, u_facade_num), columns=['tedi', 'teui', 'ghgi'])

    for row in df.itertuples():
        sim = simulation.Run(
            name=name,
            province=province,
            gfa=gfa,
            area_walls_ag=area_walls,
            area_windows=area_windows,
            area_roof=area_roof,
            window_groups=window_groups,
            setpoint_htg=setpoint_htg,
            setpoint_clg=setpoint_clg,
            cop_htg=cop_htg,
            cop_clg=cop_clg,
            cop_dhw=cop_dhw,
            hrv_efficiency=hrv_efficiency,
            u_walls=row.Index,
            u_windows=row.Index,
            u_roof=u_roof,
            test_leakage=test_leakage,
            isd_file=None,
            silent=True,
            clg_pct=kwargs['clg_pct'],
            occupant_density=kwargs['occupant_density'],
            peak_receptacle_load=kwargs['peak_receptacle_load'],
            lpd=kwargs['lpd'],
            fraction_occupied=kwargs['fraction_occupied'],
            fraction_lighting=kwargs['fraction_lighting'],
            fraction_receptacle_load=kwargs['fraction_receptacle_load'],
            service_water_heating_load=kwargs['service_water_heating_load'],
            mass_level=kwargs['mass_level'])

        df.at[row.Index, 'tedi'] = np.sum(sim.heating_demand) / sim.gfa
        df.at[row.Index, 'teui'] = np.sum(sim.total_energy_consumption) / sim.gfa
        df.at[row.Index, 'ghgi'] = np.sum(sim.total_ghg_emissions) / sim.gfa

    # Approximate quadratic functions of TEDI/TEUI/GHGI with respect to U-value
    f_tedi = interp1d(df.index, df.tedi, kind='quadratic')
    f_teui = interp1d(df.index, df.teui, kind='quadratic')
    f_ghgi = interp1d(df.index, df.ghgi, kind='quadratic')

    # Approximate functions of U-value with respect to TEDI/TEUI/GHGI
    f_tedi_r = interp1d(df.tedi, df.index)
    f_teui_r = interp1d(df.teui, df.index)
    f_ghgi_r = interp1d(df.ghgi, df.index)

    for target in performance_targets:

        # Estimate facade U-value required to meet the TEDI targets
        if target.tedi is not None:
            if not (df.tedi.min() < target.tedi < df.tedi.max()):
                raise Exception(f'TEDI target "{target.name}" does not intersect with the interpolated function.'
                                f' Either increase the range of U-values assessed or set this target to None')
            else:
                u_for_tedi = round(float(f_tedi_r(target.tedi)), 2)
                print(
                    f'To meet the {target.name} TEDI target of {target.tedi} kWh/m2yr, overall facade U-value must be no greater than {u_for_tedi} W/m2K')
        else:
            u_for_tedi = None

        # Estimate facade U-value required to meet the TEUI targets
        if target.teui is not None:
            if not (df.teui.min() < target.teui < df.teui.max()):
                raise Exception(f'TEUI target "{target.name}" does not intersect with the interpolated function.'
                                f' Either increase the range of U-values assessed or set this target to None')
            else:
                u_for_teui = round(float(f_teui_r(target.teui)), 2)
                print(
                    f'To meet the {target.name} TEUI target of {target.teui} kWh/m2yr, overall facade U-value must be no greater than {u_for_teui} W/m2K')
        else:
            u_for_teui = None

        # Estimate facade U-value required to meet the GHGI targets
        if target.ghgi is not None:
            if not (df.ghgi.min() < target.ghgi < df.ghgi.max()):
                raise Exception(f'GHGI target "{target.name}" does not intersect with the interpolated function.'
                                f' Either increase the range of U-values assessed or set this target to None')
            else:
                u_for_ghgi = round(float(f_ghgi_r(target.ghgi)), 2)
                print(
                    f'To meet the {target.name} GHGI target of {target.ghgi} kgCO2e/m2yr, overall facade U-value must be no greater than {u_for_ghgi} W/m2K')
        else:
            u_for_ghgi = None
        print('\n')

    return {"f_tedi": f_tedi,
            "f_tedi_r": f_tedi_r,
            "f_teui": f_teui,
            "f_teui_r": f_teui_r,
            "f_ghgi": f_ghgi,
            "f_ghgi_r": f_ghgi_r}


def minimum_cop_htg_performance(
        name,
        province,
        gfa,
        area_walls,
        area_windows,
        area_roof,
        window_groups,
        performance_targets,
        setpoint_htg=21,
        setpoint_clg=24,
        cop_htg_start=0.55,
        cop_htg_stop=3.5,
        cop_htg_num=10,
        cop_clg=5.2,
        hrv_efficiency=0.55,
        u_walls=0.273,
        u_windows=2.56,
        u_roof=0.164,
        test_leakage=2,
        **kwargs):
    default_kwargs = {'clg_pct': 1,
                      'occupant_density': static.necb['occupant_density'],
                      'peak_receptacle_load': static.necb['peak_receptacle_load'],
                      'lpd': static.necb['lpd'],
                      'fraction_occupied': static.necb['fraction_occupied'],
                      'fraction_lighting': static.necb['fraction_lighting'],
                      'fraction_receptacle_load': static.necb['fraction_receptacle_load'],
                      'service_water_heating_load': static.necb['service_water_heating_load'],
                      'mass_level': 'medium'}
    kwargs = {**default_kwargs, **kwargs}

    print(f'Running {cop_htg_num} simulations to determine minimum heating COP\n')

    df = pd.DataFrame(index=np.linspace(cop_htg_start, cop_htg_stop, cop_htg_num), columns=['tedi', 'teui', 'ghgi'])

    for row in df.itertuples():
        sim = simulation.Run(
            name=name,
            province=province,
            gfa=gfa,
            area_walls_ag=area_walls,
            area_windows=area_windows,
            area_roof=area_roof,
            window_groups=window_groups,
            setpoint_htg=setpoint_htg,
            setpoint_clg=setpoint_clg,
            cop_htg=row.Index,
            cop_clg=cop_clg,
            cop_dhw=row.Index,
            hrv_efficiency=hrv_efficiency,
            u_walls=u_walls,
            u_windows=u_windows,
            u_roof=u_roof,
            test_leakage=test_leakage,
            isd_file=None,
            silent=True,
            clg_pct=kwargs['clg_pct'],
            occupant_density=kwargs['occupant_density'],
            peak_receptacle_load=kwargs['peak_receptacle_load'],
            lpd=kwargs['lpd'],
            fraction_occupied=kwargs['fraction_occupied'],
            fraction_lighting=kwargs['fraction_lighting'],
            fraction_receptacle_load=kwargs['fraction_receptacle_load'],
            service_water_heating_load=kwargs['service_water_heating_load'],
            mass_level=kwargs['mass_level'])

        df.at[row.Index, 'tedi'] = np.sum(sim.heating_demand) / sim.gfa
        df.at[row.Index, 'teui'] = np.sum(sim.total_energy_consumption) / sim.gfa
        df.at[row.Index, 'ghgi'] = np.sum(sim.total_ghg_emissions) / sim.gfa

    # Approximate quadratic functions of TEDI/TEUI/GHGI with respect to COP
    f_teui = interp1d(df.index, df.teui, kind='quadratic')
    f_ghgi = interp1d(df.index, df.ghgi, kind='linear')  # linear because of drop off at change from natural gas to electric

    # Approximate functions of U-value with respect to TEDI/TEUI/GHGI
    f_teui_r = interp1d(df.teui, df.index)
    f_ghgi_r = interp1d(df.ghgi, df.index)

    for target in performance_targets:

        # Estimate heating system COP required to meet the TEUI targets
        if target.teui is not None:
            if not (df.teui.min() < target.teui < df.teui.max()):
                raise Exception(f'TEUI target "{target.name}" does not intersect with the interpolated function.'
                                f' Either increase the range of COPs assessed or set this target to None')
            else:
                cop_for_teui = round(float(f_teui_r(target.teui)), 1)
                print(
                    f'To meet the {target.name} TEUI target of {target.teui} kWh/m2yr, the heating system COP should be no less than {cop_for_teui}')
        else:
            cop_for_teui = None

        # Estimate heating system COP required to meet the GHGI targets
        if target.ghgi is not None:
            if not (df.ghgi.min() < target.ghgi < df.ghgi.max()):
                raise Exception(f'GHGI target "{target.name}" does not intersect with the interpolated function.'
                                f' Either increase the range of COPs assessed or set this target to None')
            else:
                cop_for_ghgi = round(float(f_ghgi_r(target.ghgi)), 1)
                print(
                    f'To meet the {target.name} GHGI target of {target.ghgi} kgCO2e/m2yr, the heating system COP should be no less than {cop_for_ghgi}')
        else:
            cop_for_ghgi = None
        print('\n')

    return {"f_teui": f_teui, "f_teui_r": f_teui_r, "f_ghgi": f_ghgi, "f_ghgi_r": f_ghgi_r}
