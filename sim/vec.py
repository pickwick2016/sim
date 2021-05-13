"""
向量工具模块.
"""

import numpy as np
import math


def vec(v):
    """ 向量化. """
    return np.array(v, dtype=np.float64)


def zeros_like(v):
    """ 生成 0 向量."""
    return np.zeros_like(v)


def dist(v1, v2=None) -> float:
    """ 两个点的距离. """
    v = v1 if v2 is None else (v1 - v2)
    return np.linalg.norm(v)


def norm(v) -> float:
    """ 向量的模. """
    return np.linalg.norm(v)


def unit(v):
    """ 计算单位向量. """
    d = norm(v)
    if d > 0.:
        return v / dist(v)
    else:
        return zeros_like(v)


def angle(v1, v2) -> float:
    """ 计算向量夹角

    :return: 向量夹角的弧度值.
    """
    if norm(v1) > 0. and norm(v2) > 0.:
        return math.acos(np.dot(unit(v1), unit(v2)))
    else:
        return 0.


def proj(v1, v2):
    """ 计算v1投影到v2上的向量. """
    v2u = unit(v2)
    return v2u * np.dot(v1, v2u)


def move_to(p0, p1, d):
    """ 向目的地移动一定距离.

    ! 将被转移至 move 模块.

    :param p0: 出发位置.
    :param p1: 目标位置.
    :param d: 移动距离.
    :return: [当前位置, 剩余距离]
    """
    d0 = dist(p0, p1)
    left = d0 - d
    if left > 0:
        return p0 + d * unit(p1 - p0), left
    return p1, left


def move_step(p0, p1, d):
    """ 向目的地移动一步（向量）.

    ! 将被转移至 move 模块.
    
    :param p0: 出发位置.
    :param p1: 目标位置.
    :param d: 移动距离.
    :return: [移动向量, 剩余距离]
    """
    d0 = dist(p0, p1)
    step = unit(p1 - p0) * min(d0, d)
    left = d0 - d
    return step, left
