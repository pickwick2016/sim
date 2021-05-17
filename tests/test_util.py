import unittest
import math

import numpy as np

from sim import vec
from sim.common import util
from sim.common.util import rad


class TestUtil(unittest.TestCase):
    def test_aer(self):
        v0 = vec.vec([0, 0])
        v1 = vec.vec([1, 1])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 0.25, 2 ** 0.5]))

        v0 = vec.vec([0, 0])
        v1 = vec.vec([1, -1])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 0.75, 2 ** 0.5]))

        v0 = vec.vec([0, 0])
        v1 = vec.vec([-1, -1])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 1.25, 2 ** 0.5]))

        v0 = vec.vec([0, 0])
        v1 = vec.vec([-1, 1])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 1.75, 2 ** 0.5]))

        v0 = vec.vec([0, 0, 0])
        v1 = vec.vec([1, 1, 2 ** 0.5])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 0.25, math.pi * 0.25, 2]))

        v0 = vec.vec([0, 0, 0])
        v1 = vec.vec([1, -1, 2 ** 0.5])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 0.75, math.pi * 0.25, 2]))

        v0 = vec.vec([0, 0, 0])
        v1 = vec.vec([-1, -1, -2 ** 0.5])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 1.25, -math.pi * 0.25, 2]))

        v0 = vec.vec([0, 0, 0])
        v1 = vec.vec([-1, 1, -2 ** 0.5])
        ret = util.polar(v0, v1)
        np.testing.assert_almost_equal(ret, vec.vec([math.pi * 1.75, -math.pi * 0.25, 2]))

    def test_in_range_d(self):
        rng = [rad(30), rad(330)]
        self.assertTrue(util.in_range_d(rng, rad(30)))
        self.assertTrue(not util.in_range_d(rng, rad(330)))
        self.assertTrue(util.in_range_d(rng, rad(50)))
        self.assertTrue(util.in_range_d(rng, rad(50+360)))
        self.assertTrue(util.in_range_d(rng, rad(50-360)))
        self.assertTrue(not util.in_range_d(rng, rad(350)))
        self.assertTrue(not util.in_range_d(rng, rad(350+360)))
        self.assertTrue(not util.in_range_d(rng, rad(350-360)))

        rng = [rad(30), rad(330-360)]
        self.assertTrue(util.in_range_d(rng, rad(30)))
        self.assertTrue(not util.in_range_d(rng, rad(330)))
        self.assertTrue(util.in_range_d(rng, rad(50)))
        self.assertTrue(util.in_range_d(rng, rad(50+360)))
        self.assertTrue(util.in_range_d(rng, rad(50-360)))
        self.assertTrue(not util.in_range_d(rng, rad(350)))
        self.assertTrue(not util.in_range_d(rng, rad(350+360)))
        self.assertTrue(not util.in_range_d(rng, rad(350-360)))
        
        rng = [rad(30+360), rad(330)]
        self.assertTrue(util.in_range_d(rng, rad(30)))
        self.assertTrue(not util.in_range_d(rng, rad(330)))
        self.assertTrue(util.in_range_d(rng, rad(50)))
        self.assertTrue(util.in_range_d(rng, rad(50+360)))
        self.assertTrue(util.in_range_d(rng, rad(50-360)))
        self.assertTrue(not util.in_range_d(rng, rad(350)))
        self.assertTrue(not util.in_range_d(rng, rad(350+360)))
        self.assertTrue(not util.in_range_d(rng, rad(350-360)))

        
        rng = [rad(30-360), rad(330)]
        self.assertTrue(util.in_range_d(rng, rad(30)))
        self.assertTrue(not util.in_range_d(rng, rad(330)))
        self.assertTrue(util.in_range_d(rng, rad(50)))
        self.assertTrue(util.in_range_d(rng, rad(50+360)))
        self.assertTrue(util.in_range_d(rng, rad(50-360)))
        self.assertTrue(not util.in_range_d(rng, rad(350)))
        self.assertTrue(not util.in_range_d(rng, rad(350+360)))
        self.assertTrue(not util.in_range_d(rng, rad(350-360)))

        # rng = [0., util.rad(360)]
        # self.assertTrue(util.in_range_d(rng, rad(0)))
        # self.assertTrue(util.in_range_d(rng, rad(180)))
        # self.assertTrue(not util.in_range_d(rng, rad(360)))
