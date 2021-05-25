import unittest
import numpy as np
from functools import partial

from sim import Scenario, Entity
from sim.event import StepEvent
from sim.common import Laser, rules, util
from sim import vec

from tests import Target, ResultRecord


class TestLaser(unittest.TestCase):
    """ 测试光电传感器. """

    def test_create(self):
        """ 测试创建. """
        laser = Laser(pos=[0, 0])
        self.assertTrue(laser is not None)

        laser = Laser(pos=[0, 0], fov=0.3)
        self.assertTrue(laser is not None)

        laser = Laser(pos=[0, 0], fov=0.3, max_r=20)
        self.assertTrue(laser is not None)

    def test_detect(self):
        """ 测试检测功能. """
        laser = Laser(pos=[0, 0])
        self.assertAlmostEqual(laser.dir[0], 0.0)  # 视场指向是0.

        obj = Target(pos=[10, 10])  # 视场外目标.
        ret = laser.detect(obj)
        self.assertTrue(ret is None)

        laser.guide([util.rad(45)], True) # 引导视场指向
        self.assertAlmostEqual(laser.dir[0], util.rad(45))  # 视场指向是0.
        ret = laser.detect(obj) 
        self.assertTrue(ret is not None)

    def test_run_detect(self):
        """ 测试单目标. """
        # 测试1.
        scene = Scenario(end=30)
        laser = scene.add(Laser(pos=[0, 0]))  # 默认激光.
        scene.add(Target(pos=[0, 5]))
        recorder = ResultRecord(laser, attr='result')
        scene.step_handlers.append(recorder)
        scene.run()

        self.assertTrue(len(recorder.results) == 0)  # 没有引导，没有结果.
        
        # 测试2.
        scene = Scenario(end=30)
        laser = scene.add(Laser(pos=[0, 0]))  # 默认探测器.
        scene.add(Target(pos=[5, 0]))  # 静止目标.

        recorder = ResultRecord(laser, attr='result')
        scene.step_handlers.append(recorder)

        laser.guide([util.rad(90.0)])  # 有正确引导
        scene.run(reset=False)

        self.assertTrue(len(recorder.results) == recorder.counter)  # 有引导，有结果.
        values = [tuple(ret.value.tolist()) for ret in recorder.results]
        self.assertTrue(len(set(values)) == 1)  # 静止目标，结果唯一

        # 测试3.
        scene = Scenario(end=30)
        laser = scene.add(Laser(pos=[0, 0]))  # 默认探测器.
        obj = scene.add(Target(pos=[0, 50], vel=[1, 0]))  # 运动目标
        recorder = ResultRecord(laser, attr='result')
        scene.step_handlers.append(recorder)

        laser.guide([util.rad(0.0)])  # 有正确引导；立刻起效，不然会被甩开
        scene.run(reset=False)

        self.assertTrue(len(recorder.results) == recorder.counter)   # 有引导，有结果.
        values = [tuple(ret.value.tolist()) for ret in recorder.results]
        self.assertTrue(len(values) == len(set(values)))  # 运动目标，结果不同

        # 测试4.
        scene = Scenario(end=30)
        laser = scene.add(Laser(pos=[0, 0]))  # 默认探测器.
        obj = scene.add(Target(pos=[0, 50], vel=[1, 0], life=10.0))  # 运动目标, 生命为10.
        recorder = ResultRecord(laser, attr='result')
        scene.step_handlers.append(recorder)

        laser.guide([util.rad(0.0)])  # 有正确引导；立刻起效，不然会被甩开
        scene.run(reset=False)

        self.assertTrue(101 >= len(recorder.results) >= 99)   # 有引导，有结果.
        values = [tuple(ret.value.tolist()) for ret in recorder.results]
        # self.assertTrue(len(values) == len(set(values)))  # 运动目标，结果不同

    def test_run_fire(self):
        """ 测试开火. """
        fire = lambda l : l.switch(True)

        # 静态开火，测试最大时间.
        scene = Scenario(end=30)
        laser = scene.add(Laser(work=10, recover=10))
        scene.step_handlers.append(StepEvent(times=1.0, entity=laser, evt=fire))

        recorder1 = ResultRecord(laser, attr='power_on')
        scene.step_handlers.append(recorder1)
        recorder2 = ResultRecord(laser, attr='work_time')
        scene.step_handlers.append(recorder2)

        scene.run()

        self.assertTrue(recorder1.results[-1] == False)
        self.assertAlmostEqual(recorder2.results[-1], 10)

        # 静态开火，测试损坏能力.
        scene = Scenario(end=30)
        laser = scene.add(Laser(name='laser', pos=[0, 0], work=10))
        obj = scene.add(Target(name='obj', pos=[0, 100], damage=5))
        obj.access_rules.append(rules.entity_access_laser)
        scene.step_handlers.append(StepEvent(times=1.0, entity=laser, evt=fire))

        recorder1 = ResultRecord(obj, attr='damage')
        scene.step_handlers.append(recorder1)

        scene.run()

        self.assertTrue(recorder1.results[0] == 5.0)
        self.assertTrue(recorder1.results[-1] <= 0.0)

        # 动态开火
        def guide_and_fire(scene):
            laser, obj = scene.find('laser'), scene.find('obj')
            aer = util.polar(laser.position, obj.position)
            laser.guide(aer[0:-1])
            laser.switch(True)

        scene = Scenario(end=30)
        laser = scene.add(Laser(name='laser', pos=[0, 0], work=10))
        obj = scene.add(Target(name='obj', pos=[0, 100], vel=[1, 0], damage=5))
        obj.access_rules.append(rules.entity_access_laser)

        scene.step_handlers.append(StepEvent(times=1.0, evt=guide_and_fire))

        recorder1 = ResultRecord(obj, attr='damage')
        scene.step_handlers.append(recorder1)

        scene.run()

        self.assertTrue(recorder1.results[0] == 5.0)
        self.assertTrue(recorder1.results[-1] <= 0.0)

        # 动态开火和关火.
        scene = Scenario(end=30)
        laser = scene.add(Laser(name='laser', pos=[0, 0], work=10))
        obj = scene.add(Target(name='obj', pos=[0, 100], vel=[1, 0], damage=5))
        obj.access_rules.append(rules.entity_access_laser)

        scene.step_handlers.append(StepEvent(times=1.0, evt=guide_and_fire))
        scene.step_handlers.append(StepEvent(times=5.0, entity=laser, evt=lambda l: l.switch(False)))

        recorder1 = ResultRecord(obj, attr='damage')
        scene.step_handlers.append(recorder1)

        scene.run()

        self.assertTrue(recorder1.results[0] == 5.0)
        self.assertAlmostEqual(recorder1.results[-1], 1.0)

        
