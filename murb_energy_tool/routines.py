"""
The ``routines`` module contains functions for commonly requested feasibility analysis.
"""

from murb_energy_tool import static, simulation
from murb_energy_tool.interp import interp_linear, interp_quadratic


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

    step = (u_facade_stop - u_facade_start) / (u_facade_num - 1)
    u_values = [u_facade_start + i * step for i in range(u_facade_num)]
    tedi, teui, ghgi = [], [], []

    for u in u_values:
        sim = simulation.Run(
            name=name,
            province=province,
            gfa=gfa,
            area_walls_ag=area_walls,
            area_walls_bg=0.0,
            area_windows=area_windows,
            area_roof=area_roof,
            window_groups=window_groups,
            setpoint_htg=setpoint_htg,
            setpoint_clg=setpoint_clg,
            cop_htg=cop_htg,
            cop_clg=cop_clg,
            cop_dhw=cop_dhw,
            hrv_efficiency=hrv_efficiency,
            u_walls=u,            # NOTE: pre-existing bug preserved for parity —
            u_windows=u,          # u_walls lands in **kwargs and is ignored;
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

        tedi.append(sum(sim.heating_demand) / sim.gfa)
        teui.append(sum(sim.total_energy_consumption) / sim.gfa)
        ghgi.append(sum(sim.total_ghg_emissions) / sim.gfa)

    # Approximate quadratic functions of TEDI/TEUI/GHGI with respect to U-value
    f_tedi = interp_quadratic(u_values, tedi)
    f_teui = interp_quadratic(u_values, teui)
    f_ghgi = interp_quadratic(u_values, ghgi)

    # Approximate functions of U-value with respect to TEDI/TEUI/GHGI
    f_tedi_r = interp_linear(tedi, u_values)
    f_teui_r = interp_linear(teui, u_values)
    f_ghgi_r = interp_linear(ghgi, u_values)

    for target in performance_targets:

        # Estimate facade U-value required to meet the TEDI targets
        if target.tedi is not None:
            if not (min(tedi) < target.tedi < max(tedi)):
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
            if not (min(teui) < target.teui < max(teui)):
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
            if not (min(ghgi) < target.ghgi < max(ghgi)):
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

    step = (cop_htg_stop - cop_htg_start) / (cop_htg_num - 1)
    cop_values = [cop_htg_start + i * step for i in range(cop_htg_num)]
    tedi, teui, ghgi = [], [], []

    for c in cop_values:
        sim = simulation.Run(
            name=name,
            province=province,
            gfa=gfa,
            area_walls_ag=area_walls,
            area_walls_bg=0.0,
            area_windows=area_windows,
            area_roof=area_roof,
            window_groups=window_groups,
            setpoint_htg=setpoint_htg,
            setpoint_clg=setpoint_clg,
            cop_htg=c,
            cop_clg=cop_clg,
            cop_dhw=c,
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

        tedi.append(sum(sim.heating_demand) / sim.gfa)
        teui.append(sum(sim.total_energy_consumption) / sim.gfa)
        ghgi.append(sum(sim.total_ghg_emissions) / sim.gfa)

    # Approximate quadratic functions of TEDI/TEUI/GHGI with respect to COP
    f_teui = interp_quadratic(cop_values, teui)
    f_ghgi = interp_linear(cop_values, ghgi)  # linear because of drop off at change from natural gas to electric

    # Approximate functions of U-value with respect to TEDI/TEUI/GHGI
    f_teui_r = interp_linear(teui, cop_values)
    f_ghgi_r = interp_linear(ghgi, cop_values)

    for target in performance_targets:

        # Estimate heating system COP required to meet the TEUI targets
        if target.teui is not None:
            if not (min(teui) < target.teui < max(teui)):
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
            if not (min(ghgi) < target.ghgi < max(ghgi)):
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
