"""
向量工具模块.
"""

import numpy as np


def dist(v1, v2=None):
    """ 两个点的距离. """
    v = v1 if v2 is None else (v1 - v2)
    return np.linalg.norm(v)


def unit(v):
    """ 计算单位向量. """
    d = dist(v)
    if d > 0.:
        return v / dist(v)
    else:
        return zeros_like(v)


def vec(v):
    """ 向量化. """
    return np.array(v, dtype=np.float64)


def zeros_like(v):
    """ 生成 0 向量."""
    return np.zeros_like(v)


def move_to(p0, p1, d):
    """ 向目的地移动一定距离.

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

    :param p0: 出发位置.
    :param p1: 目标位置.
    :param d: 移动距离.
    :return: [移动向量, 剩余距离]
    """
    d0 = dist(p0, p1)
    step = unit(p1 - p0) * min(d0, d)
    left = d0 - d
    return step, left
