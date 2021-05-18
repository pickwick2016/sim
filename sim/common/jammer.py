""" 
干扰器.
"""
from enum import Enum

from .. import basic
from .. import vec
from . import util


class JammerType(Enum):
    """ 干扰器类型. """
    DataLink = 0  # 链路.
    GPS = 1  # GPS


class Jammer(basic.Entity):
    """ 干扰器. 
    
    Attributes:
        position: 位置.
        power_on: 是否开干扰.
    """

    def __init__(self, name='', pos=[0, 0], type=JammerType.DataLink, **kwargs):
        """ 初始化.

        :param name: 实体名称.
        :param pos: 干扰器位置.
        :param type: 干扰器类型.
        :param max_r: 最大干扰距离.
        :see: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.type = type
        self.power_on = False
        self.position = vec.vec(pos)

    def reset(self):
        self.power_on = False

    def in_range(self, pos) -> bool:
        """ 判断目标在范围内. """
        aer = util.polar(self.position, pos)
        return self.aer_range.contains(aer)

    def __str__(self) -> str:
        if self.power_on:
            return 'jammer [{}] : on'.format(self.id)
        return ''
