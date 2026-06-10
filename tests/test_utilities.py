import json
from pathlib import Path

import pytest

from murb_energy_tool import utilities

GOLDEN = Path(__file__).parent / 'golden'
EPW = GOLDEN / 'data' / 'CAN_AB_CALGARY-INTL-A_3031092_CWEC.epw'
FIX = json.loads((GOLDEN / 'fixtures.json').read_text())


def test_monthly_weather_matches_golden():
    epw, meta = utilities.process_weather_data(silent=True, epw_path=EPW)
    mw = utilities.get_degree_hours_from_weather_data(epw, 21, 24)
    ref = FIX['monthly_weather']
    exact = ('hours', 'htg_hours', 'clg_hours', 'htg_degree_hrs', 'clg_degree_hrs',
             'htg_degree_hrs_ground', 'clg_degree_hrs_ground',
             'htg_degree_hrs_w_clg_setpoint', 'htg_degree_hrs_w_clg_setpoint_ground')
    for col in exact:
        assert getattr(mw, col) == pytest.approx(ref[col], rel=1e-9), col


def test_solar_columns_populated():
    epw, meta = utilities.process_weather_data(silent=True, epw_path=EPW)
    assert len(epw.sun_elevation) == 8760
    assert max(epw.sun_elevation) > 50      # Calgary midsummer noon
    assert min(epw.sun_elevation) < -40


def test_clamps():
    from murb_energy_tool.vec import Vec
    assert utilities.set_zero_below_zero(Vec([-1.0, 0.5])) == [0.0, 0.5]
    assert utilities.set_zero_to_one(Vec([-1.0, 0.5, 2.0])) == [0.0, 0.5, 1.0]
