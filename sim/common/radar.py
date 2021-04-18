"""
雷达.
"""

import math

from .. import basic
from .. import vec


class _DetectResult:
    """ 检测结果. """

    def __init__(self, t, ret=None):
        self.time = t
        self.result = ret
        self.state = 0

    def accept(self, radar, t, ret):
        if (t - self.time) >= radar.track_dt:
            self.time = t
            self.result = ret


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
        self.position = vec.vec([0, 0])
        self.track_dt = 1.0
        self.search_dt = 3.0
        self.search_count = 3
        self.track_off = 6.0
        self._results = {}
        self._now = 0
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
            self.search_dt = float(kwargs['search_dt'])
        if 'track_dt' in kwargs:
            self.track_dt = float(kwargs['track_dt'])

    def reset(self):
        self._results.clear()
        self._now = 0

    @property
    def results(self):
        return self._results

    def access(self, others):
        for other in others:
            # 更新结果.
            if ret := self.detect(other):
                if other.id not in self._results:
                    self._results[other.id] = _DetectResult(self._now, ret)
                else:
                    self._results[other.id].accept(self, self._now, ret)
            # 消批
            if other.id in self._results:
                if (self._now - self._results[other.id].time) > self.track_off:
                    self._results.pop(other.id)

    def step(self, tt):
        self._now = tt[0]

    def detect(self, other):
        """ 探测目标. """
        if hasattr(other, 'rcs') and hasattr(other, 'position'):
            v = other.position - self.position
            return vec.dist(v), math.atan2(v[1], v[0])
        return None



def in_range(val, rng) -> bool:
    """ 判断数值在范围内. """
    assert len(rng) == 2
    return (rng[0] is None or val >= rng[0]) and (rng[1] is None or val <= rng[1])


class AerRange:
    """ 范围. """

    def __init__(self, **kwargs):
        self.range_r = [None, None]
        self.range_az = [None, None]
        self.range_el = [None, None]
        self.set_params(**kwargs)

    def set_params(self, **kwargs):
        if 'min_r' in kwargs:
            self.range_r[0] = kwargs['min_r']
        if 'max_r' in kwargs:
            self.range_r[1] = kwargs['max_r']
        if 'min_a' in kwargs:
            self.range_az[0] = kwargs['min_a']
        if 'max_a' in kwargs:
            self.range_az[1] = kwargs['max_a']
        if 'min_e' in kwargs:
            self.range_el[0] = kwargs['min_e']
        if 'max_e' in kwargs:
            self.range_el[1] = kwargs['max_e']

    def contains(self, aer):
        """ 判断目标在范围内. """
        return in_range(aer[0], self.range_az) and in_range(aer[1], self.range_el) and in_range(aer[2], self.range_r)


class Beam:
    """ 波束. """

    def __init__(self, **kwargs):
        self.direction = [0, 0]
        self.range = AerRange()

    def contains(self, aer):
        aer2 = (aer[0] - self.direction[0], aer[1] - self.direction[1], aer[2])
        return self.range.contains(aer2)

