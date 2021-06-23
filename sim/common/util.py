from typing import Any, Iterable
import math
import numpy as np

from .. import vec


def poly_center(polygon: Iterable) -> np.array:
    """ 求闭合区域（多边形）中心. """
    ret = vec.zeros_like(polygon[0])
    for p in polygon:
        ret = ret + p
    ret = ret / len(p)
    return ret


def dist_p2poly(p, poly) -> float:
    """ 点到区域的最近距离.
    """
    d1s = [vec.dist(p, pt) for pt in poly]

    num = len(poly)
    ss = [(poly[i], poly[(i + 1) % num]) for i in range(num)]
    d2s = [dist_p2l(p, s) for s in ss]

    d1, d2 = min(d1s), min(d2s)
    return min(d1, d2)


def dist_p2ls(p, ls) -> float:
    """ 点到线段的距离. 

    :param p: 点
    :param ls: 线段 [p0, p1]
    """
    pv = vec.vec(p)
    lv0, lv1 = vec.vec(ls[0]), vec.vec(ls[1])
    pv2 = vec.proj(pv-lv0, lv1-lv0) + lv0
    if vec.dist(pv2, lv0) + vec.dist(pv2, lv1) > vec.dist(lv0, lv1):
        ds = [vec.dist(pv, lv0), vec.dist(pv, lv1)]
        return min(ds)
    else:
        return dist_p2l(p, ls)


def dist_p2l(p, l) -> float:
    """ 点到直线的距离.

    :param p: 点
    :param l: 直线 [p0, p1]
    """
    v0, v1 = p - l[0], l[1] - l[0]
    a = vec.angle(v0, v1)
    ret = abs(math.sin(a) * vec.norm(v0))
    return ret
    

def ar(center, pos):
    """ 计算AR """
    assert len(center) == 2 and len(pos) == 2
    v = pos - center
    r = vec.norm(v)
    a = math.atan2(v[0], v[1]) % (math.pi * 2)
    return a, r


def xyz2aer(center, pos):
    """ xyz 坐标转换为 aer 坐标. """
    assert len(center) == 3 and len(pos) == 3
    v = vec.vec(pos) - vec.vec(center)
    r = vec.norm(v)
    a = math.atan2(v[0], v[1]) % (math.pi * 2)
    r2 = vec.norm(vec.vec([v[0], v[1]]))
    e = math.atan2(v[2], r2)
    return vec.vec([a, e, r])


def aer2xyz(center, aer):
    """ aer 坐标转换为 xyz 坐标. """
    assert len(center) == 3 and len(aer) == 3
    a, e, r = aer[0], aer[1], aer[2]
    z = r * math.sin(e)
    r2 = r * math.cos(e)
    x, y = r2 * math.sin(a), r2 * math.cos(a)
    return vec.vec([x, y, z]) + vec.vec(center)


def lla2xyz(center, lla):
    """ 大地坐标到 xyz 坐标 """
    raise NotImplementedError


def xyz2lla(center, xyz):
    """ xyz 坐标到大地坐标 """
    raise NotImplementedError


def polar(center, pos):
    """ 计算极坐标. 
    
    对于2维向量，计算AR；   
    对于3维向量，计算AER。
    """
    if len(center) == 3:
        return xyz2aer(center, pos)
    elif len(center) == 2:
        return ar(center, pos)
    return None


def in_range(rng: Iterable, val: Any) -> bool:
    """ 检查数值是否在范围（左闭右开）内.
    """
    assert len(rng) == 2
    if val is None:
        return True
    if rng[0] is not None and val < rng[0]:
        return False
    if rng[1] is not None and val >= rng[1]:
        return False
    return True


def norm_angle(a: float, unit='d', type='+'):
    """ 标准化角度.

    :param type: '+' - 0～360°；'-' - -180°～180° 
    """
    if unit == 'd' or unit == 'deg':
        r = a % 360
        if type != '+':
            r = r if (r <= 180) else (r - 360)
        return r
    elif unit == 'r' or unit == 'rad':
        r = a % (math.pi * 2)
        if type != '+':
            r = r if (r <= math.pi) else (r - math.pi * 2)
        return r
    else:
        raise Exception('error')


def clip(rng: Iterable, v: Any) -> Any:
    """ 将数值约束在范围内. """
    assert len(rng) == 2
    ret = v
    if rng[0] is not None and ret < rng[0]:
        ret = rng[0]
    if rng[1] is not None and ret > rng[1]:
        ret = rng[1]
    return ret


def rad(d: float) -> float:
    """ 角度转换为弧度. """
    return (d % 360.0) / 360.0 * math.pi * 2


def deg(r: float) -> float:
    """ 弧度转化为角度. """
    return (r % (math.pi * 2)) / (math.pi * 2) * 360


def angle(a1: float, a2: float, unit='d') -> float:
    """ 计算两个角度的夹角. """
    if unit == 'd' or unit == 'deg':
        da = abs(a1 % 360 - a2 % 360)
        return da if da <= 180 else (360 - da)
    elif unit == 'r' or unit == 'rad':
        pi2 = math.pi * 2
        da = abs(a1 % pi2 - a2 % pi2)
        return da if da <= math.pi else (pi2 - da)
    else:
        raise Exception('error')


def in_angle_range(rng: Iterable, v: float, unit='d') -> bool:
    """ 判断在角度起止范围（左闭右开）. 
    
    :param rng: 角度起、止范围，顺时针
    :param a: 角度.
    :param unit: 单位. 'd','deg' 角度；'r','rad' 弧度.
    """
    assert len(rng) == 2

    if unit == 'd' or unit == 'deg':
        rng2 = (rng[0] % 360, rng[1] % 360)
        v2 = v % 360
    elif unit == 'r' or unit == 'rad':
        rng2 = (rng[0] % (math.pi * 2), rng[1] % (math.pi * 2))
        v2 = v % (math.pi * 2)
    else:
        raise Exception('error')

    if rng2[1] > rng2[0]:
        return rng2[1] > v2 >= rng2[0]
    elif rng2[0] < rng2[1]:
        return not (rng[0] > v2 >= rng[1])
    elif rng2[0] == rng2[1]:
        return v2 == rng2[0]


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
        return in_range(self.range_a, a) and in_range(self.range_e, e) \
            and in_range(self.range_r, r)

