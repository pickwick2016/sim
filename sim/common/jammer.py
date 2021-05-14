""" 
干扰器.

干扰器通常有以下操作：
+ 开关干扰
TODO: 瞄准指定方向
TODO: 设置干扰频段
TODO: 设置干扰功率
TODO: 设置干扰样式
"""

from .. import basic
from .. import vec
from . import util


class Jammer(basic.Entity):
    """ 干扰器. 
    
    Attributes:
        position: 位置.
        power_on: 是否开干扰.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.power_on = False
        self.position = vec.vec([0, 0])
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        """ 设置参数.

        :param pos: 位置.
        """
        if 'pos' in kwargs:
            self.position = vec.vec(kwargs['pos'])

    def in_range(self, pos) -> bool:
        """ 判断目标在范围内. """
        aer = util.polar(self.position, pos)
        return self.aer_range.contains(aer)

    def info(self) -> str:
        if self.power_on:
            return 'jammer [{}] : on'.format(self.id)
        return ''
