import unittest
import math

import numpy as np

from sim import vec


class TestVec(unittest.TestCase):
    """ 测试 vec 模块. """

    def test_dist(self):
        #  测试 dist
        v1, v2, v3 = vec.vec([0, 0]), vec.vec([1, 1]), vec.vec([-1, -1])
        self.assertAlmostEqual(vec.dist(v1), 0.0)
        self.assertAlmostEqual(vec.dist(v2), 2 ** 0.5)
        self.assertAlmostEqual(vec.dist(v3), 2 ** 0.5)
        self.assertAlmostEqual(vec.dist(v1, v2), 2 ** 0.5)
        self.assertAlmostEqual(vec.dist(v2, v3), 2 * (2 ** 0.5))

    def test_unit(self):
        # 测试 unit
        v = vec.unit(vec.vec([0, 2]))
        np.testing.assert_almost_equal(v, vec.vec([0, 1]))
        v = vec.unit(vec.vec([0, 0.2]))
        np.testing.assert_almost_equal(v, vec.vec([0, 1]))
        v = vec.unit(vec.vec([0, 0]))
        np.testing.assert_almost_equal(v, vec.vec([0, 0]))

    def test_zeros_like(self):
        # 测试 zeros_like
        v = vec.zeros_like(vec.vec([2]))
        np.testing.assert_almost_equal(v, vec.vec([0]))
        v = vec.zeros_like(vec.vec([0, 2]))
        np.testing.assert_almost_equal(v, vec.vec([0, 0]))
        v = vec.zeros_like(vec.vec([0, 2, 3]))
        np.testing.assert_almost_equal(v, vec.vec([0, 0, 0]))

    def test_angle(self):
        # 测试angle
        v1 = vec.vec([1, 0])
        v2 = vec.vec([2, 2])
        self.assertAlmostEqual(vec.angle(v1, v2), math.pi / 4)

        v1 = vec.vec([1, 0])
        v2 = vec.vec([0, 1])
        self.assertAlmostEqual(vec.angle(v1, v2), math.pi / 2)

        v1 = vec.vec([0, 1])
        v2 = vec.vec([2, 2])
        self.assertAlmostEqual(vec.angle(v1, v2), math.pi / 4)

        v1 = vec.vec([1, 1])
        v2 = vec.vec([2, 2])
        self.assertAlmostEqual(vec.angle(v1, v2), 0)

        v1 = vec.vec([1, 0])
        v2 = vec.vec([0, 0])
        self.assertAlmostEqual(vec.angle(v1, v2), 0)

        v1 = vec.vec([1, 0])
        v2 = vec.vec([-2, 2])
        self.assertAlmostEqual(vec.angle(v1, v2), math.pi * 0.75)

        v1 = vec.vec([3 ** 0.5, 1])
        v2 = vec.vec([1, 0])
        self.assertAlmostEqual(vec.angle(v1, v2), math.pi / 6)

    def test_proj(self):
        # 测试 proj
        v1 = vec.vec([3 ** 0.5, 1])
        v2 = vec.vec([1, 0])
        np.testing.assert_almost_equal(
            vec.proj(v1, v2), vec.vec([3 ** 0.5, 0]))

        v1 = vec.vec([0, 0])
        v2 = vec.vec([1, 0])
        np.testing.assert_almost_equal(vec.proj(v1, v2), vec.vec([0, 0]))
  