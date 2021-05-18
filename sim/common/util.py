import math
from .. import vec


def ar(center, pos):
    """ 计算AR """
    assert len(center) == 2 and len(pos) == 2
    v = pos - center
    r = vec.norm(v)
    a = math.atan2(v[0], v[1]) % (math.pi * 2)
    return a, r


def aer(center, pos):
    """ 计算AER """
    assert len(center) == 3 and len(pos) == 3
    v = pos - center
    r = vec.norm(v)
    a = math.atan2(v[0], v[1]) % (math.pi * 2)
    r2 = vec.norm(vec.vec([v[0], v[1]]))
    e = math.atan2(v[2], r2)
    return vec.vec([a, e, r])


def polar(center, pos):
    """ 计算极坐标. 
    
    对于2维向量，计算AR；   
    对于3维向量，计算AER。
    """
    if len(center) == 3:
        return aer(center, pos)
    elif len(center) == 2:
        return ar(center, pos)
    return None


def check_range(rng, val) -> bool:
    """ 检查数值是否在范围内.

    None 表示不检查.
    """
    if val is None:
        return True
    if rng[0] is not None and val < rng[0]:
        return False
    if rng[1] is not None and val > rng[1]:
        return False
    return True


def rad(d):
    """ 角度转换为弧度. """
    return (d % 360.0) / 360.0 * math.pi * 2


def in_range_d(rng, a) -> bool:
    """ 判断角度在规定起止范围内. """
    rng2 = [v % (math.pi * 2) for v in rng]
    a = a % (math.pi * 2)
    if rng2[0] <= rng2[1]:
        return rng2[0] <= a < rng2[1]
    else:
        return not (rng2[0] > a >= rng2[1])


class AerRange:
    """ AER 范围. """

    def __init__(self, **kwargs) -> None:
        """ 初始化.
        
        :param max_a: 最大方位角. 默认值None.
        :param min_a: 最小方位角. 默认值None.
        :param max_e: 最大仰角. 默认值None.
        :param min_e: 最小仰角. 默认值None.
        :param max_r: 最大距离. 默认值None.
        :param min_r: 最小距离. 默认值0.
        """
        self.range_a = [None, None]
        self.range_e = [None, None]
        self.range_r = [None, None]
        self.set_param(**kwargs)

    def set_param(self, **kwargs):
        self.range_a[0] = kwargs['min_a'] if 'min_a' in kwargs else None
        self.range_a[1] = kwargs['max_a'] if 'max_a' in kwargs else None
        self.range_e[0] = kwargs['min_e'] if 'min_e' in kwargs else None
        self.range_e[1] = kwargs['max_e'] if 'max_e' in kwargs else None
        self.range_r[0] = kwargs['min_r'] if 'min_r' in kwargs else 0
        self.range_r[1] = kwargs['max_r'] if 'max_r' in kwargs else None

    def contains(self, aer) -> bool:
        """ 判断指定极坐标位置目标是否在范围内. """
        if aer is None:
            return False
        if len(aer) == 3:
            a, e, r = aer[0], aer[1], aer[2]
        else:
            a, e, r = aer[0], None, aer[1]
        return check_range(self.range_a, a) and check_range(self.range_e, e) \
            and check_range(self.range_r, r)
