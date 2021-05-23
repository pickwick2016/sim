import unittest
import math
import random

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

    def test_rad_deg(self):
        from sim.common.util import rad, deg
        pi2 = math.pi * 2
        pi = math.pi
        
        self.assertAlmostEqual(deg(0.0), 0.0)
        self.assertAlmostEqual(deg(pi), 180.0)
        self.assertAlmostEqual(deg(pi / 6), 30.0)
        self.assertAlmostEqual(deg(-pi / 6), 330.0)
        self.assertAlmostEqual(deg(pi2), 0.0)

        self.assertAlmostEqual(rad(0.0), 0.0)
        self.assertAlmostEqual(rad(180), pi)
        self.assertAlmostEqual(rad(30), pi / 6)
        self.assertAlmostEqual(rad(-30), pi2 - pi / 6)
        self.assertAlmostEqual(rad(360), 0.0)


    def test_angle(self):
        from sim.common.util import rad, deg
        d = util.angle(5, 5)
        self.assertAlmostEqual(d, 0.0)

        self.assertAlmostEqual(util.angle(15, 45), 30)
        self.assertAlmostEqual(util.angle(375, 45), 30)
        self.assertAlmostEqual(util.angle(-345, 45), 30)
        self.assertAlmostEqual(util.angle(15, 405), 30)
        self.assertAlmostEqual(util.angle(15, -315), 30)
        self.assertAlmostEqual(util.angle(375, -315), 30)
        self.assertAlmostEqual(util.angle(-345, 405), 30)

        self.assertAlmostEqual(util.angle(rad(15), rad(45), 'r'), rad(30))
        self.assertAlmostEqual(util.angle(rad(375), rad(45), 'r'), rad(30))
        self.assertAlmostEqual(util.angle(rad(-345), rad(45), 'r'), rad(30))
        self.assertAlmostEqual(util.angle(rad(15), rad(405), 'r'), rad(30))
        self.assertAlmostEqual(util.angle(rad(15), rad(-315), 'r'), rad(30))
        self.assertAlmostEqual(util.angle(rad(375), rad(-315), 'r'), rad(30))
        self.assertAlmostEqual(util.angle(rad(-345), rad(405), 'r'), rad(30))

        for _ in range(10):
            a, b = random.random() * 360, random.random() * 360
            self.assertEqual(util.angle(a, b), util.angle(b, a))

        for _ in range(10):
            a, b = random.random() * math.pi * 2, random.random() * math.pi * 2
            self.assertEqual(util.angle(a, b, unit='r'), util.angle(b, a, unit='r'))
