from pathlib import Path

from murb_energy_tool.epw import read_epw
from murb_energy_tool.solarpos import solar_position
from murb_energy_tool.vec import Vec


def process_weather_data(silent, isd_file=None, epw_path=None):
    """Read EPW + compute hourly solar position.

    epw_path=None preserves the legacy behaviour (exactly one .epw in
    ./input, relative to cwd) that the Streamlit webapp relies on.
    """
    if isd_file is not None:
        raise NotImplementedError(
            'ISD support was removed in the pure-Python port; use a TMY EPW.')
    if epw_path is None:
        p = list(Path('input').glob('*.epw'))
        if len(p) != 1:
            raise Exception('There needs to be exactly one EPW file in the input directory.')
        epw_path = p[0]
    epw, metadata = read_epw(epw_path, coerce_year=2021)
    for i in range(len(epw.month)):
        elev, az = solar_position(epw.year[i], epw.month[i], epw.day[i], epw.hour[i],
                                  metadata['TZ'], metadata['latitude'], metadata['longitude'])
        epw.sun_elevation.append(elev)
        epw.sun_azimuth.append(az)
    if not silent:
        print('Weather file for degree hours: %s' % Path(str(epw_path)).name)
    return epw, metadata


class MonthlyWeather:
    """Monthly aggregates; attribute names match the old DataFrame columns."""


def get_degree_hours_from_weather_data(epw, setpoint_htg, setpoint_clg):
    t = epw.temp_air
    t_mean = sum(t) / len(t)
    mw = MonthlyWeather()
    mw.hours = epw.monthly_sum([1.0] * len(t))
    mw.htg_hours = epw.monthly_sum([0.0 if x > setpoint_htg else 1.0 for x in t])
    mw.clg_hours = epw.monthly_sum([0.0 if x < setpoint_clg else 1.0 for x in t])
    mw.htg_degree_hrs = epw.monthly_sum([max(setpoint_htg - x, 0.0) / 1000.0 for x in t])
    mw.clg_degree_hrs = epw.monthly_sum([max(x - setpoint_clg, 0.0) / 1000.0 for x in t])
    mw.htg_degree_hrs_w_clg_setpoint = epw.monthly_sum(
        [max(setpoint_clg - x, 0.0) / 1000.0 for x in t])
    mw.htg_degree_hrs_ground = epw.monthly_sum(
        [max(setpoint_htg - t_mean, 0.0) / 1000.0] * len(t))
    mw.clg_degree_hrs_ground = epw.monthly_sum(
        [max(t_mean - setpoint_clg, 0.0) / 1000.0] * len(t))
    mw.htg_degree_hrs_w_clg_setpoint_ground = epw.monthly_sum(
        [max(setpoint_clg - t_mean, 0.0) / 1000.0] * len(t))
    return mw


def set_zero_below_zero(v):
    return Vec([0.0 if x < 0.0 else x for x in v])


def set_zero_to_one(v):
    return Vec([0.0 if x < 0.0 else (1.0 if x > 1.0 else x) for x in v])
