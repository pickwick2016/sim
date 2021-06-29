"""
光电探测设备.
"""

from __future__ import annotations
from collections import namedtuple
import copy
from enum import Enum
from typing import Iterable, List, Any, Optional

from sim import Entity
from .. import vec
from . import util
from .sensor import Sensor, SensorType


class Eo(Entity):
    """ 光电探测设备. """

    def __init__(self, name: str = '', pos=(0, 0), **kwargs):
        super().__init__(name)
        self.position = vec.vec3(pos)
        self.aer_range = util.AerRange(**kwargs)
        self._guide_dir = None
        self._state = EoState.StandBy
        self._capacity = EoCapacity()
        self._sensor = Sensor(self, SensorType.Conic, util.rad(3))
        self._target = None

    def reset(self):
        self._target = None
        self._guide_dir = None
        self._state = EoState.StandBy

    def step(self, clock):
        self._take_guide()

    def access(self, others: List[Entity]) -> None:
        if self._state == EoState.Guide:
            self._access_on_guide(others)
        elif self._state == EoState.Track:
            self._access_on_track(others)

    @property
    def result(self):
        """ 跟踪/结果. """
        return self._target

    @property
    def state(self):
        return self._state

    def guide(self, ae, update=False):
        """ 接收引导. 

        :param ae: 引导方位/俯仰. 
        """
        self._guide_dir = vec.vec2(ae)
        if update:
            self._take_guide()

    def _take_guide(self):
        """ 接收引导信息. """
        if self._guide_dir is not None:
            if self._state in (EoState.StandBy, EoState.Guide):
                self._sensor.direction = copy.copy(self._guide_dir)
                self._guide_dir = None
                self._state = EoState.Guide

    def _access_on_guide(self, others):
        assert self._state == EoState.Guide

        found, min_val = False, 100000.0
        for other in others:
            if (ret := self._detect(other)) is not None:
                ae_val = vec.norm(vec.vec2(ret))  # TODO: FIX: 应该判断与轴向之间的距离.
                if ae_val < min_val:
                    found, min_val = True, ae_val
                    self._target = EoTarget(self.clock_info[0], ret, other.id)
        self._state = EoState.Track if found else EoState.StandBy

    def _access_on_track(self, others):
        assert self._state == EoState.Track
        assert self._target is not None

        find = False
        if target := util.find(others, lambda obj: obj.id == self._target.id):
            if (aer := self._detect(target)) is not None:
                self._sensor.direction = vec.vec2(aer)
                self._target = target
                find = True
        if not find:
            self._state = EoState.StandBy
            self._target = None

    def _detect(self, obj) -> Optional[Any]:
        """ 检测目标是否在视场内. 
        :return: 在视场，返回AER；不在视场，返回None.
        """
        #TODO: 根据检测能力计算效果.
        if hasattr(obj, 'position'):
            aer = util.xyz2aer(self.position, obj.position)
            if self.aer_range.contain(aer) and self._sensor.contain_a(vec.vec2(aer)):
                return aer
        return None


EoCapacity = namedtuple('EoCapacity', field_names=['min', 'max', 'normal'])
""" 光电探测能力描述. 
"""


EoTarget = namedtuple('EoTarget', ['time', 'value', 'obj_id'])
""" 光电探测结果. 

:prop time: 时戳.
:prop value: 探测结果 AER
:prop obj_id: 关联目标的 id.
"""


class EoState(Enum):
    """ 光电状态. """
    StandBy = 0  # 待机.
    Guide = 1  # 导引.
    Track = 2  # 跟踪.
