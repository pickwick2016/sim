"""
全要素场景仿真.
"""

from __future__ import annotations

import sys
sys.path.append('../')

from sim.visualize import make_view
from sim.common import Laser, Receiver, Radar, EoDetector, Jammer, Uav
from sim.event import StepEvent
from sim import Scenario, vec


def main():
    view = make_view('qt')

    scene = Scenario(end=300)

    scene.add(Radar(name='radar', pos=(0, 0)))
    scene.add(Receiver(name='receiver', pos=(10, 10)))
    scene.add(EoDetector(name='eo', pos=(-10, 10)))
    scene.add(Jammer(name='jammer', pos=(10, -10)))
    scene.add(Laser(name='laser', pos=(-10, -10)))

    h = 50  # 飞行高度.
    tracks = [(500, 0, h), (0, 0, h)]
    scene.add(Uav(name='uav', tracks=tracks, life=60*3, speed=5))

    scene.step_handlers.append(lambda s: view.render(s))
    scene.step_handlers.append(
        StepEvent(entity='uav', evt=lambda u: print(u.clock_info[0], u.position)))
    scene.step_handlers.append(Commander())

    scene.run()


class Commander:
    """ 指控. """

    def __call__(self, scene: Scenario):
        """ 根据场景，决策和控制防控设备. """
        uav = scene.find('uav')
        jammer = scene.find('jammer')
        if uav and jammer:
            d = vec.dist(jammer.position, uav.position)
            if d < 100:
                jammer.power_on = True
            else:
                jammer.power_on = False


if __name__ == '__main__':
    main()
