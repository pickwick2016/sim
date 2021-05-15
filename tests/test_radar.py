import unittest
import numpy as np

from sim import Scenario, Entity
from sim.event import StepEvent
from sim.common import Radar, Uav
from sim import vec


class Target(Entity):
    """ 测试目标. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position = vec.vec(kwargs['pos'])
        self.rcs = 0.1


class TestRadar(unittest.TestCase):
    """ 测试 Radar """

    def test_create(self):
        radar = Radar()
        self.assertTrue(radar is not None)

        radar = Radar(pos=[1, 1])
        np.testing.assert_almost_equal(radar.position, vec.vec([1, 1]))

        radar.set_params(search_dt=2.0, track_dt=2.0)
        self.assertAlmostEqual(radar.search_rate, 2.0)
        self.assertAlmostEqual(radar.track_rate, 2.0)
        

    def test_detect(self):
        radar = Radar()
        uav = Target(pos=vec.vec([50, 50]))

        ret = radar.detect(uav)
        self.assertAlmostEqual(ret[0], 50 * 2 ** 0.5)

    def test_step(self):
        scene = Scenario(end=30.0)
        radar = scene.add(Radar())
        target = scene.add(Target(pos=[50, 50]))

        scene.step_handlers.append(StepEvent(times=6.0, evt=lambda s: s.remove(target)))

        ts = set()
        scene.reset()
        while True:
            tt = scene.step()
            rets = radar.results
            ts.add(rets[target.id].time)
            if tt is None:
                break
        tt = sorted(list(ts))
        print(tt)

        