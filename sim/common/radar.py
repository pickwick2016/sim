"""
雷达.
"""

from __future__ import annotations
from typing import Dict, Optional, Any, List
import copy
import math
import random

from .. import basic
from .. import vec
from . import util
from . import detector


class Radar(detector.Detector):
    """ 雷达.

    可以探测作用范围内以下实体：
    * 具有属性：rcs
    * 具有属性：position

    雷达属性:
    * position: 雷达位置.  
    * results: 探测结果. List[(batch_id, time, result, state)]
    """

    def __init__(self, name: str = '', pos=[0, 0], min_v: float = 0.0,
                 search_rate: float = 6.0, search_num: int = 3,
                 track_rate: float = 1.0, cancel_num: int = 3,
                 error_d: float = 0, error_r: float = 0,
                 checker=None, detector=None, **kwargs):
        """ 初始化.

        :param name: 实体名称
        :param pos: 雷达位置
        :param search_rate: 搜索数据率
        :param track_rate: 跟踪数据率
        :param search_num: 搜索次数（起批）
        :param cancel_num: 消批次数
        :param error_d: 角度误差.
        :param error_r: 距离误差.
        :param min_v: 最小径向速度.
        :see: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.position = vec.vec(pos)

        self._search_rate = search_rate
        self._search_num = search_num
        self._track_rate = track_rate
        self._cancel_num = cancel_num

        self._error_d = error_d
        self._error_r = error_r

        self._min_v = abs(float(min_v))

        self._outputs = []
        self._current_az = 0.0
        self._batch_id = 0

    def reset(self):
        super().reset()
        self._outputs.clear()
        self._batch_id = 0
        self._current_az = 0.0

    def step(self, clock):
        _, dt = clock
        self._current_az += dt * 2 * math.pi / self._search_rate

    @property
    def results(self) -> Optional[List]:
        """ 当前结果列表.  

        返回当前结果列表，列表元素为 (batch_id, time, result, state)
        """
        return self._outputs if self._outputs else None

    def detect2(self, other) -> Optional[Any]:
        """ 探测目标. """
        if self._check_detect(other):
            ret = self._do_detect(other)
            if other.id not in self._results:
                if ret is not None:
                    self._batch_id += 1
                    self._results[other.id] = RadarResult(self._batch_id)
            if other.id in self._results:
                now = self.clock_info[0] if self.clock_info else None
                self._results[other.id].update(self, now, ret)
                return self._results[other.id]
        return None

    def _update_results(self):
        """ 更新/处理侦察结果. """
        # 删除消批结果.
        for k, v in self._results.copy().items():
            if v.state == 0:
                self._results.pop(k)

        # 产生输出结果.
        now = self.clock_info[0]
        self._outputs = list([(v.batch_id, v.time, v.result, v.state)
                              for _, v in self._results.items() if (v.time == now)])

    def need_detect(self, other) -> bool:
        """ 判断是否应该探测. 

        注意：判断是否应该探测，而不是探不探测得到.
        """
        if not hasattr(other, 'rcs') or not hasattr(other, 'position'):
            return False

        if self._min_v > 0.0 and not hasattr(other, 'velocity'):
            return False

        now, dt = self.clock_info if self.clock_info else (0.0, 0.1)
        az_rng = [self._current_az, self._current_az +
                  dt * 2 * math.pi / self._search_rate]
        aer = util.polar(self.position, other.position)

        if other.id in self._results:
            ret = self._results[other.id]
            if ret.state == 1:
                # 跟踪状态下：目标进入搜索范围，间隔大于dt
                searched = util.in_angle_range(az_rng, aer[0], unit='r')
                return ((now - ret.time) > dt) and searched
            elif ret.state == 2:
                # 搜索状态下：间隔大于 track_rate.
                return (now - ret.time) >= self._track_rate
            else:
                return False
        else:
            return util.in_angle_range(az_rng, aer[0], unit='r')

    def detect(self, other) -> Optional[Any]:
        """ 探测目标. """
        if not hasattr(other, 'rcs') or not hasattr(other, 'position'):
            return None

        aer = util.polar(self.position, other.position)
        if self.aer_range.contains(aer):
            if self._min_v > 0.0:
                # 判断最低速度（如有必要）
                if hasattr(other, 'velocity'):
                    proj_v = vec.norm(vec.proj(other.velocity, self.position - other.position))
                    if proj_v > self._min_v:
                        return aer
                else:
                    return None
            else:
                return aer
        return None

    def __make_errors(self, p):
        """ 增加误差. """
        errors = vec.zeros_like(p)
        if len(errors) == 3:
            errors[0] = 0 if (self._error_d <= 0.) else random.gauss(
                0, util.rad(self._error_d))
            errors[1] = 0 if (self._error_d <= 0.) else random.gauss(
                0, util.rad(self._error_d))
            errors[2] = 0 if (self._error_r <= 0.) else random.gauss(
                0, self._error_r)
        elif len(errors) == 2:
            errors[0] = 0 if (self._error_d <= 0.) else random.gauss(
                0, util.rad(self._error_d))
            errors[1] = 0 if (self._error_r <= 0.) else random.gauss(
                0, self._error_r)
        return errors


class RadarResult:
    """ 检测结果. """

    def __init__(self, batch_id, time=None, ret=None):
        """ 初始化.

        :param batch_id: 当前批号.
        :param time: 探测时间.
        :param ret: 探测结果.
        """
        self.batch_id = batch_id
        self.time = time
        self.result = ret
        self.state = 1  # 0:消批；1:搜索；2：跟踪
        self.__search_count = 0
        self.__missing_count = 0

    def update(self, radar: Radar, time, ret):
        """ 更新结果. """
        init = self.time is None
        
        self.time = time
        self.result = ret

        if not init:
            if self.state == 1:
                # 处理搜索状态.
                if ret is None:
                    self.state = 0
                else:
                    self.__search_count += 1
                    if self.__search_count >= radar._search_num:
                        self.state = 2
            elif self.state == 2:
                # 处理跟踪状态.
                if ret is None:
                    self.__missing_count += 1
                    if self.__missing_count >= radar._cancel_num:
                        self.state = 0
                else:
                    self.__missing_count = 0

    def __str__(self) -> str:
        return '{} {}'.format(self.time, self.result)
