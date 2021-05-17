import unittest
import numpy as np
import math

from sim import Scenario, Entity
from sim.event import StepEvent
from sim.common import Radar, Uav
from sim import vec


class Target(Entity):
    """ 测试目标. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position = vec.vec(kwargs['pos'])
        self.rcs = 0.1


class TestRadar(unittest.TestCase):
    """ 测试 Radar """

    def test_create(self):
        radar = Radar()
        self.assertTrue(radar is not None)

        radar = Radar(pos=[1, 1], search_rate=2.0, track_rate=2.0)
        np.testing.assert_almost_equal(radar.position, vec.vec([1, 1]))

        self.assertAlmostEqual(radar.search_rate, 2.0)
        self.assertAlmostEqual(radar.track_rate, 2.0)
        

    def test_detect(self):
        radar = Radar()
        uav = Target(pos=vec.vec([50, 50]))

        ret = radar.detect(uav)
        a, r = ret[0], ret[1]
        self.assertAlmostEqual(a, math.pi * 0.25)
        self.assertAlmostEqual(r, 50 * 2 ** 0.5)


        