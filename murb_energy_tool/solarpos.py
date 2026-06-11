"""NOAA solar position (replaces pvlib.solarposition.get_solarposition).

Implements the NOAA Solar Calculator equations (Meeus, Astronomical
Algorithms). Accuracy vs pvlib's NREL SPA is well under 0.5 degrees, which
is far inside the +/-1% monthly-energy parity tolerance.
Returns TRUE (unrefracted) elevation — murb uses the 'elevation' column,
not 'apparent_elevation'.
"""
import datetime
import math


def solar_position(year, month, day, hour_local, tz, lat, lon):
    """hour_local: 0..23, start-of-hour, local STANDARD time (pvlib EPW
    convention). Returns (elevation_deg, azimuth_deg_clockwise_from_north)."""
    d = datetime.date(year, month, day)
    # Julian day at the given local-standard instant, converted to UTC
    jd = d.toordinal() + 1721424.5 + (hour_local - tz) / 24.0
    jc = (jd - 2451545.0) / 36525.0

    geom_mean_long = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360.0
    geom_mean_anom = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    ecc = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)
    ma = math.radians(geom_mean_anom)
    eq_of_center = (math.sin(ma) * (1.914602 - jc * (0.004817 + 0.000014 * jc))
                    + math.sin(2 * ma) * (0.019993 - 0.000101 * jc)
                    + math.sin(3 * ma) * 0.000289)
    true_long = geom_mean_long + eq_of_center
    app_long = true_long - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * jc))

    mean_obliq = 23.0 + (26.0 + (21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813))) / 60.0) / 60.0
    obliq_corr = mean_obliq + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * jc))

    decl = math.degrees(math.asin(
        math.sin(math.radians(obliq_corr)) * math.sin(math.radians(app_long))))

    var_y = math.tan(math.radians(obliq_corr / 2.0)) ** 2
    eq_time = 4.0 * math.degrees(
        var_y * math.sin(2.0 * math.radians(geom_mean_long))
        - 2.0 * ecc * math.sin(ma)
        + 4.0 * ecc * var_y * math.sin(ma) * math.cos(2.0 * math.radians(geom_mean_long))
        - 0.5 * var_y * var_y * math.sin(4.0 * math.radians(geom_mean_long))
        - 1.25 * ecc * ecc * math.sin(2.0 * ma))  # minutes

    true_solar_min = (hour_local * 60.0 + eq_time + 4.0 * lon - 60.0 * tz) % 1440.0
    # NOAA: with true solar time in [0, 1440), hour angle is ts/4 - 180,
    # giving ha in [-180, 180) — the sign matters for the azimuth branch below.
    ha = true_solar_min / 4.0 - 180.0

    lat_r, decl_r, ha_r = math.radians(lat), math.radians(decl), math.radians(ha)
    cos_zen = (math.sin(lat_r) * math.sin(decl_r)
               + math.cos(lat_r) * math.cos(decl_r) * math.cos(ha_r))
    cos_zen = max(-1.0, min(1.0, cos_zen))
    zen = math.degrees(math.acos(cos_zen))
    elevation = 90.0 - zen

    sin_zen = math.sin(math.radians(zen))
    if abs(sin_zen) < 1e-9:
        azimuth = 180.0
    else:
        cos_az = ((math.sin(lat_r) * cos_zen) - math.sin(decl_r)) / (math.cos(lat_r) * sin_zen)
        cos_az = max(-1.0, min(1.0, cos_az))
        theta = math.degrees(math.acos(cos_az))
        if ha > 0:
            azimuth = (theta + 180.0) % 360.0
        else:
            azimuth = (540.0 - theta) % 360.0
    return elevation, azimuth
