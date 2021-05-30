"""
光电探测设备.
"""

from __future__ import annotations
from collections import namedtuple
import copy
from enum import Enum
from typing import Iterable, List, Any, Optional

from .. import vec
from . import util
from . import detector


class EoDetector(detector.Detector):
    """ 光电探测设备. 
    
    可以探测作用范围内以下实体：
    * 具有属性：position

    设备属性:
    * position: 设备位置.  
    * dir: 视场指向.
    * state: 设备状态（待机、引导、跟踪）
    * result: 探测结果. List[(time, value)]. 其中，value 是方位/俯仰值.

    设备操作:
    * guide: 引导跟踪目标.
    """

    def __init__(self, name: str = '', pos=(0, 0), fov=1.0, error=0.0, **kwargs):
        """ 初始化.

        :param pos: 位置.
        :param fov: 视场角（度）.
        :param error: 角度误差 (度).
        :see also: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)

        self.position = vec.vec3(pos)
        self.fov = util.rad(fov)
        self.error = util.rad(error)

        self._dir = vec.vec2([0, 0])  # 当前指向.
        self._state = EoState.StandBy  # 内部状态.
        self._guide_dir = None  # 引导角度.
        self._track_id: int = -1  # 跟踪目标 id.

        self._output = None

    @property
    def result(self) -> Optional[Any]:
        """ 返回探测结果. 
        
        :return: 返回当前探测结果 (time, ae)，如果没有，返回None.
        """
        return self._output

    @property
    def dir(self):
        """ 当前视场指向. """
        return self._dir

    @property
    def state(self) -> EoState:
        """ 当前光电状态. """
        return self._state
    
    def guide(self, dir: Iterable, update=False):
        """ 引导. 

        :param dir: 引导角度信息.
        :param update: 是否立刻更新. 默认不立刻更新，应该在 step一步更新.
        """
        self._guide_dir = vec.vec2(dir)
        self._state = EoState.StandBy
        if update:
            self.__take_guide()

    def reset(self) -> None:
        super().reset()
        self._dir = vec.vec2([0, 0])  # 当前指向.
        self._state = EoState.StandBy  # 内部状态.
        self._output = None

    def step(self, clock):
        self.__take_guide()

    def detect(self, other) -> Optional[Any]:
        """ 检测目标. """
        if hasattr(other, 'position'):
            aer = util.polar(self.position, other.position)
            if self.aer_range.contains(aer) and self.in_fov(other):
                return vec.vec2(aer)
        return None

    def _update_results(self):
        """ 处理结果. """
        # 处理临时结果.
        if self._state == EoState.Guide:
            # 处理引导状态.
            obj_id = self.__pick_in_fov()
            if obj_id is not None:
                self._state = EoState.Track
                self._track_id = obj_id
                self._dir = copy.copy(self._results[self._track_id])
            else:
                self._state = EoState.StandBy
                self._track_id = -1
        elif self._state == EoState.Track:
            # 处理跟踪状态.
            if self._track_id in self._results:
                self._dir = copy.copy(self._results[self._track_id])
            else:
                self._state = EoState.StandBy
                self._track_id = -1

        # 生成输出结果.
        self._output = None
        if self._state == EoState.Track and self._track_id > 0:
            value = self._results[self._track_id]
            value = tuple(value.tolist())
            self._output = EoResult(self.clock_info[0], value, self._track_id)
        self._results.clear()

    def __take_guide(self):
        """ 检查和接收引导信息. """
        if self._guide_dir is not None:
            self._state = EoState.Guide
            self._dir = copy.copy(self._guide_dir)
            self._guide_dir = None

    def __pick_in_fov(self):
        """ 找到视场中的东西. """
        if self._results:
            for k, v in self._results.items():
                return k
        return None

    def in_fov(self, obj):
        """ 判断目标在视场内. """
        aer = util.polar(self.position, obj.position)
        ae = vec.vec2(aer)
        for i in range(len(ae)):
            d = util.angle(ae[i], self._dir[i], unit='r')
            if d > self.fov:
                return False
        return True


class EoState(Enum):
    """ 光电状态. """
    StandBy = 0  # 待机.
    Guide = 1  # 导引.
    Track = 2  # 跟踪.


EoResult = namedtuple('EoResult', ['time', 'value', 'obj_id'])  # 光电探测结果.