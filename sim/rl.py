""" 
强化学习(RL, Reinforce Learning)环境工具.
"""

from __future__ import annotations
from typing import Tuple, Any, Dict, Callable, Optional

from .basic import Scenario
from .util import set_entity_attributes
from .visualize import RenderView, QtRenderView


class Environment:
    """ 强化学习环境.

    包装 Scenario 形成强化学习环境，接口与 Gym 保持一致.

    Attributes:
        total_reward: 一个 episode 的总奖励.
        need_info: 是否需要获取场景信息.
    """

    renderer: Optional[RenderView] = None

    def __init__(self, referee=None, agent=None, dt=0.01, **kwargs):
        """ 初始化.

        :param referee: 裁判. 用于评价场景，获取奖励.   
        :param agent: 与环境绑定的 agent. 用于场景状态编码和场景动作解码.   
        :param dt: display interval. 0表示尽快显示. 
        """
        self.scene = Scenario(**kwargs)
        self.referee: Callable[[Scenario], Tuple[float, bool]
                               ] = referee if referee is not None else RlReferee()
        self.agent = agent
        self.need_info = True
        self.total_reward = 0.0

    def reset(self) -> Any:
        """ 重置场景.

        :return: 返回当前状态.
        """
        self.scene.reset()
        self.total_reward = 0.0
        s = self.agent.encode_state(self.scene) if self.agent else self.scene
        return s

    def step(self, acts) -> Tuple[Any, float, bool, str]:
        """ 执行一步操作.

        :param acts: 用户操作集. 可以被 agent 解码为实体属性集.
        :return: [s_, r, done, info]
        """
        # 翻译和执行场景动作.
        actions = self.agent.decode_action(acts) if self.agent else acts
        set_entity_attributes(self.scene, actions)

        tt = self.scene.step()

        # 处理结果.
        s_ = self.agent.encode_state(self.scene) if self.agent else self.scene
        reward, done = self.referee(self.scene)
        self.total_reward += reward

        done = done or (tt is None)
        info = self._info() if self.need_info else ''
        return s_, reward, done, info

    def render(self):
        """ 显示. """
        if Environment.renderer is None:
            Environment.renderer = QtRenderView()
        if Environment.renderer:
            Environment.renderer.render(self.scene)

    def _info(self) -> str:
        infos = list()
        infos.append('{0:.2f} :'.format(self.scene.clock_info[0]))
        for e in self.scene.entities:
            if s := str(e):
                infos.append(s)
        return '\n  '.join(infos)


class RlReferee:
    """ 强化学习裁判. """

    def __call__(self, scene) -> Tuple[float, bool]:
        """ 根据场景计算奖励.

        :param scene: 场景.
        :return: (reward, done).
        """
        reward, done = 0.0, False
        return reward, done


class RlAgent:
    """ 强化学习决策代理. """

    def encode_state(self, scene) -> Any:
        """ 把场景翻译为输入."""
        return scene

    def decode_action(self, act_val) -> Dict:
        """ 把输出翻译为场景指令集. """
        return act_val

    def decide(self, s) -> Any:
        """ 根据状态做出决策. """
        return {}
