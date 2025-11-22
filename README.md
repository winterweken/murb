#murb_energy_tool
A lightweight energy model based on PHPP and RETScreen. Uses hourly TMY (EPW) files, but data is aggregated into a
monthly timestep. Mainly being used during early stage design to understand the minimum thermal envelope performance
required given TEDI, TEUI and GHGI targets.

## Installation
### Anaconda
#### Building the environment
1. Open Anaconda Powershell Prompt and [create a fresh environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands) with Python version 3.10
2. Activate the fresh environment and install pip (if Anaconda didn't do this automatically)
3. Download this whole repository and `cd` to the root folder of the repository
4. Install the required packages with `python -m pip install -r requirements.txt`
>Note: The environment you just created has only the packages necessary to run murbs_energy_tool. You'll probably want
> to install some additional ones, such as Jupyter Notebook.
#### Installing murb_energy_tool
5. Find the location of the environment you just created. Possibly something like `C:\Users\Your Name\AppData\Local\Continuum\anaconda3\envs\[new env]` *Hint: With the env activated in Anaconda Prompt run `conda 
info` and look for "active env location"*
6. From the downloaded repository, copy the entire folder "murb_energy_tool" into the environment.
#### Test the installation
7. Open a Python terminal and try importing the package: `from murb_energy_tool import test`. If you see "All tests 
passed", the package has been installed correctly.
>Note: You will need to activate the environment you created each time you want to use murb_energy_tool

## Usage
See [Jupyter Notebook examples](examples)

## To-do
- [x] Below-grade heat transfer
- [ ] More precise COPs for heating and cooling plants
- [x] Factor for non-normal irradiance on windows
- [ ] Pumps and elevator loads
- [ ] Report financial metrics
- [ ] Documentation

Questions? Contact [Jonathan Graham](mailto:jgraham@kpmbarchitects.com)
