from sim.common.sensor import SensorType
import unittest
import numpy as np
from functools import partial

from sim.common import Sensor, SensorType, util
from sim.common.util import aer2xyz, rad, deg
from sim import vec

from tests import Target


class TestSensor(unittest.TestCase):
    """ 测试传感器. """

    def test_create(self):
        """ 测试创建. """
        s = Sensor()
        self.assertTrue(s.type == SensorType.Unknown)

    def test_conic(self):
        """ 测试圆锥型传感器. """
        base = Target()
        s = Sensor(parent=base, type=SensorType.Conic, params=rad(1.0))
        self.assertTrue(s.type == SensorType.Conic)
        np.testing.assert_almost_equal(s.direction, vec.vec2((0, 0)))

        pos = aer2xyz((0, 0, 0), (0, 0, 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (rad(0.9), 0, 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (0, rad(0.9), 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (rad(1.1), 0, 10))
        self.assertTrue(not s.contain(pos))

        pos = aer2xyz((0, 0, 0), (0, rad(1.1), 10))
        self.assertTrue(not s.contain(pos))

        # 调转方向.
        s.direction = vec.vec2((0, rad(45)))

        pos = aer2xyz((0, 0, 0), (0, rad(45.9), 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (0, rad(43.9), 10))
        self.assertTrue(not s.contain(pos))


    def test_rect(self):
        """ 测试矩形传感器. """
        base = Target()
        s = Sensor(parent=base, type=SensorType.Rect,
                   params=(rad(1.0), rad(0.5)))
        self.assertTrue(s.type == SensorType.Rect)
        np.testing.assert_almost_equal(s.direction, vec.vec2((0, 0)))

        pos = aer2xyz((0, 0, 0), (0, 0, 10))
        t = Target(pos=pos)
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (rad(0.9), 0, 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (0, rad(0.4), 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (-rad(0.9), 0, 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (0, -rad(0.4), 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (rad(0.9), -rad(0.4), 10))
        self.assertTrue(s.contain(pos))

        pos = aer2xyz((0, 0, 0), (rad(1.1), -rad(0.4), 10))
        self.assertTrue(not s.contain(pos))

        pos = aer2xyz((0, 0, 0), (rad(0.9), -rad(0.6), 10))
        self.assertTrue(not s.contain(pos))
