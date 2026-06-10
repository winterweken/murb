"""Pure-Python EPW weather file reader (replaces pvlib.iotools.read_epw).

EPW data rows are fixed-position CSV. Field indices used (0-based):
1=month, 2=day, 3=hour(1..24, hour-ending), 6=dry-bulb temp [C],
13=GHI, 14=DNI, 15=DHI [Wh/m2].
Header line 0: LOCATION,city,state,country,source,WMO,lat,lon,TZ,altitude.
pvlib timestamps rows at hour-1 (start of hour) local standard time; the
solar-position caller must use the same convention for parity.
"""
from murb_energy_tool.vec import Vec

HEADER_ROWS = 8


class EpwData:
    """Hourly weather columns as plain lists, plus solar position slots
    (filled by utilities.process_weather_data after parsing)."""

    def __init__(self):
        self.year = []
        self.month = []
        self.day = []
        self.hour = []          # 0..23, start-of-hour (pvlib convention)
        self.temp_air = []
        self.ghi = []
        self.dni = []
        self.dhi = []
        self.sun_elevation = []  # degrees, true (unrefracted)
        self.sun_azimuth = []    # degrees clockwise from north

    def monthly_sum(self, values):
        out = [0.0] * 12
        for m, v in zip(self.month, values):
            out[m - 1] += v
        return Vec(out)


def read_epw(path, coerce_year=2021):
    data = EpwData()
    with open(str(path), 'r', errors='replace') as f:
        lines = f.read().splitlines()

    loc = lines[0].split(',')
    metadata = {
        'city': loc[1],
        'latitude': float(loc[6]),
        'longitude': float(loc[7]),
        'TZ': float(loc[8]),
        'altitude': float(loc[9]),
    }

    for line in lines[HEADER_ROWS:]:
        if not line.strip():
            continue
        f_ = line.split(',')
        data.year.append(coerce_year)
        data.month.append(int(f_[1]))
        data.day.append(int(f_[2]))
        data.hour.append(int(f_[3]) - 1)
        data.temp_air.append(float(f_[6]))
        data.ghi.append(float(f_[13]))
        data.dni.append(float(f_[14]))
        data.dhi.append(float(f_[15]))
    return data, metadata
