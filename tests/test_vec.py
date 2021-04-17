import unittest

import numpy as np

from sim import vec


class TestVec(unittest.TestCase):
    """ 测试 vec 模块. """

    def test_basic(self):
        #  测试 dist
        v1, v2, v3 = vec.vec([0, 0]), vec.vec([1, 1]), vec.vec([-1, -1])
        self.assertAlmostEqual(vec.dist(v1), 0.0)
        self.assertAlmostEqual(vec.dist(v2), 2 ** 0.5)
        self.assertAlmostEqual(vec.dist(v3), 2 ** 0.5)
        self.assertAlmostEqual(vec.dist(v1, v2), 2 ** 0.5)
        self.assertAlmostEqual(vec.dist(v2, v3), 2 * (2 ** 0.5))

        # 测试 unit
        v = vec.unit(vec.vec([0, 2]))
        np.testing.assert_almost_equal(v, vec.vec([0, 1]))
        v = vec.unit(vec.vec([0, 0.2]))
        np.testing.assert_almost_equal(v, vec.vec([0, 1]))
        v = vec.unit(vec.vec([0, 0]))
        np.testing.assert_almost_equal(v, vec.vec([0, 0]))

        # 测试 zeros_like
        v = vec.zeros_like(vec.vec([2]))
        np.testing.assert_almost_equal(v, vec.vec([0]))
        v = vec.zeros_like(vec.vec([0, 2]))
        np.testing.assert_almost_equal(v, vec.vec([0, 0]))
        v = vec.zeros_like(vec.vec([0, 2, 3]))
        np.testing.assert_almost_equal(v, vec.vec([0, 0, 0]))

    def test_move(self):
        # move_to tests
        v0, vt = vec.vec([0, 0]), vec.vec([0, 1])
        vn, ld = vec.move_to(v0, vt, 1)
        self.assertAlmostEqual(ld, 0)
        np.testing.assert_almost_equal(vn, vec.vec([0, 1]))

        vn, ld = vec.move_to(v0, vt, 0.5)
        self.assertAlmostEqual(ld, 0.5)
        np.testing.assert_almost_equal(vn, vec.vec([0, 0.5]))

        vn, ld = vec.move_to(v0, vt, 2)
        self.assertAlmostEqual(ld, -1)
        np.testing.assert_almost_equal(vn, vec.vec([0, 1]))

        # move_step tests
        v0, vt = vec.vec([0, 1]), vec.vec([0, 2])
        vn, ld = vec.move_step(v0, vt, 1)
        self.assertAlmostEqual(ld, 0)
        np.testing.assert_almost_equal(vn, vec.vec([0, 1]))

        vn, ld = vec.move_step(v0, vt, 0.5)
        self.assertAlmostEqual(ld, 0.5)
        np.testing.assert_almost_equal(vn, vec.vec([0, 0.5]))

        vn, ld = vec.move_step(v0, vt, 2)
        self.assertAlmostEqual(ld, -1)
        np.testing.assert_almost_equal(vn, vec.vec([0, 1]))
