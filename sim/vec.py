"""
向量工具模块.
"""

from typing import Iterable
import numpy as np
import math


def vec(v: Iterable) -> np.array:
    """ 向量化. """
    return np.array(v, dtype=np.float64)


def zeros_like(v: Iterable) -> np.array:
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

    :return: 向量夹角(弧度值).
    """
    if norm(v1) > 0. and norm(v2) > 0.:
        return math.acos(np.dot(unit(v1), unit(v2)))
    else:
        return 0.


def proj(v1, v2):
    """ 计算v1投影到v2上的向量. """
    v2u = unit(v2)
    return v2u * np.dot(v1, v2u)
