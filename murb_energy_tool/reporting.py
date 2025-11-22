"""
The ``reporting`` module contains functions for 1) writing a simulation run to an html file, and 2) validating a model
run against a utility bill.
"""

from pathlib import Path
from scipy import stats
import numpy as np
import pandas as pd
from tabulate import tabulate
from murb_energy_tool import static, report_resources
import importlib.resources as pkg_resources


def write_results(run):
    """
Writes an html file containing results and metadata for a single Run object.
The html file will be created in './results'.
    Parameters
    ----------
    run : object
        A Run object produced by murb_energy_tool.simulation
    """
    # Create inputs table
    d = {
        'Floor Area': [run.gfa, 'm2'],
        'Walls Area': [run.area_walls, 'm2'],
        'Roof Area': [run.area_roof, 'm2'],
        'Weather File': [run.weather_file, ''],
        'Operating Hours': [run.operating_hours, ''],
        'Occupancy': [run.occupancy, 'm2/person'],
        'Plug Loads': [run.plug_loads, 'W/m2'],
        'People Outdoor Air': [run.ppl_oa, 'L/s/person'],
        'Area Outdoor Air': [run.area_oa, 'L/s/m2'],
        'Infiltration': [run.infiltration, 'L/s/m2 exterior area @ 75 Pa'],
        'Wall R-value': [round(run.wall_r, 1), 'hr ft2 F/Btu'],
        'Roof R-value': [round(run.roof_r, 1), 'hr ft2 F/Btu'],
        'Window U-value': [run.window_u, 'W/m2K'],
        'Window SHGC': [run.shgc, ''],
        'Shading': [run.shading, '%'],
        'Lighting': [run.lighting, 'W/m2'],
        'Heat Recovery': [run.heat_recovery, '%'],
        'Cooling': [run.cooling_cop, 'COP'],
        'Heating': [run.heating_cop, 'COP'],
        'DHW Load': [run.dhw_load, 'W/person'],
        'DHW Plant': [run.dhw_plant, 'COP'],
        'GHG Intensity - Electricity': [run.ghg_intensity_electricity, 'kgCO2e/kWh'],
        'GHG Intensity - Natural Gas': [round(run.ghg_intensity_natural_gas, 2), 'kgCO2e/kWh']
    }
    df_inputs = pd.DataFrame(data=d, index=['Value', 'Unit']).transpose()

    # Create annual intensities table
    d = {'TEDI heating (kWh/m2)': round(np.sum(run.heating_demand) / run.gfa, 1),
         'TEDI cooling (kWh/m2)': round(np.sum(run.cooling_demand) / run.gfa, 1),
         'TEUI (kWh/m2)': round(np.sum(run.total_energy_consumption) / run.gfa, 1),
         'GHGI (kgCO2e/m2)': round(np.sum(run.total_ghg_emissions) / run.gfa, 1)}
    df_annual_intensities = pd.DataFrame(index=['Annual'], data=d)

    # Create annual thermal demand breakdowns
    d = {'Transmission': [round(np.sum(run.transmission_heat_losses) / run.gfa, 1),
                          round(np.sum(run.transmission_heat_gains) / run.gfa, 1)],
         'Ventilation': [round(np.sum(run.ventilation_heat_losses) / run.gfa, 1),
                         round(np.sum(run.ventilation_heat_gains) / run.gfa, 1)],
         'Infiltration': [round(np.sum(run.infiltration_heat_losses) / run.gfa, 1),
                          round(np.sum(run.infiltration_heat_gains) / run.gfa, 1)],
         'Internal Gains': [np.nan, round(np.sum(run.internal_gains_during_clg) / run.gfa, 1)],
         'Solar Gains': [np.nan, round(np.sum(run.solar_gains_during_clg) / run.gfa, 2)]}
    df_annual_thermal_breakdown = pd.DataFrame(index=['Heating (kWh/m2)', 'Cooling (kWh/m2)'], data=d)

    # Create monthly thermal demand table
    d = {'Heating (kWh)': run.heating_demand.astype('int'),
         'Cooling (kWh)': run.cooling_demand.astype('int')}
    df_monthly_thermal_demand = pd.DataFrame(index=pd.date_range('2021-01-01', periods=12, freq='M').month_name(),
                                             data=d)

    # Create annual end use breakdown
    d = {'Lighting': round(np.sum(run.lighting_consumption) / run.gfa, 1),
         'Space Heating': round(np.sum(run.heating_consumption) / run.gfa, 1),
         'Space Cooling': round(np.sum(run.cooling_consumption) / run.gfa, 1),
         'Service Water Heating': round(np.sum(run.dhw_htg_consumption) / run.gfa, 1),
         'Plug Loads': round(np.sum(run.plug_loads_consumption) / run.gfa, 1)}
    df_annual_end_use_breakdown = pd.DataFrame(index=['Annual (kWh/m2)'], data=d)

    # Create monthly end use table
    d = {'Lighting (kWh)': run.lighting_consumption.astype('int'),
         'Space Heating (kWh)': run.heating_consumption.astype('int'),
         'Space Cooling (kWh)': run.cooling_consumption.astype('int'),
         'Service Water Heating (kWh)': run.dhw_htg_consumption.astype('int'),
         'Plug Loads (kWh)': run.plug_loads_consumption.astype('int')}
    df_monthly_end_use = pd.DataFrame(index=pd.date_range('2021-01-01', periods=12, freq='M').month_name(), data=d)

    # Create monthly electricity / gas table
    d = {'Electricity (kWh)': run.electricity_consumption.astype('int'),
         'Gas (kWh)': run.gas_consumption.astype('int'),
         'Gas (m3)': (run.gas_consumption/static.constants['ed_gas']).astype('int')}
    df_monthly_gas_electricity = pd.DataFrame(index=pd.date_range('2021-01-01', periods=12, freq='M').month_name(),
                                              data=d)

    # Make output folders
    out_dir = Path(f'results/{run.name}/javascript')
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write all tables into js file
    tables = {
        'inputs': df_inputs,
        'annual_intensities': df_annual_intensities,
        'annual_thermal_breakdown': df_annual_thermal_breakdown,
        'monthly_thermal_demand': df_monthly_thermal_demand,
        'annual_end_use_breakdown': df_annual_end_use_breakdown,
        'monthly_end_use': df_monthly_end_use,
        'monthly_gas_electricity': df_monthly_gas_electricity
    }
    f = open(out_dir / 'tables.js', 'w')
    for key, value in tables.items():
        f.write(f"document.getElementById('{key}').innerHTML = `\n")
        f.write(value.to_html(justify="center"))
        f.write("`;\n")
    f.close()

    # Write metadata into another js file
    f = open(out_dir / 'metadata.js', 'w')
    f.write(f"document.getElementById('run_name').innerHTML = '{run.name}'\n")
    f.write(f"document.getElementById('last_updated').innerHTML = '{run.last_updated}'")

    # Copy the html package included with this package
    skeleton = pkg_resources.read_text(report_resources, 'skeleton.html')
    f = open(out_dir.parent / f'{run.name}.html', 'w')
    f.write(skeleton)
    f.close()

    print(df_annual_intensities.to_markdown(tablefmt='grid', stralign='center', numalign='center'))


def validate(electricity_consumption, gas_consumption, utility_data, silent=False):
    """
Compares simulated electricity and gas consumption to measured electricity and gas consumption. Returns prediction
accuracy metrics: r-squared & mean absolute error.

Measured utility data should be in the form of a CSV located in './input'. The first row should have the labels
'electricity' and 'gas'. 12 rows should follow for each month. Consumption should be given in kWh.
    Parameters
    ----------
    electricity_consumption : array
        electricity_consumption attribute of a simulation Run object.
    gas_consumption : array
        gas_consumption attribute of a simulation Run object.
    utility_data : str
        Filename (including extension) of the utility data. File should be a CSV located in './input'.
    silent : bool, default False
        Supress printing of the statistical metrics.
    Returns
    -------
        r2_electricity, r2_gas, mae_electricity, mae_gas
    """
    p = list(Path('input').glob(utility_data))
    df = pd.read_csv(p[0], index_col=False, dtype='float')

    r2_electricity = round(stats.linregress(electricity_consumption, df['electricity'])[2]**2, 2)
    r2_gas = round(stats.linregress(gas_consumption, df['gas'])[2] ** 2, 2)

    mae_electricity = int(np.mean(abs(electricity_consumption - df['electricity'])))
    mae_gas = int(np.mean(abs(gas_consumption - df['gas'])))

    d = {'Electricity': [r2_electricity, mae_electricity],
         'Natural Gas': [r2_gas, mae_gas]}
    df_validation = pd.DataFrame(index=['R-squared', 'MAE'], data=d)
    if not silent:
        print(df_validation.to_markdown(tablefmt='grid', stralign='center', numalign='center'))
    return r2_electricity, r2_gas, mae_electricity, mae_gas
