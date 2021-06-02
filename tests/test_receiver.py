import unittest
from functools import reduce
import math
import numpy as np

from sim import Scenario
from sim.event import StepEvent
from sim.common import Receiver, util
from sim import vec

from tests import Target, ResultRecord


class TestReceiver(unittest.TestCase):
    """ 测试接收机. """

    def test_create(self):
        """ 测试创建. """
        recv = Receiver(pos=[0, 0])
        self.assertTrue(recv is not None)

        recv = Receiver(pos=[0, 0], rate=2.0, max_r=20)
        self.assertTrue(recv is not None)

    def test_detect(self):
        """ 测试检测功能. """

        # 默认侦察设备.
        recv = Receiver(pos=[0, 0])

        obj = Target(pos=[10, 0])
        ret = recv.detect(obj)
        self.assertTrue(ret is None)  # 无法侦察没有signal属性的实体.

        obj = Target(pos=[10, 0], signal=1.0)
        ret = recv.detect(obj)
        self.assertTrue(ret is not None)  # 侦察没有signal属性的实体.

        # 带有范围的侦察设备
        recv = Receiver(pos=[0, 0], max_r=10)  # 最大侦察距离10

        ret1 = recv.detect(Target(pos=[11, 0], signal=1.0))
        self.assertTrue(ret1 is None)  # 无法侦察范围外实体

        ret2 = recv.detect(Target(pos=[9, 0], signal=1.0))
        self.assertTrue(ret2 is not None)  # 能够侦察范围外实体
        self.assertAlmostEqual(ret2, math.pi * 0.5)

    def test_run_1(self):
        """ 单目标侦察测试. """

        # 测试1.
        scene = Scenario(end=30)
        recv = scene.add(Receiver(pos=(0, 0)))  # 默认探测器.
        scene.add(Target(pos=(0, 5), vel=(1, 0), signal=1.0))  # 运动目标
        recorder = ResultRecord(recv)
        scene.step_listeners.append(recorder)
        scene.run()

        self.assertTrue(31 >= len(recorder.results) >= 29)
        for ret in recorder.results:
            self.assertTrue(isinstance(ret, list))
            self.assertTrue(len(ret) == 1)

        times = [ret[0].time for ret in recorder.results]
        self.assertTrue(len(times) == len(set(times)))
        times_diff = [times[i] - times[i-1] for i in range(1, len(times))]
        for val in times_diff:
            self.assertTrue(val >= recv.rate)

        values = [ret[0].value for ret in recorder.results]
        self.assertTrue(len(values) == len(set(values)))

        # 测试2.
        scene = Scenario(end=30)
        recv = scene.add(Receiver(pos=(0, 0), max_r=15))  # 带最大距离的探测器.
        obj = scene.add(
            Target(pos=[5, 0], vel=(1, 0), signal=1.0))
        recorder = ResultRecord(recv)
        scene.step_listeners.append(recorder)
        scene.run()

        self.assertTrue(11 >= len(recorder.results) >= 9)
        for ret in recorder.results:
            self.assertTrue(isinstance(ret, list))
            self.assertTrue(len(ret) == 1)

        times = [ret[0].time for ret in recorder.results]
        self.assertTrue(len(times) == len(set(times)))
        times_diff = [times[i] - times[i-1] for i in range(1, len(times))]
        for val in times_diff:
            self.assertTrue(val >= recv.rate)

        # 测试3.
        scene = Scenario(end=30)
        recv = scene.add(Receiver(pos=(0, 0), rate=0.0))  # 无探测数据率限制的探测器.
        obj = scene.add(
            Target(pos=[5, 0], vel=(1, 0), signal=1.0))
        recorder = ResultRecord(recv)
        scene.step_listeners.append(recorder)
        scene.run()

        self.assertTrue(301 >= len(recorder.results) >= 299)
        for ret in recorder.results:
            self.assertTrue(isinstance(ret, list))
            self.assertTrue(len(ret) == 1)

        times = [ret[0].time for ret in recorder.results]
        self.assertTrue(len(times) == len(set(times)))
        times_diff = [times[i] - times[i-1] for i in range(1, len(times))]
        for val in times_diff:
            self.assertTrue(val >= recv.rate)

        # 测试4.
        scene = Scenario(end=30)
        recv = scene.add(Receiver(pos=[0, 0], rate=0.0))
        scene.add(Target(pos=[5, 0], life=10.0, signal=1.0))  # 寿命不超过10的目标.
        recorder = ResultRecord(recv)
        scene.step_listeners.append(recorder)
        scene.run()

        self.assertTrue(len(recorder.results) > 0)
        last = recorder.results[-1][0]
        self.assertTrue(last.time <= 10.0)


    def test_run_2(self):
        """ 多目标侦察测试. """
        scene = Scenario(end=30)
        
        recv = scene.add(Receiver(pos=[0, 0]))
        scene.add(Target(pos=(0, 5), vel=(1, 0), signal=1.0))
        scene.add(Target(pos=(0, -10), vel=(1, 0), signal=1.0))

        recorder = ResultRecord(recv)
        scene.step_listeners.append(recorder)
        scene.run()

        self.assertTrue(31 >= len(recorder.results) >= 29)
        for ret in recorder.results:
            self.assertTrue(isinstance(ret, list))
            self.assertTrue(len(ret) == 2)

        values = [util.norm_angle(ret[0].value - ret[1].value, unit='r')
                  for ret in recorder.results]
        for val in values:
            self.assertNotAlmostEqual(val, 0)
