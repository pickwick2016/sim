"""
场景 Demo.
"""

import sys
import time

sys.path.append('../')

from sim import Scenario
from sim.common import Uav, Jammer, JammerType, Receiver
from sim.event import StepEvent
from sim import visualize


def print_scene(scene):
    """ 打印场景信息. """
    print('{:.2f}'.format(scene.clock_info[0]))
    for e in scene.entities:
        if info := str(e):
            print(info)


def switch_jammer(jammer):
    """ 切换干扰机开关. """
    assert jammer
    jammer.power_on = not jammer.power_on


def main():
    renderer = visualize.make_view(typename='qt', win_size=(1000, 600))

    scene = Scenario(end=60)
    scene.step_handlers.append(print_scene)
    scene.step_handlers.append(lambda s: time.sleep(0.01))

    jammer = scene.add(Jammer(name='jammer-1', pos=[0, 0], type=JammerType.DataLink))
    scene.step_handlers.append(StepEvent(times=[13, 30], entity=jammer, evt=switch_jammer))

    receiver = scene.add(Receiver(name='recv-1', pos=[0, 0]))
    
    # jammer_gps = scene.add(Jammer(name='jammer-2', pos=[0, 0], type=JammerType.GPS, max_r=100))
    # scene.step_handlers.append(StepEvent(times=[10, 15], entity=jammer_gps, evt=switch_jammer))

    scene.add(Uav(name='uav-1', tracks=[[100, 100], [0, 0]], two_way=True, speed=10, life=60))

    scene.reset()
    while scene.step():
        renderer.render(scene)


if __name__ == '__main__':
    main()
    print('--- over ---')
