
import os
import sys
sys.path.append(os.getcwd())

from typing import Tuple

import time
from sim import Scenario, Entity
from sim.event import StepEvent


G = 9.8

class Bottle(Entity):
    def __init__(self, name: str='', **kwargs):
        super().__init__(name=name, **kwargs)
        self.x = 0.0
        self.v = 0.0
        self.m = 239.46

    def step(self, clock) -> None:
        _, dt = clock
        f_m = G - 1035.71 * 0.2058 * G / self.m - 0.6 * self.v / self.m
        self.x += self.v * dt
        self.v += f_m * dt
        

scene = Scenario(end=20, step=0.01)
bottle = scene.add(Bottle())
scene.add_step_listener(StepEvent(entity=bottle, evt=lambda obj: print(obj.clock_info[0], obj.v)))
scene.run()