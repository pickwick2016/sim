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
        """ 测试检测. """
        # 测试1
        radar = Radar()

        uav = Target(pos=[50, 50])  # 静止目标, 无RCS
        ret = radar.detect(uav)
        self.assertTrue(ret is None)

        uav = Target(pos=[50, 50], rcs=1.0)
        ret = radar.detect(uav)
        self.assertTrue(ret is not None)
        a, r = ret
        self.assertAlmostEqual(a, math.pi * 0.25)
        self.assertAlmostEqual(r, 50 * 2 ** 0.5)

        # 测试2
        radar = Radar(min_v=1.0)

        uav = Target(pos=[50, 0], vel=[1.1, 0], rcs=1.0)  # 运动目标, 快速
        ret = radar.detect(uav)
        self.assertTrue(ret is not None)

        uav = Target(pos=[50, 0], vel=[-1.1, 0], rcs=1.0)  # 运动目标, 快速
        ret = radar.detect(uav)
        self.assertTrue(ret is not None)

        uav = Target(pos=[50, 0], vel=[0.9, 0], rcs=1.0)  # 运动目标, 慢速
        ret = radar.detect(uav)
        self.assertTrue(ret is None)

        uav = Target(pos=[50, 0], vel=[-0.9, 0], rcs=1.0)  # 运动目标, 慢速
        ret = radar.detect(uav)
        self.assertTrue(ret is None)


    def test_run_1(self):
        """ 探测单目标. """
        scene = Scenario(end=30)
        radar = scene.add(Radar(pos=[0, 0]))
        dist, vel = 150.0, 5.0
        scene.add(Target(pos=[dist, 0], speed=[-vel, 0]))

        recorder = ResultRecord(radar)
        scene.step_handlers.append(recorder)
        scene.run()

        self.assertTrue(len(recorder.results) > (30 - 18))

        times = [ret[0].time for ret in recorder.results]
        times_diff = [times[i] - times[i-1] for i in range(1, len(times))]
        self.assertTrue(times_diff[0] >= radar.search_rate and times_diff[1] >= radar.search_rate)
        for v in times_diff:
            self.assertTrue(v >= self.track_rate)
        
        values = [ret[0].value for ret in recorder.results]
        self.assertTrue(times[-1] <= 30)
        self.assertTrue(len(set(values)) == len(values))



        
