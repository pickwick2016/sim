"""
测试 common 对象在场景中的创建.
"""

import os
import sys
sys.path.append(os.getcwd())

import time
from sim import Scenario
from sim.common import Uav, Radar, Jammer, Laser, Receiver, EoDetector


def setup_scene(scene: Scenario):
    """ 初始化场景. """
    scene.add(Uav(tracks=[[0, 0], [10, 10]]))
    scene.add(Radar())
    scene.add(EoDetector())
    scene.add(Receiver())
    scene.add(Laser())
    scene.add(Jammer())
    scene.step_listeners.append(lambda s: print(time.time()))


def main():
    scene = Scenario(end=60)
    setup_scene(scene)
    scene.run()


if __name__ == '__main__':
    main()
    print('--- over ---')
