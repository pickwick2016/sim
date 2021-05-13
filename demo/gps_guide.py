"""
GPS 欺骗策略.
"""

import math
import copy
import random
from typing import Tuple

import sys
sys.path.append('../')

import sim
from sim import Scenario, vec, util
from sim.event import StepEvent
from sim.rl import Environment
from sim.common import Uav, Jammer, Radar


class GpsAgent:
    def __init__(self):
        self.target = vec.vec([50., 0.])
        self.pos = None
        self.vel = None

    def decide(self, scene):
        acts = {}
        if uav := scene.find('uav'):
            _, dt = scene.clock_info
            self.pos = copy.copy(uav.position)
            self.vel = copy.copy(uav.velocity)
            fake_pos = self.vel * dt - self.target + 1 * self.pos
            acts['uav.sensor_position'] = fake_pos
        return acts


def setup_scene(scene):
    """ （随机）初始化场景. """
    scene.set_params(end=50.0)
    # scene.add(Radar(pos=[10, 10]))

    # d, theta = random.uniform(50, 100), random.uniform(0, math.pi * 2)
    # pt = (d * math.cos(theta), d * math.sin(theta))
    # speed = random.uniform(3, 5)
    pt = [50, 50]
    speed = 5
    scene.add(Uav(name='uav', tracks=[pt, [-10, -10]], speed=speed, life=50.0, two_way=False))


def print_uav(uav: Uav):
    if uav and uav.is_active:
        print(uav.position, uav.sensor_position, vec.dist(uav.velocity))


def play_once():
    """ 玩一次. """
    renderer = sim.visualize.QtRenderView()
    
    scene = Scenario()
    setup_scene(scene)
    scene.step_handlers.append(StepEvent(entity='uav', evt=print_uav))

    agent = GpsAgent()

    tt = scene.reset()
    while tt:
        acts = agent.decide(scene)
        util.set_entity_attributes(scene, acts)

        tt = scene.step()
        renderer.render(scene)

if __name__ == '__main__':
    play_once()
    print('--- over ---')
