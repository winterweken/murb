import os
import shutil
import tempfile
from pathlib import Path

from murb_energy_tool import routines, simulation

GOLDEN = Path(__file__).parent / 'golden'
EPW_NAME = 'CAN_AB_CALGARY-INTL-A_3031092_CWEC.epw'


def test_facade_sweep_runs_and_interp_is_monotone_sane():
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        (Path(td) / 'input').mkdir()
        shutil.copy(GOLDEN / 'data' / EPW_NAME, Path(td) / 'input' / EPW_NAME)
        try:
            os.chdir(td)
            wg = [simulation.WindowGroup(1.0, 180)]
            targets = [routines.PerformanceTarget('test', tedi=None, teui=None, ghgi=None)]
            out = routines.minimum_facade_performance(
                'sweep', 'AB', gfa=12000.0, area_walls=4200.0, area_windows=1800.0,
                area_roof=1100.0, window_groups=wg, performance_targets=targets,
                u_facade_num=4)
            # Higher window U => more heating demand: f_tedi increasing.
            assert out['f_tedi'](2.5) > out['f_tedi'](0.3)
            # Reverse interp inverts forward interp to within a step.
            mid_tedi = out['f_tedi'](1.0)
            assert abs(out['f_tedi_r'](mid_tedi) - 1.0) < 0.45
        finally:
            os.chdir(cwd)
