"""Generate golden-master outputs from the CURRENT (numpy/pvlib) implementation.

Run ONLY under .venv-legacy, BEFORE the port begins:
    cd ~/code/murb && .venv-legacy/bin/python tests/golden/generate_goldens.py
Commit the resulting JSON. Never regenerate after porting starts.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
EPW_NAME = 'CAN_AB_CALGARY-INTL-A_3031092_CWEC.epw'

BASE = dict(name='golden', province='AB', gfa=12000.0, area_walls_ag=4200.0,
            area_walls_bg=0.0, area_windows=1800.0, area_roof=1100.0,
            silent=True)

WG4 = [dict(pct_window_area=0.30, window_azimuth=0, shgc=0.40, shading=0.0),
       dict(pct_window_area=0.20, window_azimuth=90, shgc=0.40, shading=0.10),
       dict(pct_window_area=0.35, window_azimuth=180, shgc=0.30, shading=0.20),
       dict(pct_window_area=0.15, window_azimuth=270, shgc=0.40, shading=0.10)]
WG1 = [dict(pct_window_area=1.0, window_azimuth=180, shgc=0.40, shading=0.0)]

SCENARIOS = {
    'baseline_gas':    {**BASE, 'wg': WG1},
    'four_orient':     {**BASE, 'wg': WG4, 'area_windows': 2600.0},
    'all_electric_hp': {**BASE, 'wg': WG1, 'cop_htg': 3.0, 'cop_dhw': 2.5, 'cop_clg': 4.0},
    'low_mass':        {**BASE, 'wg': WG1, 'mass_level': 'low'},
    'half_cooled':     {**BASE, 'wg': WG1, 'clg_pct': 0.5},
    'below_grade':     {**BASE, 'wg': WG1, 'area_walls_bg': 900.0, 'area_sog': 950.0,
                        'perim_exp': 120.0, 'u_walls_bg': 0.35, 'f_factor': 0.9},
}

RUN_OUTPUTS = ['heating_demand', 'cooling_demand', 'heating_consumption',
               'cooling_consumption', 'lighting_consumption', 'dhw_htg_consumption',
               'plug_loads_consumption', 'total_energy_consumption',
               'electricity_consumption', 'gas_consumption', 'total_ghg_emissions',
               'transmission_heat_losses', 'transmission_heat_gains',
               'ventilation_heat_losses', 'ventilation_heat_gains',
               'infiltration_heat_losses', 'infiltration_heat_gains',
               'internal_gains_during_htg', 'internal_gains_during_clg',
               'solar_gains_during_htg', 'solar_gains_during_clg']


def run_in_tempdir(fn):
    """murb globs ./input/*.epw — give it a temp cwd with exactly one EPW."""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'input').mkdir()
        shutil.copy(HERE / 'data' / EPW_NAME, Path(td) / 'input' / EPW_NAME)
        try:
            os.chdir(td)
            return fn()
        finally:
            os.chdir(cwd)


def main():
    import pvlib.iotools
    import pvlib.solarposition
    from scipy.interpolate import interp1d
    from murb_energy_tool import simulation, utilities

    goldens, fixtures = {}, {}

    # ---- full-run goldens ----
    for label, sc in SCENARIOS.items():
        sc = dict(sc)
        wg = [simulation.WindowGroup(**w) for w in sc.pop('wg')]

        def go():
            return simulation.Run(window_groups=wg, **sc)
        run = run_in_tempdir(go)
        goldens[label] = {k: list(np.asarray(getattr(run, k), dtype=float))
                          for k in RUN_OUTPUTS}
        goldens[label]['tedi'] = float(np.sum(run.heating_demand) / run.gfa)
        goldens[label]['teui'] = float(np.sum(run.total_energy_consumption) / run.gfa)
        goldens[label]['ghgi'] = float(np.sum(run.total_ghg_emissions) / run.gfa)

    # ---- module fixtures ----
    epw, meta = pvlib.iotools.read_epw(HERE / 'data' / EPW_NAME, coerce_year=2021)
    fixtures['epw_meta'] = {k: meta[k] for k in ('latitude', 'longitude', 'TZ', 'altitude', 'city')}
    fixtures['epw_head'] = {c: [float(v) for v in epw[c].values[:72]] for c in ('temp_air', 'ghi', 'dni', 'dhi')}
    fixtures['epw_annual_sums'] = {c: float(epw[c].sum()) for c in ('temp_air', 'ghi', 'dni', 'dhi')}

    sp = pvlib.solarposition.get_solarposition(
        epw.index, meta['latitude'], meta['longitude'], meta['altitude'])
    idx = list(range(0, 8760, 97))  # ~91 samples across the year, all hours of day
    fixtures['solpos_samples'] = {
        'index': idx,
        'timestamps': [str(epw.index[i]) for i in idx],
        'elevation': [float(sp.elevation.values[i]) for i in idx],
        'azimuth': [float(sp.azimuth.values[i]) for i in idx]}

    # degree-hours fixture (setpoints 21/24, the defaults)
    def degree_hours():
        e, m = pvlib.iotools.read_epw(Path('input') / EPW_NAME, coerce_year=2021)
        return utilities.get_degree_hours_from_weather_data(e, 21, 24)
    mw = run_in_tempdir(degree_hours)
    fixtures['monthly_weather'] = {c: list(np.asarray(mw[c].values, dtype=float))
                                   for c in mw.columns}

    # interp fixture: quadratic + linear samples from scipy on a known curve
    xs = list(np.linspace(0.1, 2.8, 10))
    ys = [round(3.0 + 40.0 * x - 2.0 * x ** 2, 6) for x in xs]
    probe = list(np.linspace(0.15, 2.75, 23))
    fixtures['interp'] = {
        'xs': xs, 'ys': ys, 'probe': probe,
        'quadratic': [float(v) for v in interp1d(xs, ys, kind='quadratic')(probe)],
        'linear': [float(v) for v in interp1d(xs, ys)(probe)]}

    (HERE / 'goldens.json').write_text(json.dumps(goldens, indent=1))
    (HERE / 'fixtures.json').write_text(json.dumps(fixtures, indent=1))
    print(f'Wrote {len(goldens)} scenarios and {len(fixtures)} fixture groups.')


if __name__ == '__main__':
    main()
