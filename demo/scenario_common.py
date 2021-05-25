"""
测试 common 对象在场景中的创建.
"""

import sys
sys.path.append('../')

import time

from sim.common import Uav, Radar, Jammer
from sim import Scenario


def setup_scene(scene: Scenario):
    """ 初始化场景. """
    scene.add(Uav(tracks=[[0, 0], [10, 10]]))
    scene.add(Radar())
    scene.add(Jammer())
    scene.step_handlers.append(lambda s: print(time.time()))


def main():
    scene = Scenario(mode='realtime')
    setup_scene(scene)
    scene.run()


if __name__ == '__main__':
    main()
    print('--- over ---')
