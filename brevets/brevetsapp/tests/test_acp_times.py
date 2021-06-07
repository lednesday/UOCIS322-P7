"""
Nose tests for acp_times.py
"""


from acp_times import open_time, close_time
import logging
import nose    # Testing framework
import arrow

''' Not sure what this logging block is for but copying it from Project 3'''
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.WARNING)
log = logging.getLogger(__name__)


"""
open_time and close_time 
    Args:
       control_dist_km:  number, control distance in kilometers
       brevet_dist_km: number, nominal distance of the brevet
           in kilometers, which must be one of 200, 300, 400, 600,
           or 1000 (the only official ACP brevet distances)
       brevet_start_time:  A date object (arrow)
    Returns:
       A date object indicating the control open time.
       This will be in the same time zone as the brevet start time.
"""

brevet_dists: list = [200, 300, 400, 600, 1000]
# control_dist_corners = [200, 400, 600, 1000]
start_time = arrow.get('2021-02-20 14:00:00', 'YYYY-MM-DD HH:mm:ss')

# I thought about using nested loops with control_dist,
# but the oracle value is different for each combination


def test_open_normal():
    for dist in brevet_dists:
        print("testing dist: ", dist)
        assert open_time(100, dist, start_time) == arrow.get(
            '2021-02-20 16:56:00', 'YYYY-MM-DD HH:mm:ss')
    assert open_time(456, 1000, start_time) == arrow.get(
        '2021-02-21 04:00:00', 'YYYY-MM-DD HH:mm:ss')
    assert open_time(889.6, 1000, start_time) == arrow.get(
        '2021-02-21 19:09:00', 'YYYY-MM-DD HH:mm:ss')


def test_close_normal():
    for dist in brevet_dists:
        assert close_time(100, dist, start_time) == arrow.get(
            '2021-02-20 20:40:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(456, 1000, start_time) == arrow.get(
        '2021-02-21 20:24:00', 'YYYY-MM-DD HH:mm:ss')


def test_open_corners():
    for dist in brevet_dists:
        assert open_time(200, dist, start_time) == arrow.get(
            '2021-02-20 19:53:00', 'YYYY-MM-DD HH:mm:ss')
    for dist in brevet_dists:
        assert open_time(300, dist, start_time) == arrow.get(
            '2021-02-20 23:00:00', 'YYYY-MM-DD HH:mm:ss')
    for dist in brevet_dists:
        assert open_time(400, dist, start_time) == arrow.get(
            '2021-02-21 02:08:00', 'YYYY-MM-DD HH:mm:ss')
    assert open_time(600, 600, start_time) == arrow.get(
        '2021-02-21 08:48:00', 'YYYY-MM-DD HH:mm:ss')
    assert open_time(600, 1000, start_time) == arrow.get(
        '2021-02-21 08:48:00', 'YYYY-MM-DD HH:mm:ss')
    assert open_time(1000, 1000, start_time) == arrow.get(
        '2021-02-21 23:05:00', 'YYYY-MM-DD HH:mm:ss')


def test_close_corners():
    assert close_time(200, 300, start_time) == arrow.get(
        '2021-02-21 03:20:00', 'YYYY-MM-DD HH:mm:ss')
    for dist in brevet_dists:
        assert close_time(300, dist, start_time) == arrow.get(
            '2021-02-21 10:00:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(400, 600, start_time) == arrow.get(
        '2021-02-21 16:40:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(600, 600, start_time) == arrow.get(
        '2021-02-22 06:00:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(600, 1000, start_time) == arrow.get(
        '2021-02-22 06:00:00', 'YYYY-MM-DD HH:mm:ss')


def test_oddities():
    # test 1-hour window at 0
    for dist in brevet_dists:
        assert open_time(0, dist, start_time) == arrow.get(
            '2021-02-20 14:00:00', 'YYYY-MM-DD HH:mm:ss')
        assert close_time(0, dist, start_time) == arrow.get(
            '2021-02-20 15:00:00', 'YYYY-MM-DD HH:mm:ss')
    # by the rules the time for a 200km brevet is 13H30
    assert close_time(200, 200, start_time) == arrow.get(
        '2021-02-21 03:30:00', 'YYYY-MM-DD HH:mm:ss')
    # there seems to be a similar extension at 400km
    assert close_time(400, 400, start_time) == arrow.get(
        '2021-02-21 17:00:00', 'YYYY-MM-DD HH:mm:ss')
    # just guessing this is another oddity
    assert close_time(1000, 1000, start_time) == arrow.get(
        '2021-02-23 17:00:00', 'YYYY-MM-DD HH:mm:ss')
    # final controle can be up through 20% longer than brevet distance
    assert close_time(310, 300, start_time) == arrow.get(
        '2021-02-21 10:00:00', 'YYYY-MM-DD HH:mm:ss')
    # TODO: this is super-weird - even when this is broken in acp_times.py, it passes
    assert open_time(301, 300, start_time) == arrow.get(
        '2021-02-20 23:00:00', 'YYYY-MM-DD HH:mm:ss')
    assert open_time(1005, 1000, start_time) == arrow.get(
        '2021-02-21 23:05:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(1005, 1000, start_time) == arrow.get(
        '2021-02-23 17:00:00', 'YYYY-MM-DD HH:mm:ss')
    # test French system for short controle points
    assert close_time(10, 200, start_time) == arrow.get(
        '2021-02-20 15:30:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(59, 200, start_time) == arrow.get(
        '2021-02-20 17:57:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(60, 200, start_time) == arrow.get(
        '2021-02-20 18:00:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(61, 200, start_time) == arrow.get(
        '2021-02-20 18:04:00', 'YYYY-MM-DD HH:mm:ss')


def test_invalids():
    # if last controle is more than 20% over brevet distance, error
    assert open_time(241, 200, start_time) != arrow.get(
        '2021-02-20 19:53:00', 'YYYY-MM-DD HH:mm:ss')
    assert close_time(241, 200, start_time) != arrow.get(
        '2021-02-21 03:30:00', 'YYYY-MM-DD HH:mm:ss')
