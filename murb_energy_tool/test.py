from murb_energy_tool import heatbalance, static
from murb_energy_tool.vec import Vec
import math

print('Running test.py')

"""
Heat Balance Functions
"""
htg_degree_hours = Vec([17.6086, 16.5144, 15.3207, 9.6504, 5.187, 2.0687, 1.1326, 1.2248, 2.6802, 7.6254,
                         12.2228, 17.5143])
clg_degree_hours = Vec([0., 0., 0., 0.0263, 0.2125, 0.3511, 0.6661, 0.3644, 0.233, 0., 0., 0.])
htg_degree_hours_ground = Vec([9.84070795, 8.88838137, 9.84070795, 9.52326575, 9.84070795, 9.52326575, 9.84070795,
                                9.84070795, 9.52326575, 9.84070795, 9.52326575, 9.84070795])
clg_degree_hours_ground = Vec([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
hours = Vec([744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744])

area_walls_ag = 2800
area_walls_bg = 900
area_windows = 2800 * .3
area_roof = 700
u_walls_ag = 0.273
u_walls_bg = 0.379
u_windows = 2.56
u_roof = 0.164
oa_rate = 10400
heat_recovery = 0.8
envelope_area = area_walls_ag + area_windows + area_roof
test_leakage = 3.09
gfa = 7000
occupancy = 25


def _assert_allclose(actual, desired, rtol):
    """Element-wise relative-tolerance check mirroring np.testing.assert_allclose."""
    assert len(actual) == len(desired), 'Length mismatch: %d vs %d' % (len(actual), len(desired))
    for i, (a, d) in enumerate(zip(actual, desired)):
        if not math.isclose(a, d, rel_tol=rtol, abs_tol=0.0):
            raise AssertionError(
                'Mismatch at index %d: got %.10g, expected %.10g (rtol=%.0e)' % (i, a, d, rtol))


def test_transmission():
    htg = heatbalance.transmission(u_walls_ag=u_walls_ag,
                                   u_walls_bg=u_walls_bg,
                                   u_windows=u_windows,
                                   u_roof=u_roof,
                                   f_factor=0.93,
                                   area_walls_ag=area_walls_ag,
                                   area_walls_bg=area_walls_bg,
                                   area_sog=0,
                                   perim_exp=0,
                                   area_windows=area_windows,
                                   area_roof=area_roof,
                                   degree_hours=htg_degree_hours,
                                   degree_hours_ground=htg_degree_hours_ground)
    clg = heatbalance.transmission(u_walls_ag=u_walls_ag,
                                   u_walls_bg=u_walls_bg,
                                   u_windows=u_windows,
                                   u_roof=u_roof,
                                   f_factor=0.93,
                                   area_walls_ag=area_walls_ag,
                                   area_walls_bg=area_walls_bg,
                                   area_sog=0,
                                   perim_exp=0,
                                   area_windows=area_windows,
                                   area_roof=area_roof,
                                   degree_hours=clg_degree_hours,
                                   degree_hours_ground=clg_degree_hours_ground)

    htg_desired = [44392.11637629, 41559.90892333, 38900.61444799, 25221.92858124, 14577.33410761,
                   7024.05272576, 4845.81375353, 5067.11559268, 8491.79757001, 20430.07168441, 31396.29789823,
                   44165.77403972]
    clg_desired = [0., 0., 0., 63.12622961, 510.05033426, 842.72316405, 1598.79777719, 874.64631438,
                   559.25519004, 0., 0., 0.]

    _assert_allclose(htg, htg_desired, rtol=1e-09)
    _assert_allclose(clg, clg_desired, rtol=1e-09)


def test_ventilation():
    htg = heatbalance.ventilation(oa_rate, heat_recovery, htg_degree_hours)
    clg = heatbalance.ventilation(oa_rate, heat_recovery, clg_degree_hours)

    htg_desired = [12086.54304, 11335.48416, 10516.12848, 6624.03456, 3560.3568, 1419.95568, 777.41664,
                   840.70272, 1839.68928, 5234.07456, 8389.72992, 12021.81552]
    clg_desired = [0, 0, 0, 18.05232, 145.86, 240.99504, 457.21104, 250.12416, 159.9312, 0, 0, 0]

    _assert_allclose(htg, htg_desired, rtol=1e-11)
    _assert_allclose(clg, clg_desired, rtol=1e-11)


def test_infiltration():
    htg = heatbalance.infiltration(test_leakage, envelope_area, htg_degree_hours)
    clg = heatbalance.infiltration(test_leakage, envelope_area, clg_degree_hours)

    htg_desired = [55250.31039, 51817.0511, 48071.59175, 30279.95385, 16275.1928, 6490.937219, 3553.746553,
                   3843.041478, 8409.634038, 23926.13364, 38351.34502, 54954.42632]
    clg_desired = [0, 0, 0, 82.5212205, 666.7589109, 1101.642605, 2090.014638, 1143.373869, 731.0815353, 0, 0, 0]

    _assert_allclose(htg, htg_desired, rtol=1e-09)
    _assert_allclose(clg, clg_desired, rtol=1e-09)


def test_outdoor_air_rate():
    oa = heatbalance.outdoor_air_rate(gfa=gfa, people_outdoor_air_rate=static.ashrae_62['people_outdoor_air_rate'],
                                      area_outdoor_air_rate=static.ashrae_62['area_outdoor_air_rate'], occupancy=25)
    assert oa == 12600


def test_internal_gains():
    int_gains = heatbalance.internal_gains(gfa, hours, occupancy, static.necb['fraction_occupied'], static.necb['lpd'],
                                           static.necb['fraction_lighting'], static.necb['peak_receptacle_load'],
                                           static.necb['fraction_receptacle_load'])

    int_gains_desired = [35599.49232, 32154.38016, 35599.49232, 34451.1216, 35599.49232, 34451.1216,
                         35599.49232, 35599.49232, 34451.1216, 35599.49232, 34451.1216, 35599.49232]

    _assert_allclose(int_gains, int_gains_desired, rtol=1e-15)


"""
Models Functions
"""

"""
Solar Gains Functions
"""

"""
Simulation Functions
"""

"""
Run Tests
"""

# Heat Balance
test_transmission()
test_ventilation()
test_infiltration()
test_outdoor_air_rate()
test_internal_gains()

# Models

# Solar Gains

# Simulation

print('All tests passed')
