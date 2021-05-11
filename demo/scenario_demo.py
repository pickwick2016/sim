"""
场景 Demo.
"""

import time
import sys
sys.path.append('../')

from sim import Scenario
from sim.common import Uav, Jammer, Radar
from sim.event import TimeEvent
from sim.visualize import QtRenderView


def print_scene(scene):
    """ 打印场景信息. """
    tt = scene.clock_info
    print('{:.2f}'.format(tt[0]))

    for e in scene.entities:
        if info := e.info():
            print(info)


def switch_jammer(jammer):
    """ 切换干扰机开关. """
    assert jammer
    jammer.power_on = not jammer.power_on


def main():
    renderer = QtRenderView()

    scene = Scenario(end=20)
    scene.step_handlers.append(print_scene)
    scene.step_handlers.append(lambda s: time.sleep(0.01))

    jammer = scene.add(Jammer(name='jammer-1', pos=[0, 0]))
    jammer.step_handlers.append(TimeEvent(times=[5, 11], evt=switch_jammer))

    scene.add(Uav(name='uav-1', tracks=[[100, 100], [0, 0]], two_way=True, speed=10))

    scene.reset()
    while scene.step():
        renderer.render(scene)


if __name__ == '__main__':
    main()
    print('--- over ---')
