from pathlib import Path
import pvlib.iotools
import numpy as np
import pandas as pd


def process_weather_data(silent, isd_file=None):
    # Process EPW file
    p = list(Path('input').glob('*.epw'))
    if len(p) != 1:
        raise Exception('There needs to be exactly one EPW file in the input directory.')
    epw, metadata = pvlib.iotools.read_epw(p[0], coerce_year=2021)
    solar_positions = pvlib.solarposition.get_solarposition(epw.index,
                                                            metadata['latitude'],
                                                            metadata['longitude'],
                                                            metadata['altitude'])
    epw = epw.merge(right=solar_positions, left_index=True, right_index=True)
    epw = epw.filter(['temp_air', 'dni', 'dhi', 'ghi', 'elevation', 'azimuth'], axis='columns')

    # Process ISD file if it is provided.
    if isd_file is not None:
        p = list(Path('input').glob(isd_file))
        if not silent:
            print(f'Weather file for degree hours: {p[0].name}')
        df = pd.read_csv(p[0], index_col=False, dtype='str')
        df.set_index('DATE', inplace=True)
        df.index = pd.to_datetime(df.index)
        tmp = df.filter(['TMP']).TMP.str.split(',', expand=True)
        tmp.rename(columns={0: 'air temperature', 1: 'air temperature quality code'}, inplace=True)
        tmp['air temperature'] = tmp['air temperature'].astype('float') / 10
        tmp.loc[(tmp['air temperature quality code'].astype(float) != 1) &
                (tmp['air temperature quality code'].astype(float) != 5)] = 8  # if values are missing, fill in with 8 C
        isd = tmp.resample('h').mean()
        isd = isd.rename(columns={'air temperature': 'temp_air'})
        return epw, metadata, isd
    else:
        if not silent:
            print(f'Weather file for degree hours: {p[0].name}')
        return epw, metadata


def get_degree_hours_from_weather_data(weather_file, setpoint_htg, setpoint_clg):
    weather_file['hours'] = 1
    weather_file['htg_hours'] = weather_file.temp_air.apply(lambda x: 0 if x > setpoint_htg else 1)
    weather_file['clg_hours'] = weather_file.temp_air.apply(lambda x: 0 if x < setpoint_clg else 1)
    weather_file['htg_degree_hrs'] = (setpoint_htg - weather_file.temp_air).apply(lambda x: 0 if x < 0 else x) / 1000
    weather_file['clg_degree_hrs'] = (weather_file.temp_air - setpoint_clg).apply(lambda x: 0 if x < 0 else x) / 1000
    # Need this next one for the solar utilisation factor... even if it seems weird
    weather_file['htg_degree_hrs_w_clg_setpoint'] = (setpoint_clg - weather_file.temp_air).apply(
        lambda x: 0 if x < 0 else x) / 1000
    # This next one is for ground heat transfer
    weather_file['temp_air_mean'] = weather_file.temp_air.mean()
    weather_file['htg_degree_hrs_ground'] = (setpoint_htg - weather_file.temp_air_mean).apply(lambda x: 0 if x < 0 else x) / 1000
    weather_file['clg_degree_hrs_ground'] = (weather_file.temp_air_mean - setpoint_clg).apply(lambda x: 0 if x < 0 else x) / 1000
    weather_file['htg_degree_hrs_w_clg_setpoint_ground'] = (setpoint_clg - weather_file.temp_air_mean).apply(
        lambda x: 0 if x < 0 else x) / 1000
    weather_file_monthly = weather_file.resample('ME').sum()
    # drop columns that no longer have meaning
    weather_file_monthly = weather_file_monthly.filter(['hours', 'htg_hours', 'clg_hours', 'htg_degree_hrs',
                                                        'clg_degree_hrs', 'htg_degree_hrs_ground',
                                                        'clg_degree_hrs_ground', 'htg_degree_hrs_w_clg_setpoint',
                                                        'htg_degree_hrs_w_clg_setpoint_ground'])
    return weather_file_monthly


set_zero_below_zero = np.vectorize(lambda x: 0. if x < 0. else x)
set_zero_to_one = np.vectorize(lambda x: 0. if x < 0. else (1. if x > 1. else x))
