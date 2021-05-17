"""
强化学习示例.
"""


import math
import random
from typing import Tuple


import sys
sys.path.append('../')

from sim import vec
from sim.common import Uav, Jammer, Radar
from sim.rl import Environment, RlReferee

##############################################################################
# 决策代理
##############################################################################

class CmdAgent:
    """ 简单指控代理. """

    def __init__(self):
        self.range_0 = 21.0
        self.range_1 = 30.0

    def encode_state(self, scene):
        """ 把场景翻译为输入."""
        jammer, uav = scene.find('jammer'), scene.find('target')
        s = vec.dist(uav.position, jammer.position)
        return s

    def decode_action(self, act_val):
        """ 把输出翻译为动作. """
        actions = {}
        if act_val == 1:
            actions['jammer.power_on'] = True
        if act_val == -1:
            actions['jammer.power_on'] = False
        return actions

    def decide(self, s):
        """ 根据状态（距离），产生决策.

        :return: 1表示power_on；-1表示power_off；0表示维持原状.
        """
        output = 0
        if s < self.range_0:
            output = 1
        if s > self.range_1:
            output = -1
        return output


##############################################################################


class DqnAgent:
    """ 深度Q网络代理. """

    def __init__(self):
        """ 初始化.

        :param network: 深度网络 inputs=2， output=3
            inputs = [dist, speed]
            outputs = softmax([on, off, keep])
        """
        self.network = None

    def encode_state(self, scene):
        """ 把场景翻译为输入."""
        jammer, uav = scene.find('jammer'), scene.find('target')
        d = vec.dist(uav.position, jammer.position)
        s = vec.dist(uav.velocity)
        return vec.vec([d, s])

    def decode_action(self, acts):
        """ 把输出翻译为动作. """
        mi = 0  # acts 中最大值的索引.
        actions = {}
        if mi == 0:
            actions['jammer.power_on'] = True
        elif mi == 1:
            actions['jammer.power_on'] = False
        return actions

    def decide(self, s) -> dict:
        """ 决策. """
        output = 0
        # output = network.forward(x)
        return output


##############################################################################
# 裁判
##############################################################################

class SimpleReferee:
    """ 简单裁判. """

    def __call__(self, scene) -> Tuple[float, bool]:
        """ 计算奖励值（reward, done）

        :return:
            reward 奖励值.  入侵=-1000， 其他=0
            done 入侵或飞机消失，可以结束.
        """
        jammer, uav = scene.find('jammer'), scene.find('target')
        d = vec.dist(uav.position, jammer.position)

        invade = d < 20.0  # 判断是否已经入侵.
        done = not uav.is_active or invade

        reward = 0.0
        if invade:
            reward -= 1000.0
        if jammer.power_on:
            reward -= 1.0
        reward = max(-1000., reward)

        return reward, done


##############################################################################
# 环境/场景构建
##############################################################################

def setup_scene(scene):
    """ （随机）初始化场景. """
    scene.add(Jammer(name='jammer', pos=[0, 0]))
    scene.add(Radar(pos=[10, 10]))

    d, theta = random.uniform(50, 100), random.uniform(0, math.pi * 2)
    pt = (d * math.cos(theta), d * math.sin(theta))
    speed = random.uniform(3, 5)
    scene.add(Uav(name='target', tracks=[pt, [0, 0]], speed=speed, life=60.0))


def play_once(show=False):
    """ 玩一次. """
    agent = CmdAgent()
    env = Environment(referee=SimpleReferee(), agent=agent, dt=.1, end=50.0)
    setup_scene(env.scene)

    s = env.reset()
    while True:
        if show:
            env.render()
        a = agent.decide(s)
        s_, r, done, info = env.step(a)
        if done:
            break
        s = s_
    return env.total_reward


def play(rounds=15):
    total_rewards = []
    for i in range(rounds):
        r = play_once(show=True)
        print('episode [{0}] : total reward = {1}'.format(str(i + 1), r))
        total_rewards.append(r)
    print('avg reward = {}'.format(sum(total_rewards) / len(total_rewards)))


if __name__ == '__main__':
    play()
    print('--- over ---')
