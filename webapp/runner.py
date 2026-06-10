import os
import tempfile
import threading
from pathlib import Path

from murb_energy_tool import reporting, simulation

_RUN_LOCK = threading.Lock()


def run_simulation(epw_bytes: bytes, epw_filename: str, run_kwargs: dict, window_groups: list) -> dict:
    """Run a single simulation in an isolated temp dir and return the report artifacts in memory.

    The library globs `./input/*.epw` and writes to `./results/{name}/`, both
    relative to the current working directory. We chdir into a per-call temp
    dir, run, capture artifacts as strings, then restore cwd. The chdir
    critical section is serialised via a process-wide lock so that
    concurrent Streamlit sessions can't race.
    """
    with tempfile.TemporaryDirectory(prefix="murb_run_") as td:
        td_path = Path(td)
        (td_path / "input").mkdir()
        (td_path / "input" / epw_filename).write_bytes(epw_bytes)

        original_cwd = os.getcwd()
        with _RUN_LOCK:
            try:
                os.chdir(td_path)
                wg_objects = [simulation.WindowGroup(**row) for row in window_groups]
                run = simulation.Run(window_groups=wg_objects, **run_kwargs)
                reporting.write_results(run)

                results_dir = td_path / "results" / run.name
                html = (results_dir / f"{run.name}.html").read_text()
                tables_js = (results_dir / "javascript" / "tables.js").read_text()
                metadata_js = (results_dir / "javascript" / "metadata.js").read_text()
            finally:
                os.chdir(original_cwd)

        return {
            "name": run.name,
            "html": html,
            "tables_js": tables_js,
            "metadata_js": metadata_js,
        }
