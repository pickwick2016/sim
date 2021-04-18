import unittest

from sim.common import Uav

class TestUav(unittest.TestCase):
    """ 测试 UAV """
    
    def test_create(self):
        uav = Uav()
        self.assertTrue(uav is not None)