import copy
import unittest

import numpy as np

from sim import Scenario, Entity
from sim import vec
from sim.basic import SimClock


class TestScenario(unittest.TestCase):
    """ 测试 Scenario 模块. """

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

        obj = scene.add(Entity(name='obj_1'))
        self.assertTrue(obj)
        self.assertEqual(len(scene.entities), 1)

        obj1b = scene.add(obj)
        self.assertTrue(obj is obj1b)
        self.assertEqual(len(scene.entities), 1)

        obj2 = scene.add(Entity(name='obj_2'))
        self.assertTrue(obj2)
        self.assertEqual(len(scene.entities), 2)

        self.assertTrue(scene.find('obj_1') is obj)
        self.assertTrue(scene.find(obj.id) is obj)
        self.assertTrue(scene.find(obj) is obj)

        self.assertTrue(scene.find('obj_2') is obj2)
        self.assertTrue(scene.find(obj2.id) is obj2)
        self.assertTrue(scene.find(obj2) is obj2)

        scene.remove(obj)
        self.assertEqual(len(scene.entities), 1)

        scene.clear()
        self.assertEqual(len(scene.entities), 0)

    def test_scenario_run(self):
        """ 测试场景运行. """
        scene = Scenario()
        np.testing.assert_almost_equal(
            vec.vec(scene.clock_info), vec.vec([0, 0.]))

        time_rec = []

        scene.step_handlers.append(
            lambda s: time_rec.append(s.clock_info[0]))

        tt = scene.step()
        self.assertTrue(tt == scene.clock_info)
        np.testing.assert_almost_equal(
            vec.vec(scene.clock_info), vec.vec([0.1, 0.1]))

        scene.run()
        np.testing.assert_almost_equal(
            vec.vec(scene.clock_info), vec.vec([10.1, 0.1]))
        self.assertAlmostEqual(time_rec[0], 0.0)
        self.assertAlmostEqual(time_rec[-1], 10.0)

    def test_scenario_msg(self):
        """ 测试场景消息. """
        obj = Entity()
        self.assertFalse(obj.send_msg('obj_2', 'msg'))

        class MsgEntity(Entity):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.msg_counter = 0

            def on_msg(self, sender, msg):
                self.msg_counter += msg

        scene = Scenario()
        obj1 = scene.add(MsgEntity(name='obj_1'))
        obj1.step_handlers.append(lambda obj: obj.send_msg('obj_2', 1))

        obj2 = scene.add(MsgEntity(name='obj_2'))
        obj2.step_handlers.append(lambda obj: obj.send_msg('obj_1', 1))

        scene.run()

        self.assertTrue(obj1.msg_counter >= 100)
        self.assertTrue(obj2.msg_counter >= 100)

    def test_sim_clock(self):
        """ 测试仿真时钟. """
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
        np.testing.assert_almost_equal(
            vec.vec(clock.info()), vec.vec([0.0, 0.0]))

        tt = clock.step()
        self.assertTrue(tt == clock.info())
        np.testing.assert_almost_equal(
            vec.vec(clock.info()), vec.vec([0.1, 0.1]))

        while True:
            tt = clock.step()
            if not tt:
                break
        self.assertTrue(tt is None)
        np.testing.assert_almost_equal(
            vec.vec(clock.info()), vec.vec([10.1, 0.1]))

    def test_multi_entity(self):
        """ 测试多实体场景. """
        import time
        start_t = time.time()

        scene = Scenario()

        class CounterEntity(Entity):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.counter = 0
                self.max_counter = 0

            def access(self, others):
                max_num = 0
                for other in others:
                    self.counter += 1
                    if max_num < other.max_counter:
                        max_num = other.max_counter
                self.max_counter = max_num + 1

        for _ in range(200):
            scene.add(CounterEntity())
        scene.step_handlers.append(lambda s: print(s.clock_info))
        scene.reset()
        scene.run()
        self.assertEqual(len(scene.entities), 100)
        self.assertEqual(scene.entities[0].counter, 99 * 101)
        self.assertEqual(scene.entities[10].max_counter, 101)

        dt = time.time() - start_t
        print('total_time: 10s - real_time: {}s'.format(dt))
        self.assertTrue(dt < 10.0)
