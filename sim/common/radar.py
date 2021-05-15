"""
雷达.
"""

from __future__ import annotations

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.access_rules.append(rules.radar_access_rcs)

        self.aer_range = util.AerRange(**kwargs)
        self.access_results = {}

        self.position = vec.vec([0, 0])

        self.__batch_id = 0

        self.search_rate = 3.0
        self.search_count = 3

        self.track_rate = 1.0
        self.track_off = 6.0

        self.__results = {}  # id : (batch_id, time, state, aer, ...)
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        """ 设置参数.

        :param pos: 雷达站位置.
        :param search_dt: 搜索时间间隔.
        :param track_dt: 跟踪时间间隔.
        """
        if 'pos' in kwargs:
            self.position = vec.vec(kwargs['pos'])
        if 'search_dt' in kwargs:
            self.search_rate = float(kwargs['search_dt'])
        if 'track_dt' in kwargs:
            self.track_rate = float(kwargs['track_dt'])

    def reset(self):
        self.__results.clear()
        self.__batch_id = 0

    @property
    def results(self):
        return self.__results

    @property
    def current_results(self):
        """ 当前结果列表.  

        元素为 (batch_id, time, result)
        """
        now = self.clock_info[0]
        ret = [(v.batch_id, v.time, v.result) for _, v in self.__results.items() if (v.time == now)]
        return list(ret)

    def access(self, others):
        self.access_results = {}
        super().access(others)
        self.__accept_access_results()

    def __accept_access_results(self):
        """ 整理交互结果. """
        # 更新探测结果.
        for obj_id, obj_det in self.access_results.items():
            if obj_id not in self.__results:
                self.__batch_id += 1
                self.__results[obj_id] = _DetectResult(self.__batch_id, None, None)
            self.__results[obj_id].accept(self, self.clock_info[0], obj_det)

        # 删除消批结果.
        now = self.clock_info[0]
        remove_ids = [k for k, v in self.__results.items() if (now - v.time > self.track_off)]
        for rid in remove_ids:
            self.__results.pop(rid)

    def detect(self, other):
        """ 探测目标. """
        if hasattr(other, 'rcs') and hasattr(other, 'position'):
            p = util.polar(self.position, other.position)
            if self.aer_range.contains(p):
                return p
        return None


class _DetectResult:
    """ 检测结果. """

    def __init__(self, batch_id, time, ret):
        self.batch_id = batch_id
        self.time = time
        self.result = ret
        self._state = 0
        self._counter = 1

    def accept(self, radar, time, ret):
        if self._state == 0:
            # 处理搜索状态.
            if (self.time is None) or (time - self.time >= radar.search_rate):
                self.time = time
                self.result = ret
                if self._counter < radar.search_count:
                    self._counter += 1
                else:
                    self._state = 1
        elif self._state == 1:
            # 处理跟踪状态.
            if (time - self.time) >= radar.track_rate:
                self.time = time
                self.result = ret
