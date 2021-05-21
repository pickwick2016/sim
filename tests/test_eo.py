import unittest
import numpy as np
import math

from sim import Scenario, Entity
from sim.event import StepEvent
from sim.common import Uav, EoDetector, util
from sim import vec


class Target(Entity):
    """ 测试目标. """

    def __init__(self, pos=[0, 0], speed=None, **kwargs):
        super().__init__(**kwargs)
        self.position = vec.vec(pos)
        self.velocity = vec.vec(speed) if speed else vec.zeros_like(pos)

    def step(self, clock):
        _, dt = clock
        self.position += self.velocity * dt
        pass


class TestEo(unittest.TestCase):
    def test_create(self):
        eo = EoDetector(pos=[0, 0])
        self.assertTrue(eo is not None)

    def test_detect(self):
        obj = Target(pos=[10, 10])
        eo = EoDetector(pos=[0, 0])

        ret = eo.detect(obj)
        self.assertTrue(ret is None)

        eo.guide([math.pi / 4])
        eo.step(None)
        ret = eo.detect(obj)
        self.assertTrue(ret is not None)

        obj = Target(pos=[0, 10])
        eo.guide([0], True)

        ret = eo.detect(obj)
        self.assertTrue(ret is not None)

        eo.guide([math.pi / 4], True)
        ret = eo.detect(obj)
        self.assertTrue(ret is None)

    def test_detect_2(self):
        obj = Target(pos=[0, 10, 10])
        eo = EoDetector(pos=[0, 0, 0])

        ret = eo.detect(obj)
        self.assertTrue(ret is None)

        eo.guide([0, math.pi / 4], True)
        ret = eo.detect(obj)
        self.assertTrue(ret is not None)

    def test_run(self):

        def guide(scene):
            obj, eo = scene.find('obj'), scene.find('eo')
            aer = util.polar(eo.position, obj.position)
            eo.guide(aer[0:-1])
            print('do guide')

        scene = Scenario()

        obj = scene.add(Target(name='obj', pos=[10, 10], speed=[1, 0]))
        eo = scene.add(EoDetector(name='eo', pos=[0, 0]))

        scene.step_handlers.append(StepEvent(times=1, evt=guide))
        scene.step_handlers.append(
            StepEvent(entity=obj, evt=lambda e: print(e.position)))
        scene.step_handlers.append(
            StepEvent(entity=eo, evt=lambda e: print(e.result)))

        scene.run()
