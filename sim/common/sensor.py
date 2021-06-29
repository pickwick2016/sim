from __future__ import annotations
from enum import Enum

from sim import vec
from sim.common import util


class SensorType(Enum):
    """ 传感器类型. """
    Unknown = 0  # 未知类型.
    Conic = 1  # 圆锥型
    Rect = 2  # 矩形.


class Sensor:
    """ 传感器. """

    def __init__(self, parent=None, dir=(0, 0), type: SensorType = SensorType.Unknown, params=None):
        """ 初始化.

        :param parent: 传感器附着物体. 该对象需要有 position 属性.
        :param direction: 传感器指向.
        :param type: 传感器类型.
        :param params: 传感器参数. 根据类型进行解释.
        """
        self.parent = parent
        self.direction = vec.vec2(dir)
        self.type = type
        self.params = params

    @property
    def position(self):
        """ 传感器位置. """
        return self.parent.position if self.parent else None

    def contain(self, pos) -> bool:
        """ 判断目标位置是否在范围内. """
        aer = util.xyz2aer(self.position, pos)
        return self.contain_a(vec.vec2(aer))

    def contain_a(self, ae) -> bool:
        """ 判断方位/俯仰角是否在范围内. """
        if self.type == SensorType.Conic:
            xyz1 = util.aer2xyz((0, 0, 0), vec.vec3(ae, padding=1.0))
            xyz2 = util.aer2xyz((0, 0, 0), vec.vec3(self.direction, padding=1.0))
            d = abs(util.a_norm(vec.angle(xyz1, xyz2), unit='r', type='-'))
            return d <= self.params
        if self.type == SensorType.Rect:
            #TODO: 此方法有问题，应该利用坐标旋转进行计算.
            da = abs(util.a_norm(ae[0] - self.direction[0], unit='r', type='-'))
            de = abs(util.a_norm(ae[1] - self.direction[1], unit='r', type='-'))
            return da <= self.params[0] and de <= self.params[1]
        return False
