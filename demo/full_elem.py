"""
全要素场景仿真.
"""

from __future__ import annotations

import os
import sys

sys.path.append(os.getcwd())

from typing import List

from sim import Scenario, vec
from sim.event import StepEvent
from sim.common import Laser, LaserState, Receiver, Radar, EoDetector, EoState, Jammer, Uav
from sim.visualize import make_view


def main():
    view = make_view('qt', world=(-100, 1100, 1100, -100))

    scene = Scenario(end=200)

    scene.add(Radar(name='radar', pos=(0, 0)))
    scene.add(Receiver(name='receiver', pos=(10, 10)))
    eo = scene.add(EoDetector(name='eo', pos=(-10, 10)))
    jammer = scene.add(Jammer(name='jammer', pos=(10, -10)))
    laser = scene.add(Laser(name='laser', pos=(-10, -10)))

    h = 50  # 飞行高度.
    tracks = [(1000, 0, h), (100, 0, h)]
    uav = scene.add(Uav(tracks=tracks, life=60 * 3, speed=5))

    scene.step_handlers.append(lambda s: view.render(s))
    scene.step_handlers.append(Commander())
    scene.step_handlers.append(lambda s: print(s.clock_info[0]))
    scene.step_handlers.append(
        StepEvent(entity=uav, evt=lambda e: print('uav: {}'.format(e.position))))
    scene.step_handlers.append(
        StepEvent(entity=jammer, evt=lambda e: print('jammer: {}'.format(e.power_on))))
    scene.step_handlers.append(StepEvent(
        entity=eo, evt=lambda e: print('eo: {} - {}'.format(e.state, e.dir))))
    scene.step_handlers.append(StepEvent(entity=laser, evt=lambda e: print(
        'laser: {} - {} - {}'.format(e.state, e.power_on, e.dir))))

    scene.run()


class Commander:
    """ 指控. """

    def __init__(self) -> None:
        self.radar: Radar = None
        self.recv: Receiver = None
        self.eo: EoDetector = None
        self.laser: Laser = None
        self.jammer: Jammer = None
        self.threads: List = []
        self.thread_sources = {}

    def __call__(self, scene: Scenario):
        """ 根据场景，决策和控制防控设备. """
        self.radar = scene.find('radar')
        self.recv = scene.find('receiver')
        self.eo = scene.find('eo')
        self.laser = scene.find('laser')
        self.jammer = scene.find('jammer')

        self.update_threads(scene)
        self.decide_and_action(scene)

    def update_threads(self, scene: Scenario):
        # 更新self.threads
        pass

    def decide_and_action(self, scene: Scenario):
        # 根据threads列表，做决策和动作。
        if self.radar.result is not None and self.eo.state != EoState.Track:
            self.eo.guide(vec.vec2(self.radar.result[0].value))

        if self.eo.result is not None and self.laser.state != LaserState.Lock:
            self.laser.guide(self.eo.result.value)

        if self.radar.result is not None:
            r = self.radar.result[0].value[-1]
            if r < 800:
                self.jammer.switch(True)

        if self.radar.result is not None:
            r = self.radar.result[0].value[-1]
            if r < 500 and self.laser.state == LaserState.Lock:
                self.laser.switch(True)


if __name__ == '__main__':
    main()
