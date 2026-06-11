"""
The ``simulation`` module contains the main classes needed to run a simulation.
"""


from murb_energy_tool.vec import Vec
from murb_energy_tool import heatbalance, models, solargains, utilities, static
from datetime import datetime


class Run:
    def __init__(self,
                 name,
                 province,
                 gfa,
                 area_walls_ag,
                 area_walls_bg,
                 area_windows,
                 area_roof,
                 window_groups,
                 area_sog=0,
                 perim_exp=0,
                 setpoint_htg=21,
                 setpoint_clg=24,
                 cop_htg=0.85,
                 cop_clg=5.2,
                 cop_dhw=0.85,
                 hrv_efficiency=0.55,
                 u_walls_ag=0.273,
                 u_walls_bg=0.379,
                 f_factor=0.93,
                 u_windows=2.56,
                 u_roof=0.164,
                 test_leakage=2,
                 isd_file=None,
                 epw_path=None,
                 silent=False,
                 **kwargs):
        """

        Parameters
        ----------
        name : str
            Name of the simulation for the results file. Will be appended with "_TMY" or "_ISD" depending on the weather
            data input.
        province : str
            Two letters identifying the Canadian province the building is located in. See static.py for accepted
            abbreviations.
        gfa : float
            Gross floor area. [m2]
        area_walls_ag : float
            Area of the above-grade walls. [m2]
        area_walls_bg : float
            Area of the below-grade walls. [m2]
        area_windows : float
            Area of the windows. [m2]
        area_roof : float
            Area of the roof. [m2]
        area_sog : float
        Area of underground slabs on grade. [m2]
        perim_exp : float
        Perimeter of exposed slabs on grade. [m]
        window_groups : list
            A list of WindowGroup objects.
        setpoint_htg : float, default 21
            Heating system setpoint [C]
        setpoint_clg : float, default 24
            Cooling system setpoint [C]
        cop_htg : float, default 0.85
            Seasonal COP of the space heating plant. Default represents a high efficiency condensing boiler.
        cop_clg : float, default 5.2
            Seasonal COP of the space cooling plant. Default represents a water-cooled centrifugal chiller.
        cop_dhw : float, default 0.85
            Seasonal COP of the domestic hot water plant. Default represents a high efficiency condensing boiler.
        hrv_efficiency : float, default 0.55
            Seasonal heat recovery effectiveness (sensible only). Default is 55% (Ontario Building Code SB-10).
        u_walls_ag : float, default 0.273
            Overall surface-to-surface U-value of the above-grade walls. Do not include surface films. [W/m2K]
        u_walls_bg : float, default 0.379
            Overall surface-to-surface U-value of the below-grade walls. Do not include surface films. [W/m2K]
        f_factor : float
            F-factor for exposed slabs on grade. [W/mK]
        u_windows : float, default 0.273
            Overall surface-to-surface U-value of the above-grade windows. Should be a product U-value which considers
            thermal bridging through the frame. Do not include surface films. [W/m2K]
        u_roof : float, default 0.164
            Overall surface-to-surface U-value of the roof. Do not include surface films. [W/m2K]
        test_leakage : float, default 2
            Air leakage rate at 75 Pa pressure difference. [L/s/m2 exterior area]
            Default of 2 L/s/m2 is recommended by CaGBC ZCB Design v2 Energy Modelling Guidelines.
        isd_file : str, default None
            Filename (including extension) of the ISD file. File should be a .isd located in './input'.
        silent : bool, default False
            Supress printing of the summary metrics.
        kwargs
        """
        default_kwargs = {'clg_pct': 1,  # % of the GFA which is cooled
                          'occupant_density': static.necb['occupant_density'],
                          'peak_receptacle_load': static.necb['peak_receptacle_load'],
                          'lpd': static.necb['lpd'],
                          'fraction_occupied': static.necb['fraction_occupied'],
                          'fraction_lighting': static.necb['fraction_lighting'],
                          'fraction_receptacle_load': static.necb['fraction_receptacle_load'],
                          'service_water_heating_load': static.necb['service_water_heating_load'],
                          'people_outdoor_air_rate': static.ashrae_62['people_outdoor_air_rate'],
                          'area_outdoor_air_rate': static.ashrae_62['area_outdoor_air_rate'],
                          'mass_level': 'medium'}  # Thermal mass
        kwargs = {**default_kwargs, **kwargs}

        if isd_file is not None:
            raise NotImplementedError(
                'ISD support was removed in the pure-Python port; use a TMY EPW.')
        epw, epw_metadata = utilities.process_weather_data(silent=silent, epw_path=epw_path)
        weather_data_monthly = utilities.get_degree_hours_from_weather_data(
            epw, setpoint_htg, setpoint_clg)
        self.name = f'{name}_TMY'

        # Resample the EPW or ISD file to get monthly degree hours and heating/cooling period hours
        hours = weather_data_monthly.hours
        htg_hours = weather_data_monthly.htg_hours
        clg_hours = weather_data_monthly.clg_hours
        htg_degree_hrs = weather_data_monthly.htg_degree_hrs
        clg_degree_hrs = weather_data_monthly.clg_degree_hrs
        htg_degree_hrs_ground = weather_data_monthly.htg_degree_hrs_ground
        clg_degree_hrs_ground = weather_data_monthly.clg_degree_hrs_ground
        htg_degree_hrs_w_clg_setpoint = weather_data_monthly.htg_degree_hrs_w_clg_setpoint
        htg_degree_hrs_w_clg_setpoint_ground = weather_data_monthly.htg_degree_hrs_w_clg_setpoint_ground

        # Check validity of window groups
        if type(window_groups) != list:
            raise Exception('`window_groups` should be a list of window groups!')
        if len(window_groups) < 1:
            raise Exception('You have not assigned any windows!')

        # Calculate the monthly solar gains during each month's heating / cooling period
        solar_gains_tot = solargains.get_solar_gains(window_groups, area_windows, epw)

        # Calculate lighting, service water heating and plug loads
        self.lighting_consumption = models.lighting_energy(gfa, hours, kwargs['lpd'], kwargs['fraction_lighting'])
        self.dhw_htg_consumption = models.domestic_hot_water(gfa, hours, kwargs['occupant_density'], cop_dhw, kwargs['service_water_heating_load'])
        self.plug_loads_consumption = models.plug_loads(gfa, hours, kwargs['peak_receptacle_load'],
                                                        kwargs['fraction_receptacle_load'])

        # Calculate the monthly heating/cooling energy demand
        oa = heatbalance.outdoor_air_rate(gfa, kwargs['people_outdoor_air_rate'], kwargs['area_outdoor_air_rate'], kwargs['occupant_density'])
        self.transmission_heat_losses = heatbalance.transmission(u_walls_ag, u_walls_bg, u_windows, u_roof, f_factor,
                                                                 area_walls_ag, area_walls_bg, area_sog, perim_exp,
                                                                 area_windows, area_roof, htg_degree_hrs,
                                                                 htg_degree_hrs_ground)
        self.transmission_heat_gains = heatbalance.transmission(u_walls_ag, u_walls_bg, u_windows, u_roof, f_factor,
                                                                area_walls_ag, area_walls_bg, area_sog, perim_exp,
                                                                area_windows, area_roof, clg_degree_hrs,
                                                                clg_degree_hrs_ground)
        self.ventilation_heat_losses = heatbalance.ventilation(oa, hrv_efficiency, htg_degree_hrs)
        self.ventilation_heat_gains = heatbalance.ventilation(oa, hrv_efficiency, clg_degree_hrs)

        envelope_area_ag = area_walls_ag + area_windows + area_roof

        self.infiltration_heat_losses = heatbalance.infiltration(test_leakage, envelope_area_ag, htg_degree_hrs)
        self.infiltration_heat_gains = heatbalance.infiltration(test_leakage, envelope_area_ag, clg_degree_hrs)
        self.internal_gains_during_htg = heatbalance.internal_gains(gfa=gfa, hours=htg_hours,
                                                               occupancy=kwargs['occupant_density'],
                                                               fraction_occupied=kwargs['fraction_occupied'],
                                                               lpd=kwargs['lpd'],
                                                               fraction_lighting=kwargs['fraction_lighting'],
                                                               peak_receptacle_load=kwargs['peak_receptacle_load'],
                                                               fraction_receptacle_load=kwargs[
                                                                   'fraction_receptacle_load'])
        self.internal_gains_during_clg = heatbalance.internal_gains(gfa=gfa, hours=clg_hours,
                                                                    occupancy=kwargs['occupant_density'],
                                                                    fraction_occupied=kwargs['fraction_occupied'],
                                                                    lpd=kwargs['lpd'],
                                                                    fraction_lighting=kwargs['fraction_lighting'],
                                                                    peak_receptacle_load=kwargs['peak_receptacle_load'],
                                                                    fraction_receptacle_load=kwargs[
                                                                        'fraction_receptacle_load'])

        # Calculate heat losses using the cooling set-point (I know it seems weird, but that's what RETScreen does)
        transmission_heat_losses_clg = heatbalance.transmission(u_walls_ag, u_walls_bg, u_windows, u_roof, f_factor,
                                                                area_walls_ag, area_walls_bg, area_sog, perim_exp,
                                                                area_windows, area_roof,
                                                                htg_degree_hrs_w_clg_setpoint,
                                                                htg_degree_hrs_w_clg_setpoint_ground)
        ventilation_heat_losses_clg = heatbalance.ventilation(oa, hrv_efficiency, htg_degree_hrs_w_clg_setpoint)
        infiltration_heat_losses_clg = heatbalance.infiltration(test_leakage, envelope_area_ag,
                                                                htg_degree_hrs_w_clg_setpoint)

        # Calculate solar gains utilisation factors
        hl = self.transmission_heat_losses + self.ventilation_heat_losses + self.infiltration_heat_losses
        hl_prime = transmission_heat_losses_clg + ventilation_heat_losses_clg + infiltration_heat_losses_clg
        ig = self.internal_gains_during_htg + self.internal_gains_during_clg
        # Solar gains usable for heating
        f = solargains.utilisation_factors(solar_gains_tot, hl, ig, kwargs['mass_level'])
        utilisation_factor_htg = utilities.set_zero_to_one(f)
        # Solar gains adding to cooling demand
        f_prime = solargains.utilisation_factors(solar_gains_tot, hl_prime, ig, kwargs['mass_level'])
        utilisation_factor_clg = 1 - utilities.set_zero_to_one(f_prime)

        self.f = f  # Assign for diagnostics
        self.f_prime = utilities.set_zero_to_one(f_prime)

        # Re-calculate solar gains
        self.solar_gains_during_htg = utilisation_factor_htg * solar_gains_tot
        self.solar_gains_during_clg = utilisation_factor_clg * solar_gains_tot

        # Sum up heating and cooling demand
        self.heating_demand = utilities.set_zero_below_zero(self.transmission_heat_losses + self.ventilation_heat_losses +
                                             self.infiltration_heat_losses - self.internal_gains_during_htg - self.solar_gains_during_htg)
        cooling_demand = self.transmission_heat_gains + self.ventilation_heat_gains + self.infiltration_heat_gains + self.internal_gains_during_clg + self.solar_gains_during_clg

        self.cooling_demand = cooling_demand * kwargs['clg_pct']  # Prorate cooling demand by conditioned floor area

        # Calculate the monthly space heating/cooling energy use
        self.heating_consumption = models.space_heating_energy_use(self.heating_demand, cop_htg)
        self.cooling_consumption = models.cooling_energy_use(self.cooling_demand, cop_clg)
        self.total_energy_consumption = self.heating_consumption + self.cooling_consumption + self.plug_loads_consumption + self.lighting_consumption + self.dhw_htg_consumption

        # Calculate the monthly gas/electricity energy use
        self.electricity_consumption = self.cooling_consumption + self.plug_loads_consumption + self.lighting_consumption
        self.gas_consumption = Vec.zeros(len(hours))
        if cop_htg < .99:
            self.gas_consumption = self.gas_consumption + self.heating_consumption
        else:
            self.electricity_consumption = self.electricity_consumption + self.heating_consumption
        if cop_dhw < .99:
            self.gas_consumption = self.gas_consumption + self.dhw_htg_consumption
        else:
            self.electricity_consumption = self.electricity_consumption + self.dhw_htg_consumption

        # Calculate the total greenhouse gas emissions
        ghg_electricity = static.ghg_electricity[province]
        ghg_natural_gas = static.ghg_natural_gas[province]
        self.total_ghg_emissions = self.gas_consumption * ghg_natural_gas + self.electricity_consumption * ghg_electricity

        # Inputs
        self.gfa = gfa
        self.area_walls = area_walls_ag
        self.area_roof = area_roof
        self.weather_file = epw_metadata['city']
        if kwargs['fraction_occupied'] == static.necb['fraction_occupied']:
            self.operating_hours = 'NECB Schedule G'
        else:
            self.operating_hours = 'Custom'
        self.occupancy = kwargs['occupant_density']
        self.plug_loads = kwargs['peak_receptacle_load']
        self.ppl_oa = static.ashrae_62['people_outdoor_air_rate']
        self.area_oa = static.ashrae_62['area_outdoor_air_rate']
        self.infiltration = test_leakage
        self.wall_r = u_walls_ag ** -1 * 5.678
        self.roof_r = u_roof ** -1 * 5.678
        self.window_u = u_windows
        self.shgc = str([window.shgc for window in window_groups])
        self.shading = str([window.shading for window in window_groups])
        self.lighting = kwargs['lpd']
        self.heat_recovery = hrv_efficiency * 100
        self.cooling_cop = cop_clg
        self.heating_cop = cop_htg
        self.dhw_load = kwargs['service_water_heating_load']
        self.dhw_plant = cop_dhw
        self.ghg_intensity_electricity = static.ghg_electricity[province]
        self.ghg_intensity_natural_gas = static.ghg_natural_gas[province]

        # Metadata
        self.last_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if not silent:
            print('Done.')


class WindowGroup:
    def __init__(self, pct_window_area, window_azimuth, shgc=0.4, shading=0.):
        self.pct_window_area = pct_window_area
        self.window_azimuth = window_azimuth
        self.shgc = shgc
        self.shading = shading
