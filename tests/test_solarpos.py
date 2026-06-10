import json
from pathlib import Path

from murb_energy_tool.epw import read_epw
from murb_energy_tool.solarpos import solar_position

GOLDEN = Path(__file__).parent / 'golden'
FIX = json.loads((GOLDEN / 'fixtures.json').read_text())


def test_sampled_hours_match_pvlib():
    data, meta = read_epw(GOLDEN / 'data' / 'CAN_AB_CALGARY-INTL-A_3031092_CWEC.epw')
    sp = FIX['solpos_samples']
    max_elev_err, max_az_err = 0.0, 0.0
    for j, i in enumerate(sp['index']):
        elev, az = solar_position(
            data.year[i], data.month[i], data.day[i], data.hour[i],
            meta['TZ'], meta['latitude'], meta['longitude'])
        max_elev_err = max(max_elev_err, abs(elev - sp['elevation'][j]))
        if sp['elevation'][j] > 0:   # azimuth meaningless at night
            d = abs(az - sp['azimuth'][j]) % 360
            max_az_err = max(max_az_err, min(d, 360 - d))
    assert max_elev_err < 0.5, max_elev_err
    assert max_az_err < 1.0, max_az_err
