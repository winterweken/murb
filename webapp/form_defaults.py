from murb_energy_tool import static

PROVINCES = sorted(static.ghg_electricity.keys())

GEOMETRY_FIELDS = [
    ("gfa", "Gross floor area [m²]", 5000.0, 1.0, "%.1f"),
    ("area_walls_ag", "Above-grade walls area [m²]", 2500.0, 1.0, "%.1f"),
    ("area_walls_bg", "Below-grade walls area [m²]", 500.0, 1.0, "%.1f"),
    ("area_windows", "Windows area [m²]", 1500.0, 1.0, "%.1f"),
    ("area_roof", "Roof area [m²]", 800.0, 1.0, "%.1f"),
    ("area_sog", "Slabs on grade area [m²]", 0.0, 1.0, "%.1f"),
    ("perim_exp", "Exposed slab perimeter [m]", 0.0, 1.0, "%.1f"),
]

ENVELOPE_FIELDS = [
    ("u_walls_ag", "U-value, above-grade walls [W/m²K]", 0.273, 0.001, "%.3f"),
    ("u_walls_bg", "U-value, below-grade walls [W/m²K]", 0.379, 0.001, "%.3f"),
    ("f_factor", "F-factor, slabs on grade [W/mK]", 0.93, 0.01, "%.2f"),
    ("u_windows", "U-value, windows [W/m²K]", 2.56, 0.01, "%.2f"),
    ("u_roof", "U-value, roof [W/m²K]", 0.164, 0.001, "%.3f"),
]

HVAC_FIELDS = [
    ("setpoint_htg", "Heating setpoint [°C]", 21.0, 0.5, "%.1f"),
    ("setpoint_clg", "Cooling setpoint [°C]", 24.0, 0.5, "%.1f"),
    ("cop_htg", "Heating plant seasonal COP", 0.85, 0.01, "%.2f"),
    ("cop_clg", "Cooling plant seasonal COP", 5.2, 0.1, "%.2f"),
    ("cop_dhw", "DHW plant seasonal COP", 0.85, 0.01, "%.2f"),
    ("hrv_efficiency", "HRV sensible effectiveness [0-1]", 0.55, 0.01, "%.2f"),
]

LEAKAGE_FIELDS = [
    ("test_leakage", "Air leakage @ 75 Pa [L/s/m² envelope]", 2.0, 0.1, "%.2f"),
]

ADVANCED_FIELDS = [
    ("clg_pct", "Cooled fraction of GFA [0-1]", 1.0, 0.01, "%.2f"),
    ("occupant_density", "Occupant density [m²/person]", static.necb["occupant_density"], 1.0, "%.1f"),
    ("peak_receptacle_load", "Peak receptacle load [W/m²]", static.necb["peak_receptacle_load"], 0.5, "%.2f"),
    ("lpd", "Lighting power density [W/m²]", static.necb["lpd"], 0.1, "%.2f"),
    ("service_water_heating_load", "Service water heating load [W/person]", static.necb["service_water_heating_load"], 10.0, "%.1f"),
]

MASS_LEVELS = ["light", "medium", "heavy"]

WINDOW_GROUP_DEFAULTS = [
    {"pct_window_area": 0.25, "window_azimuth": 0, "shgc": 0.4, "shading": 0.0},
    {"pct_window_area": 0.25, "window_azimuth": 90, "shgc": 0.4, "shading": 0.0},
    {"pct_window_area": 0.25, "window_azimuth": 180, "shgc": 0.4, "shading": 0.0},
    {"pct_window_area": 0.25, "window_azimuth": 270, "shgc": 0.4, "shading": 0.0},
]
