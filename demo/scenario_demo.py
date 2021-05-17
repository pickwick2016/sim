"""
场景 Demo.
"""

import sys
import time

sys.path.append('../')

from sim import Scenario
from sim.common import Uav, Jammer
from sim.event import StepEvent
from sim import visualize


def print_scene(scene):
    """ 打印场景信息. """
    print('{:.2f}'.format(scene.clock_info[0]))
    for e in scene.entities:
        if info := e.info():
            print(info)


def switch_jammer(jammer):
    """ 切换干扰机开关. """
    assert jammer
    jammer.power_on = not jammer.power_on


def main():
    renderer = visualize.make_view(typename='qt', win_size=(1000, 600))

    scene = Scenario(end=20)
    scene.step_handlers.append(print_scene)
    scene.step_handlers.append(lambda s: time.sleep(0.01))

    jammer = scene.add(Jammer(name='jammer-1', pos=[0, 0], max_r=60))
    scene.step_handlers.append(StepEvent(times=[5, 12], entity=jammer, evt=switch_jammer))

    scene.add(Uav(name='uav-1', tracks=[[100, 100], [0, 0]], two_way=True, speed=10))

    scene.reset()
    while scene.step():
        renderer.render(scene)


if __name__ == '__main__':
    main()
    print('--- over ---')
