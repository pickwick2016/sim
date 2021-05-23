import unittest
import numpy as np
import math
from functools import partial

from sim import Scenario, Entity
from sim.event import StepEvent
from sim.common import Uav, EoDetector, util
from sim import vec

from tests import Target, ResultRecord


class TestEo(unittest.TestCase):
    """ 测试光电传感器. """

    def test_create(self):
        """ 测试创建. """
        eo = EoDetector(pos=[0, 0])
        self.assertTrue(eo is not None)

        eo = EoDetector(pos=[0, 0], fov=0.3, error=0.01)
        self.assertTrue(eo is not None)

        eo = EoDetector(pos=[0, 0], fov=0.3, error=0.01, max_r=20)
        self.assertTrue(eo is not None)

    def test_detect(self):
        """ 测试检测功能. """
        eo = EoDetector(pos=[0, 0])
        self.assertAlmostEqual(eo.dir[0], 0.0)  # 视场指向是0.

        obj = Target(pos=[10, 10])  # 视场外目标.
        ret = eo.detect(obj)
        self.assertTrue(ret is None)

        eo.guide([util.rad(45)], True) # 引导视场指向
        self.assertAlmostEqual(eo.dir[0], util.rad(45))  # 视场指向是0.
        ret = eo.detect(obj) 
        self.assertTrue(ret is not None)

    def test_run_1(self):
        """ 测试单目标. """
        # 测试1.
        scene = Scenario(end=30)
        eo = scene.add(EoDetector(pos=[0, 0]))  # 默认探测器.
        scene.add(Target(pos=[0, 5]))
        recorder = ResultRecord(eo, attr='result')
        scene.step_handlers.append(recorder)
        scene.run()

        self.assertTrue(len(recorder.results) == 0)  # 没有引导，没有结果.
        
        # 测试2.
        scene = Scenario(end=30)
        eo = scene.add(EoDetector(pos=[0, 0]))  # 默认探测器.
        scene.add(Target(pos=[5, 0]))  # 静止目标.

        recorder = ResultRecord(eo, attr='result')
        scene.step_handlers.append(recorder)

        eo.guide([util.rad(90.0)])  # 有正确引导
        scene.run(reset=False)

        self.assertTrue(len(recorder.results) == recorder.counter)  # 有引导，有结果.
        values = [ret.value for ret in recorder.results]
        self.assertTrue(len(set(values)) == 1)  # 静止目标，结果唯一

        # 测试3.
        scene = Scenario(end=30)
        eo = scene.add(EoDetector(pos=[0, 0]))  # 默认探测器.
        obj = scene.add(Target(pos=[0, 50], vel=[1, 0]))  # 运动目标
        recorder = ResultRecord(eo, attr='result')
        scene.step_handlers.append(recorder)

        eo.guide([util.rad(0.0)])  # 有正确引导；立刻起效，不然会被甩开
        scene.run(reset=False)

        self.assertTrue(len(recorder.results) == recorder.counter)   # 有引导，有结果.
        values = [ret.value for ret in recorder.results]
        self.assertTrue(len(values) == len(set(values)))  # 运动目标，结果不同

        # 测试4.
        scene = Scenario(end=30)
        eo = scene.add(EoDetector(pos=[0, 0]))  # 默认探测器.
        obj = scene.add(Target(pos=[0, 50], vel=[1, 0], life=10.0))  # 运动目标, 生命为10.
        recorder = ResultRecord(eo, attr='result')
        scene.step_handlers.append(recorder)

        eo.guide([util.rad(0.0)])  # 有正确引导；立刻起效，不然会被甩开
        scene.run(reset=False)

        self.assertTrue(101 >= len(recorder.results) >= 99)   # 有引导，有结果.
        values = [ret.value for ret in recorder.results]
        self.assertTrue(len(values) == len(set(values)))  # 运动目标，结果不同

    def test_run_2(self):
        """ 测试场景下运行. """
        def guide_eo(scene):
            obj, eo = scene.find('obj'), scene.find('eo')
            aer = util.polar(eo.position, obj.position)
            eo.guide(aer[0:-1])

        scene = Scenario(end=30)

        eo = scene.add(EoDetector(name='eo', pos=[0, 0]))
        obj = scene.add(Target(name='obj', pos=[100, 100], vel=[1, 0], life=20.0))

        scene.step_handlers.append(StepEvent(times=5, evt=guide_eo))
           
        records = ResultRecord(eo, attr='result')
        scene.step_handlers.append(records)
        scene.run()

        self.assertTrue(151 >= len(records.results) >= 149)
        