import os
import tempfile
from pathlib import Path

import pytest

from murb_energy_tool import reporting
from murb_energy_tool.vec import Vec


def test_linregress_r2_matches_known_values():
    # y = 2x + 1 exactly -> r^2 == 1
    assert reporting._r_squared([1, 2, 3, 4], [3, 5, 7, 9]) == pytest.approx(1.0)
    # constant-ish noise: Pearson r for [1,2,3,4],[2,1,4,3] is 0.6 -> r^2 == 0.36
    # (original comment claimed 0.45 but that is incorrect)
    assert reporting._r_squared([1, 2, 3, 4], [2, 1, 4, 3]) == pytest.approx(0.36)


def test_html_table_shape():
    html = reporting._html_table(['A', 'B'], [['r1', 1], ['r2', 2]], index=['x', 'y'])
    assert html.count('<tr') == 3            # header + 2 rows
    assert '<th>A</th>' in html and '<td>1</td>' in html


class FakeRun:
    """Minimal Run double with 12-month Vecs and the scalar inputs
    write_results reads."""
    def __init__(self):
        twelve = Vec([float(i + 1) for i in range(12)])
        for k in ('heating_demand', 'cooling_demand', 'heating_consumption',
                  'cooling_consumption', 'lighting_consumption',
                  'dhw_htg_consumption', 'plug_loads_consumption',
                  'total_energy_consumption', 'electricity_consumption',
                  'gas_consumption', 'total_ghg_emissions',
                  'transmission_heat_losses', 'transmission_heat_gains',
                  'ventilation_heat_losses', 'ventilation_heat_gains',
                  'infiltration_heat_losses', 'infiltration_heat_gains',
                  'internal_gains_during_clg', 'solar_gains_during_clg'):
            setattr(self, k, twelve)
        self.name = 'fake_TMY'
        self.gfa = 1000.0
        self.area_walls = 400.0
        self.area_roof = 100.0
        self.weather_file = 'Calgary'
        self.operating_hours = 'NECB Schedule G'
        self.occupancy = 28.0
        self.plug_loads = 5.0
        self.ppl_oa = 2.5
        self.area_oa = 0.3
        self.infiltration = 2.0
        self.wall_r = 20.0
        self.roof_r = 35.0
        self.window_u = 1.4
        self.shgc = '[0.4]'
        self.shading = '[0.0]'
        self.lighting = 5.0
        self.heat_recovery = 55.0
        self.cooling_cop = 5.2
        self.heating_cop = 0.85
        self.dhw_load = 60.0
        self.dhw_plant = 0.85
        self.ghg_intensity_electricity = 0.59
        self.ghg_intensity_natural_gas = 0.18
        self.last_updated = '01/01/2026 00:00:00'


def test_write_results_produces_artifacts():
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        try:
            os.chdir(td)
            reporting.write_results(FakeRun())
            out = Path('results/fake_TMY')
            assert (out / 'fake_TMY.html').exists()
            tables = (out / 'javascript' / 'tables.js').read_text()
            for table_id in ('inputs', 'annual_intensities', 'annual_thermal_breakdown',
                             'monthly_thermal_demand', 'annual_end_use_breakdown',
                             'monthly_end_use', 'monthly_gas_electricity'):
                assert f"getElementById('{table_id}')" in tables
            assert 'January' in tables and 'December' in tables
        finally:
            os.chdir(cwd)
