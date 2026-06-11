import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from murb_energy_tool import simulation

GOLDEN = Path(__file__).parent / 'golden'
EPW_NAME = 'CAN_AB_CALGARY-INTL-A_3031092_CWEC.epw'
GOLD = json.loads((GOLDEN / 'goldens.json').read_text())

# Mirror of tests/golden/generate_goldens.py SCENARIOS — keep in sync by hand.
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

# Solar position was reimplemented -> every series downstream of solar gains
# gets the 1% band; series with no solar dependence must be near-exact.
SOLAR_TOUCHED = {'heating_demand', 'cooling_demand', 'heating_consumption',
                 'cooling_consumption', 'total_energy_consumption',
                 'electricity_consumption', 'gas_consumption',
                 'total_ghg_emissions', 'solar_gains_during_htg',
                 'solar_gains_during_clg'}


@pytest.mark.parametrize('label', list(SCENARIOS))
def test_run_parity(label):
    sc = dict(SCENARIOS[label])
    wg = [simulation.WindowGroup(**w) for w in sc.pop('wg')]
    run = simulation.Run(window_groups=wg,
                         epw_path=GOLDEN / 'data' / EPW_NAME, **sc)
    ref = GOLD[label]
    for key, expected in ref.items():
        if key in ('tedi', 'teui', 'ghgi'):
            continue
        got = list(getattr(run, key))
        if key in SOLAR_TOUCHED:
            annual_ref, annual_got = sum(expected), sum(got)
            assert annual_got == pytest.approx(annual_ref, rel=0.01, abs=1.0), key
            for m in range(12):
                assert got[m] == pytest.approx(expected[m], rel=0.02, abs=50.0), (key, m)
        else:
            assert got == pytest.approx(expected, rel=1e-4), key
    assert sum(run.heating_demand) / run.gfa == pytest.approx(ref['tedi'], rel=0.01)
    assert sum(run.total_energy_consumption) / run.gfa == pytest.approx(ref['teui'], rel=0.01)
    assert sum(run.total_ghg_emissions) / run.gfa == pytest.approx(ref['ghgi'], rel=0.01)


def test_legacy_input_glob_still_works():
    """The webapp chdirs into a temp dir with input/<epw> — must keep working."""
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'input').mkdir()
        shutil.copy(GOLDEN / 'data' / EPW_NAME, Path(td) / 'input' / EPW_NAME)
        try:
            os.chdir(td)
            run = simulation.Run(window_groups=[simulation.WindowGroup(1.0, 180)],
                                 **{k: v for k, v in BASE.items()})
            assert sum(run.heating_demand) > 0
        finally:
            os.chdir(cwd)


def test_isd_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        simulation.Run(window_groups=[simulation.WindowGroup(1.0, 180)],
                       isd_file='something.isd', **{k: v for k, v in BASE.items()})
