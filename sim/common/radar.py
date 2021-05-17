"""
雷达.
"""

from __future__ import annotations
from typing import Dict
import math

from .. import basic
from .. import vec
from . import util
from . import rules


class Radar(basic.Entity):
    """ 雷达.

    Attributes:
        position: 位置.
        results: 探测结果.
        track_dt: 跟踪时间间隔(数据率).
        search_dt: 搜索时间间隔(数据率).
        track_off: 消批时间.
    """

    def __init__(self, name: str = '', pos=[0, 0], search_rate: float = 6.0, \
            track_rate: float = 1.0, search_num: int = 3, cancel_num: int = 3, **kwargs):
        """ 初始化.

        :param name: 实体名称
        :param pos: 雷达位置
        :param search_rate: 搜索数据率
        :param track_rate: 跟踪数据率
        :param search_num: 搜索次数（起批）
        :param cancel_num: 消批次数
        :see: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.access_rules.append(rules.radar_access_rcs)

        self.aer_range = util.AerRange(**kwargs)
        self.access_results = {}

        self.position = vec.vec(pos)

        self.search_rate = search_rate
        self.search_num = search_num

        self.track_rate = track_rate
        self.cancel_num = cancel_num

        self.__current_az = 0.0
        self.__batch_id = 0
        self.__results: Dict[int, _DetectResult] = {}

    def reset(self):
        self.__results.clear()
        self.__batch_id = 0
        self.__current_az = 0.0

    def step(self, tt):
        _, dt = tt
        self.__current_az += dt * 2 * math.pi / self.search_rate

    @property
    def results(self):
        return self.__results

    @property
    def current_results(self):
        """ 当前结果列表.  

        元素为 (batch_id, time, result)
        """
        now = self.clock_info[0]
        ret = [(v.batch_id, v.time, v.result)
               for _, v in self.__results.items() if (v.time == now)]
        return list(ret)

    def access(self, others):
        self.access_results.clear()
        super().access(others)
        self.__accept_access_results()

    def __accept_access_results(self):
        """ 整理交互结果. """
        # 更新探测结果.
        for obj_id, obj_det in self.access_results.items():
            if obj_id not in self.__results:
                self.__batch_id += 1
                self.__results[obj_id] = _DetectResult(
                    self.__batch_id, self.clock_info[0], obj_det)
            else:
                self.__results[obj_id].update(
                    self, self.clock_info[0], obj_det)

        # 删除消批结果.
        remove_ids = [k for k, v in self.__results.items() if v.state == 0]
        for rid in remove_ids:
            self.__results.pop(rid)

    def need_detect(self, other) -> bool:
        """ 判断目标应否被探测. """
        if not hasattr(other, 'rcs') or not hasattr(other, 'position'):
            return False

        now, dt = self.clock_info
        az_rng = [self.__current_az - dt * 2 *
                  math.pi / self.search_rate, self.__current_az]
        ax = util.polar(self.position, other.position)
        if other.id in self.__results:
            if self.__results[other.id].state == 2:
                # 跟踪状态.
                if now - self.__results[other.id].time >= self.track_rate:
                    return True
            if self.__results[other.id].state == 1:
                # 搜索状态.
                if now - self.__results[other.id].time >= dt * 1.01:
                    return util.in_range_d(az_rng, ax[0])
        else:
            return util.in_range_d(az_rng, ax[0])
        return False

    def detect(self, other):
        """ 探测目标. """
        assert hasattr(other, 'rcs') and hasattr(other, 'position')

        p = util.polar(self.position, other.position)
        if self.aer_range.contains(p):
            return p
        return None


class _DetectResult:
    """ 检测结果. """

    def __init__(self, batch_id, time, ret):
        """ 初始化.

        :param batch_id: 当前批号.
        :param time: 探测时间.
        :param ret: 探测结果.
        """
        self.batch_id = batch_id
        self.time = time
        self.result = ret
        self.state = 1
        self.__search_count = 0
        self.__missing_count = 0

    def update(self, radar: Radar, time, ret):
        """ 更新结果. """
        self.time = time
        self.result = ret

        if self.state == 1:
            # 处理搜索状态.
            if ret is None:
                self.state = 0
            else:
                self.__search_count += 1
                if self.__search_count >= radar.search_num:
                    self.state = 2
        elif self.state == 2:
            # 处理跟踪状态.
            if ret is None:
                self.__missing_count += 1
                if self.__missing_count >= radar.cancel_num:
                    self.state = 0
            else:
                self.__missing_count = 0
