"""Writes an html results file for a Run, and validates a run against
utility bills. Pure-Python replacement for the pandas/scipy version; the
generated HTML tables match pandas' to_html structure closely enough for
the bundled report skeleton."""
import calendar
import csv
from pathlib import Path

from tabulate import tabulate
from murb_energy_tool import static, report_resources
import importlib.resources as pkg_resources

MONTHS = list(calendar.month_name)[1:]  # January..December


def _html_table(headers, rows, index=None, index_name=''):
    """Minimal pandas-to_html-alike: <table> with a header row and optional
    row labels rendered as <th>."""
    out = ['<table border="1" class="dataframe">', '<thead><tr style="text-align: center;">']
    out.append('<th>%s</th>' % index_name if index is not None else '')
    out.extend('<th>%s</th>' % h for h in headers)
    out.append('</tr></thead><tbody>')
    for i, row in enumerate(rows):
        out.append('<tr>')
        if index is not None:
            out.append('<th>%s</th>' % index[i])
        out.extend('<td>%s</td>' % ('' if c is None else c) for c in row)
        out.append('</tr>')
    out.append('</tbody></table>')
    return ''.join(out)


def _annual(series, gfa, ndigits=1):
    return round(sum(series) / gfa, ndigits)


def write_results(run):
    """Writes './results/{run.name}/{run.name}.html' + javascript data files.
    Same artifact layout as the pandas version (webapp depends on it)."""
    inputs_rows = [
        ('Floor Area', run.gfa, 'm2'),
        ('Walls Area', run.area_walls, 'm2'),
        ('Roof Area', run.area_roof, 'm2'),
        ('Weather File', run.weather_file, ''),
        ('Operating Hours', run.operating_hours, ''),
        ('Occupancy', run.occupancy, 'm2/person'),
        ('Plug Loads', run.plug_loads, 'W/m2'),
        ('People Outdoor Air', run.ppl_oa, 'L/s/person'),
        ('Area Outdoor Air', run.area_oa, 'L/s/m2'),
        ('Infiltration', run.infiltration, 'L/s/m2 exterior area @ 75 Pa'),
        ('Wall R-value', round(run.wall_r, 1), 'hr ft2 F/Btu'),
        ('Roof R-value', round(run.roof_r, 1), 'hr ft2 F/Btu'),
        ('Window U-value', run.window_u, 'W/m2K'),
        ('Window SHGC', run.shgc, ''),
        ('Shading', run.shading, '%'),
        ('Lighting', run.lighting, 'W/m2'),
        ('Heat Recovery', run.heat_recovery, '%'),
        ('Cooling', run.cooling_cop, 'COP'),
        ('Heating', run.heating_cop, 'COP'),
        ('DHW Load', run.dhw_load, 'W/person'),
        ('DHW Plant', run.dhw_plant, 'COP'),
        ('GHG Intensity - Electricity', run.ghg_intensity_electricity, 'kgCO2e/kWh'),
        ('GHG Intensity - Natural Gas', round(run.ghg_intensity_natural_gas, 2), 'kgCO2e/kWh'),
    ]
    tables = {}
    tables['inputs'] = _html_table(
        ['Value', 'Unit'], [[v, u] for _, v, u in inputs_rows],
        index=[n for n, _, _ in inputs_rows])

    annual_headers = ['TEDI heating (kWh/m2)', 'TEDI cooling (kWh/m2)',
                      'TEUI (kWh/m2)', 'GHGI (kgCO2e/m2)']
    annual_values = [_annual(run.heating_demand, run.gfa),
                     _annual(run.cooling_demand, run.gfa),
                     _annual(run.total_energy_consumption, run.gfa),
                     _annual(run.total_ghg_emissions, run.gfa)]
    tables['annual_intensities'] = _html_table(annual_headers, [annual_values],
                                               index=['Annual'])

    tables['annual_thermal_breakdown'] = _html_table(
        ['Transmission', 'Ventilation', 'Infiltration', 'Internal Gains', 'Solar Gains'],
        [[_annual(run.transmission_heat_losses, run.gfa),
          _annual(run.ventilation_heat_losses, run.gfa),
          _annual(run.infiltration_heat_losses, run.gfa), None, None],
         [_annual(run.transmission_heat_gains, run.gfa),
          _annual(run.ventilation_heat_gains, run.gfa),
          _annual(run.infiltration_heat_gains, run.gfa),
          _annual(run.internal_gains_during_clg, run.gfa),
          _annual(run.solar_gains_during_clg, run.gfa, 2)]],
        index=['Heating (kWh/m2)', 'Cooling (kWh/m2)'])

    tables['monthly_thermal_demand'] = _html_table(
        ['Heating (kWh)', 'Cooling (kWh)'],
        [[int(run.heating_demand[m]), int(run.cooling_demand[m])] for m in range(12)],
        index=MONTHS)

    tables['annual_end_use_breakdown'] = _html_table(
        ['Lighting', 'Space Heating', 'Space Cooling', 'Service Water Heating', 'Plug Loads'],
        [[_annual(run.lighting_consumption, run.gfa),
          _annual(run.heating_consumption, run.gfa),
          _annual(run.cooling_consumption, run.gfa),
          _annual(run.dhw_htg_consumption, run.gfa),
          _annual(run.plug_loads_consumption, run.gfa)]],
        index=['Annual (kWh/m2)'])

    tables['monthly_end_use'] = _html_table(
        ['Lighting (kWh)', 'Space Heating (kWh)', 'Space Cooling (kWh)',
         'Service Water Heating (kWh)', 'Plug Loads (kWh)'],
        [[int(run.lighting_consumption[m]), int(run.heating_consumption[m]),
          int(run.cooling_consumption[m]), int(run.dhw_htg_consumption[m]),
          int(run.plug_loads_consumption[m])] for m in range(12)],
        index=MONTHS)

    ed_gas = static.constants['ed_gas']
    tables['monthly_gas_electricity'] = _html_table(
        ['Electricity (kWh)', 'Gas (kWh)', 'Gas (m3)'],
        [[int(run.electricity_consumption[m]), int(run.gas_consumption[m]),
          int(run.gas_consumption[m] / ed_gas)] for m in range(12)],
        index=MONTHS)

    out_dir = Path(f'results/{run.name}/javascript')
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / 'tables.js', 'w') as f:
        for key, html in tables.items():
            f.write(f"document.getElementById('{key}').innerHTML = `\n{html}`;\n")
    with open(out_dir / 'metadata.js', 'w') as f:
        f.write(f"document.getElementById('run_name').innerHTML = '{run.name}'\n")
        f.write(f"document.getElementById('last_updated').innerHTML = '{run.last_updated}'")
    skeleton = pkg_resources.read_text(report_resources, 'skeleton.html')
    with open(out_dir.parent / f'{run.name}.html', 'w') as f:
        f.write(skeleton)

    print(tabulate([annual_values], headers=annual_headers, tablefmt='grid',
                   stralign='center', numalign='center'))


def _r_squared(x, y):
    n = float(len(x))
    sx, sy = sum(x), sum(y)
    sxx = sum(a * a for a in x)
    syy = sum(b * b for b in y)
    sxy = sum(a * b for a, b in zip(x, y))
    denom = (n * sxx - sx * sx) * (n * syy - sy * sy)
    if denom <= 0:
        return 0.0
    r = (n * sxy - sx * sy) / denom ** 0.5
    return r * r


def validate(electricity_consumption, gas_consumption, utility_data, silent=False):
    """Compares simulated vs measured monthly consumption (CSV in ./input
    with 'electricity' and 'gas' columns, 12 rows, kWh).
    Returns r2_electricity, r2_gas, mae_electricity, mae_gas."""
    p = list(Path('input').glob(utility_data))
    with open(p[0]) as f:
        rows = list(csv.DictReader(f))
    elec_meas = [float(r['electricity']) for r in rows]
    gas_meas = [float(r['gas']) for r in rows]

    r2_electricity = round(_r_squared(electricity_consumption, elec_meas), 2)
    r2_gas = round(_r_squared(gas_consumption, gas_meas), 2)
    mae_electricity = int(sum(abs(a - b) for a, b in zip(electricity_consumption, elec_meas))
                          / len(elec_meas))
    mae_gas = int(sum(abs(a - b) for a, b in zip(gas_consumption, gas_meas)) / len(gas_meas))

    if not silent:
        print(tabulate([['R-squared', r2_electricity, r2_gas],
                        ['MAE', mae_electricity, mae_gas]],
                       headers=['', 'Electricity', 'Natural Gas'], tablefmt='grid'))
    return r2_electricity, r2_gas, mae_electricity, mae_gas
