import json
from pathlib import Path

import pytest

from murb_energy_tool.epw import read_epw

GOLDEN = Path(__file__).parent / 'golden'
EPW = GOLDEN / 'data' / 'CAN_AB_CALGARY-INTL-A_3031092_CWEC.epw'
FIX = json.loads((GOLDEN / 'fixtures.json').read_text())


def test_metadata_matches_pvlib():
    data, meta = read_epw(EPW)
    ref = FIX['epw_meta']
    assert meta['latitude'] == pytest.approx(ref['latitude'])
    assert meta['longitude'] == pytest.approx(ref['longitude'])
    assert meta['TZ'] == pytest.approx(ref['TZ'])
    assert meta['altitude'] == pytest.approx(ref['altitude'])
    assert meta['city'] == ref['city']


def test_first_72_hours_match_pvlib():
    data, _ = read_epw(EPW)
    for col in ('temp_air', 'ghi', 'dni', 'dhi'):
        assert getattr(data, col)[:72] == pytest.approx(FIX['epw_head'][col])


def test_annual_sums_and_shape():
    data, _ = read_epw(EPW)
    assert len(data.temp_air) == 8760
    assert data.month[0] == 1 and data.month[-1] == 12
    for col in ('temp_air', 'ghi', 'dni', 'dhi'):
        assert sum(getattr(data, col)) == pytest.approx(FIX['epw_annual_sums'][col], rel=1e-9)


def test_monthly_sum_buckets():
    data, _ = read_epw(EPW)
    hours = data.monthly_sum([1.0] * 8760)
    assert hours == [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
