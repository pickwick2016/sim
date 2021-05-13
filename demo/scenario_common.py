"""
测试 common 对象在场景中的创建.
"""

import sys
sys.path.append('../')


from sim.common import Uav, Radar, Jammer
from sim import Scenario


def setup_scene(scene):
    """ 初始化场景. """
    scene.add(Uav(tracks=[[0, 0], [10, 10]]))
    scene.add(Radar())
    scene.add(Jammer())


def main():
    scene = Scenario()
    setup_scene(scene)
    scene.run()


if __name__ == '__main__':
    main()
    print('--- over ---')
