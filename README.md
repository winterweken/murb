# murb_energy_tool

A lightweight energy model based on PHPP and RETScreen. Uses hourly TMY (EPW) files, but data is aggregated into a monthly timestep. Mainly being used during early stage design to understand the minimum thermal envelope performance required given TEDI, TEUI and GHGI targets.

This project includes both a **Python library** for programmatic use and an interactive **Streamlit Web Application** for energy modelling. EPW files can be found from local resources or our good friends from Honeybee/Ladybug.

Found Here: https://www.ladybug.tools/epwmap/

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

### Anaconda (Recommended)

#### Building the environment
1. Open Anaconda Powershell Prompt and [create a fresh environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands) with Python version 3.10
2. Activate the fresh environment and install pip (if Anaconda didn't do this automatically)
3. Download or clone this repository and `cd` to the root folder of the repository
4. Install the required packages with:
   ```bash
   python -m pip install -r requirements.txt
   ```
> Note: The environment you just created has the packages necessary to run `murb_energy_tool` and the web app. You may want to install some additional ones, such as Jupyter Notebook, if you intend to run the example scripts.

#### Installing the python module
If you wish to use the `murb_energy_tool` module globally in your environment:
5. Find the location of the environment you just created. Possibly something like `C:\Users\Your Name\AppData\Local\Continuum\anaconda3\envs\[new env]` *(Hint: With the env activated in Anaconda Prompt run `conda info` and look for "active env location")*
6. From the downloaded repository, copy the entire folder "murb_energy_tool" into the environment.

#### Test the installation
7. Open a Python terminal and try importing the package: 
   ```python
   from murb_energy_tool import test
   ```
   If you see "All tests passed", the package has been installed correctly.
> Note: You will need to activate the environment you created each time you want to use the `murb_energy_tool` or run the web app.

## Programmatic Usage

For Python scripting and API usage, see the [Jupyter Notebook examples](examples).

## To-do
- [x] Below-grade heat transfer
- [ ] More precise COPs for heating and cooling plants
- [x] Factor for non-normal irradiance on windows
- [ ] Pumps and elevator loads
- [ ] Report financial metrics
- [ ] Documentation
