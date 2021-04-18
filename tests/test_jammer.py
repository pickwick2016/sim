import unittest
import numpy as np

from sim.common import Jammer
from sim import vec


class TestJammer(unittest.TestCase):
    """ 测试 Jammer """

    def test_create(self):
        jammer = Jammer()
        self.assertTrue(jammer is not None)

        jammer = Jammer(pos=[1, 1])
        np.testing.assert_almost_equal(jammer.position, vec.vec([1, 1]))
