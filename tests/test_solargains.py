import json
from pathlib import Path

import pytest

from murb_energy_tool import solargains, utilities
from murb_energy_tool.vec import Vec

GOLDEN = Path(__file__).parent / 'golden'
EPW = GOLDEN / 'data' / 'CAN_AB_CALGARY-INTL-A_3031092_CWEC.epw'
GOLD = json.loads((GOLDEN / 'goldens.json').read_text())


class WG:
    def __init__(self, pct, az, shgc=0.4, shading=0.0):
        self.pct_window_area = pct
        self.window_azimuth = az
        self.shgc = shgc
        self.shading = shading


def test_solar_gains_south_sanity():
    # baseline_gas golden used one south group, area 1800, shgc .4, shading 0.
    # Reconstruct its solar gains from frozen run outputs:
    # solar_gains_during_htg/f gives the pre-utilisation total only when f==1,
    # so instead compare against an independent legacy capture: the
    # 'four_orient' scenario exercises 4 azimuths through full Run parity in
    # test_simulation_parity.py. Here, test physical sanity bounds.
    epw, _ = utilities.process_weather_data(silent=True, epw_path=EPW)
    q = solargains.get_solar_gains([WG(1.0, 180)], 1800.0, epw)
    assert isinstance(q, Vec) and len(q) == 12
    assert all(v > 0 for v in q)
    assert q[11] > q[5]   # vertical south glazing in Calgary: winter beam > summer


def test_utilisation_factors_unchanged_api():
    f = solargains.utilisation_factors(Vec([10.0] * 12), Vec([100.0] * 12),
                                       Vec([20.0] * 12), 'medium')
    assert len(f) == 12 and all(0 < x <= 1.2 for x in f)
