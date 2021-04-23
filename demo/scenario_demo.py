"""
场景 Demo.
"""


import sys
sys.path.append('../')

from sim import Scenario
from sim.common import Uav, Jammer, Radar
from sim.event import TimeEvent


def print_scene(scene):
    """ 打印场景信息. """
    tt = scene.clock_info()
    print('{:.2f}'.format(tt[0]))

    for e in scene.entities:
        if info := e.info():
            print(info)


def switch_jammer(scene):
    """ 切换干扰机开关. """
    if jammer := scene.find('jammer-1'):
        jammer.power_on = not jammer.power_on


def main():
    scene = Scenario(end=20)
    scene.step_handlers.append(print_scene)
    scene.step_handlers.append(TimeEvent(times=[5, 11], evt=switch_jammer))

    scene.add(Jammer(name='jammer-1', pos=[0, 0]))
    scene.add(Uav(name='uav-1', tracks=[[0, 0], [10, 10]], two_way=True))

    scene.reset()
    scene.run()


if __name__ == '__main__':
    main()
    print('--- over ---')
