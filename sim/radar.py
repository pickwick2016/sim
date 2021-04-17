import math

from sim import Entity
from sim import vec


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
            self.range_a[0] = kwargs['min_a']
        if 'max_a' in kwargs:
            self.range_a[1] = kwargs['max_a']
        if 'min_e' in kwargs:
            self.range_e[0] = kwargs['min_e']
        if 'max_e' in kwargs:
            self.range_e[1] = kwargs['max_e']

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


class Radar(Entity):
    """ 雷达.

    Attributes:
        position: 位置.
        results: 探测结果.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.position = vec.vec([0., 0.])
        self.interval = 1.0
        self.interval2 = 3.0
        self._results = {}
        self._now = 0

    def reset(self):
        self._results.clear()
        self._now = 0

    @property
    def results(self):
        return self._results

    def access(self, others):
        for other in others:
            # 间隔时间刷新.
            if other.id in self._results:
                if self._now - self._results[other.id][0] < self.interval:
                    continue
            # 更新结果.
            if ret := self.detect(other):
                self._results[other.id] = (self._now, ret)
            # 消批
            if other.id in self._results:
                if self._now - self._results[other.id][0] > self.interval2:
                    self._results.pop(other.id)

    def step(self, tt):
        self._now = tt[0]

    def detect(self, other):
        """ 探测目标. """
        if hasattr(other, 'rcs') and hasattr(other, 'position'):
            v = other.position - self.position
            return vec.dist(v), math.atan2(v[1], v[0])
        return None
