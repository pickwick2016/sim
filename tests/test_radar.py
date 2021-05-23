import unittest
import numpy as np
import math
from functools import partial

from sim import Scenario, Entity
from sim.event import StepEvent
from sim.common import Radar, Uav
from sim import vec

from tests import Target, ResultRecord


class TestRadar(unittest.TestCase):
    """ 测试 Radar """

    def test_create(self):
        """ 测试创建. """
        radar = Radar()
        self.assertTrue(radar is not None)

        radar = Radar(pos=[1, 1], search_rate=2.0, track_rate=2.0)
        self.assertTrue(radar is not None)
        np.testing.assert_almost_equal(radar.position, vec.vec([1, 1]))
        self.assertAlmostEqual(radar._search_rate, 2.0)
        self.assertAlmostEqual(radar._track_rate, 2.0)

        radar = Radar(name='radar', pos=[10, 10], min_v=0.0, search_rate=6.0, search_num=3,
                      track_rate=1.0, cancel_num=3, error_d=0.1, error_r=5, max_r=20)
        self.assertTrue(radar is not None)
        self.assertTrue(radar.name == 'radar')
        np.testing.assert_almost_equal(radar.position, vec.vec([10, 10]))
        self.assertTrue(radar.results is None)


    def test_detect(self):
        radar = Radar()
        uav = Target(pos=vec.vec([50, 50]))

        ret = radar._do_detect(uav)
        a, r = ret
        self.assertAlmostEqual(a, math.pi * 0.25)
        self.assertAlmostEqual(r, 50 * 2 ** 0.5)


    def test_run_1(self):
        """ 探测单目标. """

        results = []
        def append_results(e, results):
            if e.is_active and e.results:
                results.append(e.results)

        dist, vel = 150.0, 5.0
        tt = dist / vel
        scene = Scenario(end=40)
        target = scene.add(RadarTarget(pos=[dist, 0], speed=[-vel, 0]))
        radar = scene.add(Radar(pos=[0, 0]))

        scene.step_handlers.append(StepEvent(entity=radar, evt=partial(append_results, results=results)))
        scene.run()

        bid_set = set()
        time_set = set()
        self.assertTrue(len(results) > int(tt - 18))
        for i in range(len(results)):
            ret = results[i][0]
            bid_set.add(ret[0])
            time_set.add(ret[1])
            if i < 3:
                self.assertTrue(ret[-1] == 1)
            else:
                self.assertTrue(ret[-1] == 2)
        self.assertTrue(len(bid_set) == 1)
        self.assertTrue(len(time_set) == len(results))
        self.assertTrue(results[-1][0][1] <= tt)


        
