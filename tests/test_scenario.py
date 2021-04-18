import copy
import unittest

import numpy as np

from sim import Scenario, Entity
from sim import vec
from sim.basic import SimClock


class TestScenario(unittest.TestCase):
    """ 测试 Scenario 文件. """

    def test_entity(self):
        """ 测试 entity. """
        # 测试 id
        e1 = Entity()
        e2 = Entity()
        self.assertTrue(e1.id != e2.id)

        e1c = copy.copy(e1)
        self.assertTrue(e1c.id == e1.id)

        e1c = copy.deepcopy(e1)
        self.assertTrue(e1c.id == e1.id)

        # 测试其他.
        e3 = Entity(name='ent1')
        self.assertTrue(e3.id != e2.id)
        self.assertTrue(e3.name == 'ent1')

        self.assertTrue(e3.is_active())

    def test_scenario_manage(self):
        """ 测试 Scenario 管理功能. """
        scene = Scenario()

        obj = scene.add(Entity())
        self.assertTrue(obj)
        self.assertEqual(len(scene.entities), 1)

        obj2 = scene.add(obj)
        self.assertTrue(obj is obj2)
        self.assertEqual(len(scene.entities), 1)

        obj = scene.add(Entity())
        self.assertTrue(obj)
        self.assertEqual(len(scene.entities), 2)

        scene.remove(obj)
        self.assertEqual(len(scene.entities), 1)

        scene.clear()
        self.assertEqual(len(scene.entities), 0)

    def test_scenario_run(self):
        scene = Scenario()
        np.testing.assert_almost_equal(vec.vec(scene.clock_info()), vec.vec([0, 0.1]))

        tt = scene.step()
        self.assertTrue(tt == scene.clock_info())
        np.testing.assert_almost_equal(vec.vec(scene.clock_info()), vec.vec([0.1, 0.1]))

        scene.run()
        np.testing.assert_almost_equal(vec.vec(scene.clock_info()), vec.vec([10.1, 0.1]))

    def test_sim_clock(self):
        # 测试默认构造
        clock = SimClock()
        self.assertAlmostEqual(clock.start, 0.0)
        self.assertAlmostEqual(clock.end, 10.0)
        self.assertAlmostEqual(clock.dt, 0.1)
        self.assertAlmostEqual(clock.now, 0.0)

        # 测试定制构造
        clock = SimClock(start=1.0, end=20.0, step=0.5)
        self.assertAlmostEqual(clock.start, 1.0)
        self.assertAlmostEqual(clock.end, 20.0)
        self.assertAlmostEqual(clock.dt, 0.5)
        self.assertAlmostEqual(clock.now, 1.0)

        # 测试默认构造下方法.
        clock = SimClock()
        np.testing.assert_almost_equal(vec.vec(clock.info()), vec.vec([0.0, 0.1]))

        tt = clock.step()
        self.assertTrue(tt == clock.info())
        np.testing.assert_almost_equal(vec.vec(clock.info()), vec.vec([0.1, 0.1]))

        while True:
            tt = clock.step()
            if not tt:
                break
        self.assertTrue(tt is None)
        np.testing.assert_almost_equal(vec.vec(clock.info()), vec.vec([10.1, 0.1]))
