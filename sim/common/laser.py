"""
激光拦截时间.
"""


from __future__ import annotations
from collections import namedtuple
import copy
from enum import Enum
from typing import List, Any, Optional

import sim
from .. import vec
from . import util


class Laser(sim.Entity):
    """ 激光拦截设备. 
    
    可以探测作用范围内以下实体：
    * 具有属性：position

    可以打击作用范围内以下实体：
    * 具有属性：damage

    设备属性:
    * position: 设备位置.  
    * dir: 视场指向.
    * power_on: 是否出光.
    * state: 设备状态（待机、引导、锁定）
    * result: 当前跟踪结果. (time, value). 其中，value 是方位/俯仰值.

    设备操作：
    * guide: 引导跟踪目标
    * switch: 开关激光器.
    """

    def __init__(self, name: str = '', pos=(0, 0), fov=1.0, work=20.0, recover=600, power=1.0, **kwargs):
        """ 初始化.

        :param pos: 位置.  
        :param fov: 视场角（度）.  
        :param work: 最大连续工作时间.  
        :param recover: 最长恢复时间.   
        :param power: 功率.
        :see also: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)

        self.position = vec.vec3(pos)
        self.fov = util.rad(fov)
        self.max_work_time: float = float(work)
        self.work_time: float = self.max_work_time
        self.recover_time: float = float(recover)
        self.power_on = False
        self.power: float = 1.0

        self._dir = vec.vec2([0, 0])  # 当前指向.
        self._state = LaserState.StandBy  # 内部状态.
        self._guide_dir = None  # 引导角度.
        self._track_id: int = -1  # 跟踪目标 id.
        self._results = {}
        self._output = None

    @property
    def dir(self):
        """ 激光指向. """
        return self._dir

    @property
    def result(self) -> Optional[Any]:
        """ 激光当前跟踪结果. """
        return self._output if self._track_id > 0 else None

    @property
    def state(self) -> LaserState:
        """ 返回当前激光状态. """
        return self._state

    def switch(self, on: Optional[bool]):
        """ 开关激光器. 
        
        :param on: 设置激光器开关. None 表示转换开关状态.
        """
        if on is None:
            self.power_on = not self.power_on
        else:
            self.power_on = on

    def reset(self) -> None:
        super().reset()
        self._dir = vec.vec2([0, 0])  # 当前指向.
        self._state = LaserState.StandBy  # 内部状态.
        self._output = None
        self._results = {}
        self.work_time = self.max_work_time

    def step(self, clock):
        _, dt = clock
        self.__take_guide()
        # 处理出光/恢复时间.
        if self.power_on:
            self.work_time = max(self.work_time - dt, 0.0)
            if self.work_time <= 0.0:
                self.power_on = False
        else:
            self.work_time += self.max_work_time / self.recover_time * dt
            self.work_time = min(self.work_time, self.max_work_time)

    def access(self, others: List[sim.Entity]) -> None:
        for other in others:
            ret = self.detect(other)
            if ret is not None:
                self._results[other.id] = ret
        self._update_results()

    def guide(self, dir, update=False):
        """ 引导. 

        :param dir: 引导角度信息.
        :param update: 是否立刻更新. 默认不立刻更新，应该在 step一步更新.
        """
        self._guide_dir = vec.vec2(dir)
        self._state = LaserState.StandBy
        if update:
            self.__take_guide()

    def __take_guide(self):
        """ 检查和接收引导信息. """
        if self._guide_dir is not None:
            self._state = LaserState.Guide
            self._dir = copy.copy(self._guide_dir)
            self._guide_dir = None

    def _need_detect(self, other) -> bool:
        if self._state == LaserState.Lock:
            return other.id == self._track_id
        return True

    def _update_results(self):
        self._output = None
        now, _ = self.clock_info
        if self._state == LaserState.Guide:
            if self._results:
                self._track_id = list(self._results.keys())[0]
                self._state = LaserState.Lock
                self._dir = self._results[self._track_id]
                self._output = LaserResult(
                    now, self._results[self._track_id], self._track_id)
            else:
                self._state = LaserState.StandBy
                self._track_id = -1
        elif self._state == LaserState.Lock:
            if self._track_id in self._results:
                self._dir = self._results[self._track_id]
                self._output = LaserResult(
                    now, self._results[self._track_id], self._track_id)
            else:
                self._state = LaserState.StandBy
                self._track_id = -1
        self._results.clear()

    def detect(self, other):
        if not hasattr(other, 'position'):
            return None
        aer = util.polar(self.position, other.position)
        if self.aer_range.contains(aer):
            ae = vec.vec2(aer)
            conds = [util.angle(ae[i], self.dir[i], 'r') <
                     self.fov for i in range(len(ae))]
            if all(conds):
                return ae
        return None

    def in_dir(self, other) -> bool:
        assert hasattr(other, 'position')
        aer = util.polar(self.position, other.position)
        if self.aer_range.contains(aer):
            ae = vec.vec2(aer)
            conds = [util.angle(ae[i], self.dir[i], 'r') <
                     0.001 for i in range(len(ae))]
            return all(conds)
        return False


class LaserState(Enum):
    """ 光电状态. """
    StandBy = 0  # 待机.
    Guide = 1  # 导引.
    Lock = 2  # 跟踪.


LaserResult = namedtuple('LaserResult', ['time', 'value', 'obj_id'])
""" 激光探测结果. 
time: 时戳.
value: 探测结果 A,E
obj_id: 关联目标的 id.
"""
