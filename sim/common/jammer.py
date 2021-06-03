""" 
干扰器.
"""

from enum import Enum
from typing import Optional

from .. import basic
from .. import vec
from . import util


class JammerType(Enum):
    """ 干扰器类型. """
    DataLink = 0  # 链路.
    GPS = 1  # GPS


class Jammer(basic.Entity):
    """ 干扰器. 
    
    可以干扰作用范围内以下实体：
    * 具有属性：signal

    设备属性:
    * position: 设备位置.  
    * power_on: 是否开干扰.

    设备操作：
    * switch: 开关干扰机.
    """

    def __init__(self, name='', pos=[0, 0], type=JammerType.DataLink, power=0.0, **kwargs):
        """ 初始化.

        :param name: 实体名称.
        :param pos: 干扰器位置.
        :param type: 干扰器类型.
        :param max_r: 最大干扰距离.
        :param power: 发射功率.(dBW)
        :see: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.type = type
        self.power_on = False
        self.position = vec.vec3(pos)
        self.power: float = float(power)  # 干扰信号功率

    def switch(self, on: Optional[bool]):
        """ 开关干扰机. 
        
        :param on: 设置干扰开关. None 表示转换开关状态.
        """
        if on is None:
            self.power_on = not self.power_on
        else:
            self.power_on = on

    def reset(self):
        self.power_on = False

    def in_range(self, pos) -> bool:
        """ 判断目标在范围内. """
        aer = util.xyz2aer(self.position, pos)
        return self.aer_range.contains(aer)

    def __str__(self) -> str:
        if self.power_on:
            return 'jammer [{}] : on'.format(self.id)
        return ''
