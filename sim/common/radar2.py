from __future__ import annotations
from collections import namedtuple
from enum import Enum
import math
import random
from sim.common.radar import RadarResult
from sim.common.detector import Detector
from typing import Dict, Optional, Tuple, Any, List

from sim import Entity
from .. import vec
from . import util


class Detector2(Entity):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self._detect_results = {}

    def access(self, others: List[Entity]) -> None:
        super().access(others)
        self._detect_others(others)

    def _detect_others(self, others: List[Entity]) -> None:
        """ 检测其他实体. """
        for other in others:
            if self._detect_check(other):
                ret = self._detect(other)
                self._take_result(other, ret)
        self._update_results()

    def _detect_check(other) -> bool:
        """ 判断是否需要检测目标. """
        return True

    def _detect(self, other) -> Any:
        """ 检测目标. """
        return None

    def _take_result(self, other, ret):
        """ 接收结果. """
        pass

    def _update_results(self):
        """ 更新结果. """
        pass


class Radar2(Detector2):
    """ 雷达2. """

    def __init__(self, name: str = '', pos=(0, 0), search_rate=6.0, min_v=0.0, **kwargs):
        """[summary]

        Args:
            name (str, optional): [description]. Defaults to ''.
            pos (tuple, optional): [description]. Defaults to (0, 0).
            search_rate (float, optional): [description]. Defaults to 6.0.
            min_v (float, optional): [description]. Defaults to 0.0.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.search_rate = float(search_rate)
        self.searcher = AzSearcher(parent=self, rate=self.search_rate)
        self.position = vec.vec3(pos)
        self._batch_id: int = 0
        self.min_v = abs(float(min_v))

    def step(self, clock: Tuple[float, float]) -> None:
        super().step(clock)
        self.searcher.step(clock)

    def _detect_check(self, other) -> bool:
        """ 判断是否需要检测目标. """
        if not hasattr(other, 'position') or not hasattr(other, 'rcs'):
            return False
        if self.min_v > 0 and not hasattr(other, 'velocity'):
            return False

        if other.id not in self._detect_results:
            return self.searcher.contains(other)
        else:
            state = self._detect_results[other.id].state
            t = self._detect_results[other.id].time
            if state == RadarResultState.Track:
                return self.clock_info[0] - t > 1
            elif state == RadarResultState.Search:
                return self.clock_info[0] - t > 1
        return False

    def _detect(self, other) -> Any:
        """ 检测目标. """
        aer = util.xyz2aer(self.position, other.position)
        if self.aer_range.contains(aer):
            return aer
        return None

    def _take_result(self, other, ret):
        """ 接收结果. """
        if ret is not None:
            if other.id not in self._detect_results:
                self._batch_id += 1
                self._detect_results[other.id] = RadarResult(
                    self.clock_info[0], self._batch_id, ret, RadarResultState.Search, 1)
            else:
                prev_ret = self._detect_results[other.id]
                state = prev_ret.state if prev_ret.num <= 3 else RadarResultState.Track
                self._detect_results[other.id] = RadarResult(
                    self.clock_info[0], prev_ret.batch_id, ret, state, prev_ret.num + 1)

    def _update_results(self):
        """ 更新结果. """
        for k, v in self._detect_results.copy().items():
            threshold = 6.0
            if self.clock_info[0] - v.time > threshold:
                self._detect_results.pop(k)


RadarResult = namedtuple(
    'RadarResult', ['time', 'batch_id', 'value', 'state', 'num'])


class RadarResultState(Enum):
    """ 雷达探测结果状态. """
    Search = 0
    Track = 1


class AzSearcher:
    def __init__(self, parent, rate=6.0, **kwargs):
        self.parent = parent
        self.az_range = [0.0, 0.0]
        self.rate = rate

    def reset(self):
        self.az_range = [0.0, 0.0]

    def step(self, clock: Tuple[float, float]) -> None:
        dr = 2 * math.pi / self.rate * clock[1]
        self.az_range[0] = self.az_range[1]
        self.az_range[1] = self.az_range[0] + dr

    def contains(self, obj) -> bool:
        if not self.parent:
            return False
        if not hasattr(self.parent, 'position') or not hasattr(obj, 'position'):
            return False
        aer = util.xyz2aer(self.parent.position, obj.position)
        return util.in_angle_range(self.az_range, aer[0], 'r')
