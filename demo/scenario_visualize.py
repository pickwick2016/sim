"""
显示场景.
"""

import sys
sys.path.append('../')

from sim.event import StepEvent
from sim import Scenario
from sim.common import Uav, Radar, Jammer
from sim.visualize import RenderView, QtRenderView
import time


def add_uav(scene):
    scene.add(Uav(tracks=[[150, 150], [0, 0]], speed=5.0))
    pass


def main():
    renderer = QtRenderView()

    scene = Scenario(end=30)
    scene.add(Jammer(pos=[-30, 30]))
    radar = scene.add(Radar(pos=[0, 0], max_r=150, error_d=1, error_r=10))
    scene.add(Uav(name='uav-1', tracks=[[150, 0], [0, 0]], speed=10.0, two_way=False))
    # scene.add(Uav(name='uav-2', tracks=[[-150, 150], [0, 0]], speed=10.0))

    scene.step_handlers.append(lambda s: time.sleep(0.01))
    scene.step_handlers.append(lambda s: print(s.clock_info))
    scene.step_handlers.append(
        StepEvent(entity=radar, evt=lambda r: print('ret:', r.current_results)))
    # scene.step_handlers.append(StepEvent(times=[10, 20, 30], evt=add_uav))

    scene.reset()
    while scene.step():
        renderer.render(scene)


if __name__ == '__main__':
    main()
    print('--- over ---')
