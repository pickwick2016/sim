"""
显示场景.
"""

import time
import sys
sys.path.append('../')

from sim.visualize import QtRenderView
from sim.common import Uav, Radar, Jammer
from sim import Scenario


def main():
    renderer = QtRenderView()

    scene = Scenario(end=60)
    scene.add(Jammer(pos=[-30, 30]))
    scene.add(Radar(pos=[0, 30]))
    scene.add(Uav(name='uav-1', tracks=[[0, 0], [150, 150]], speed=10.0))

    scene.step_handlers.append(lambda s: time.sleep(0.01))
    scene.step_handlers.append(lambda s: print(s.clock_info))

    scene.reset()
    while scene.step():
        renderer.render(scene)


if __name__ == '__main__':
    main()
    print('--- over ---')
