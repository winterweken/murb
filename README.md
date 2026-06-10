# murb_energy_tool

A lightweight energy model based on PHPP and RETScreen. Uses hourly TMY (EPW) files, but data is aggregated into a monthly timestep. Mainly being used during early stage design to understand the minimum thermal envelope performance required given TEDI, TEUI and GHGI targets.

This project includes both a **Python library** for programmatic use and an interactive **Streamlit Web Application** for energy modelling.

## Web Application

The interactive web application allows you to easily configure building geometry, windows, envelope, HVAC, and advanced settings to run simulations and generate downloadable reports.

### Running the Web App locally

1. Ensure you have installed the requirements (see [Installation](#installation) below).
2. Activate your Python environment.
3. From the root directory of the project, run:
   ```bash
   streamlit run webapp/app.py
   ```
4. The web interface will open in your default browser. Upload an EPW weather file, fill in the parameters, and click "Run simulation".

Available Here: https://9s4appx5hvvwlnevx3mtxkj.streamlit.app

## Installation

### Library (programmatic use) — stdlib only, Python 3.8+

`murb_energy_tool` is now a **pure-Python library** with no native dependencies (no numpy, scipy, pandas, or pvlib required). It works in any standard CPython 3.8+ environment, including constrained hosts such as pyRevit's embedded interpreter.

```bash
# Clone and add to sys.path — no pip install step needed for library-only use
git clone https://github.com/winterweken/murb
python -c "from murb_energy_tool import test"  # should print "All tests passed"
```

### Web application — additional packages required

The Streamlit web app uses `pandas`, `pvlib`, `streamlit`, and `tabulate`. Install them with:

```bash
pip install -r requirements.txt
streamlit run webapp/app.py
```

> **Anaconda users:** a conda environment is no longer required for the library. Create a plain `venv` or use any Python 3.8+ interpreter.

#### Test the installation
```python
from murb_energy_tool import test
```
If you see "All tests passed", the library is correctly installed.

---

### Changes in the pure-Python port

- **ISD weather-file support removed.** Passing `isd_file=` to `Run()` now raises `NotImplementedError`. Use a TMY EPW file instead (`epw_path=` or place it in `./input/`).
- **Library is now embeddable** in constrained Python hosts (e.g. pyRevit's embedded CPython) with zero per-machine environment setup.
- Internally, numpy arrays are replaced by a lightweight `Vec` list subclass; pvlib solar position is replaced by a NOAA NREL SPA implementation; scipy interpolation is replaced by stdlib linear/quadratic interpolation; pandas EPW parsing is replaced by a pure-Python EPW reader.
- Console summaries use `tabulate` instead of `pandas.DataFrame.to_markdown` (cosmetic only).

## Programmatic Usage

For Python scripting and API usage, see the [Jupyter Notebook examples](examples).

## To-do
- [x] Below-grade heat transfer
- [ ] More precise COPs for heating and cooling plants
- [x] Factor for non-normal irradiance on windows
- [ ] Pumps and elevator loads
- [ ] Report financial metrics
- [ ] Documentation
