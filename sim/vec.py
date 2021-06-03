"""
向量工具模块.
"""

from typing import Iterable
import math

import numpy as np


def vec(v: Iterable) -> np.array:
    """ 向量化. """
    return np.array(v, dtype=np.float64)


def vec3(v: Iterable) -> np.array:
    """ 3维向量. """
    if len(v) == 3:
        return np.array(v, dtype=np.float64)
    else:
        ret = np.zeros(shape=(3,), dtype=np.float64)
        for i in range(min(3, len(v))):
            ret[i] = v[i]
        return ret


def vec2(v: Iterable) -> np.array:
    """ 2维向量. """
    if len(v) == 2:
        return np.array(v, dtype=np.float64)
    else:
        ret = np.zeros(shape=(2,), dtype=np.float64)
        for i in range(min(2, len(v))):
            ret[i] = v[i]
        return ret


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
    return v / dist(v) if d > 0.0 else zeros_like(v)


def angle(v1, v2) -> float:
    """ 计算向量夹角(弧度值). """
    not_zero = norm(v1) > 0. and norm(v2) > 0.
    return math.acos(np.dot(unit(v1), unit(v2))) if not_zero else 0.


def proj(v1, v2) -> np.array:
    """ 计算v1投影到v2上的向量. """
    v2u = unit(v2)
    return v2u * np.dot(v1, v2u)
