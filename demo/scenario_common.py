"""
测试 common 对象在场景中的创建.
"""

import sys
sys.path.append('../')

from sim import Scenario
from sim.common import Uav, Radar, Jammer

def setup_scene(scene):
    scene.add(Uav())
    scene.add(Radar())
    scene.add(Jammer())

def main():
    scene = Scenario()
    setup_scene(scene)
    scene.run()

if __name__ == '__main__':
    main()
    print('--- over ---')

