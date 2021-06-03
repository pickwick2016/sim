"""
建立场景，并将场景信息通过 UDP 发送.
"""

import os
import sys
sys.path.append(os.getcwd())

from sim.common import Uav, Jammer, Receiver, UdpSender
from sim import Scenario


def main():
    scene = Scenario(end=60, mode='')
    scene.add(Jammer(name='jammer', pos=[10, 10]))
    scene.add(Receiver(name='recv-1', pos=[0, 0]))
    scene.add(Uav(tracks=[(100, 100, 50), (0, 0, 50)]))

    scene.add_step_listener(UdpSender(ip='127.0.0.1'))
    scene.run()


if __name__ == '__main__':
    main()
    print('--- over ---')
