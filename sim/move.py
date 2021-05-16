"""
运动模块.
"""

from typing import Tuple, Any
import copy
from . import vec


def move_to(start, end, d) -> Tuple[Any, float]:
    """ 向目的地移动一定距离.

    :param p0: 出发位置.
    :param p1: 目标位置.
    :param d: 移动距离.
    :return: [当前位置, 剩余距离]
    """
    d_all = vec.dist(start, end)
    d_left = d_all - d
    pos = start + d * vec.unit(end - start) if d_left > 0 else copy.copy(end)
    return pos, d_left


def step_v(start, end, d) -> Tuple[Any, float]:
    """ 获取步进向量 

    :param start: 出发点.
    :param end: 目标点.
    :param d: 前进步长.
    :return: (步进向量，剩余距离)
    """
    d_all = vec.dist(start, end)
    v = vec.unit(end - start) * min(d_all, d)
    return v, d_all - d
