"""
常用交互规则.
"""

from __future__ import annotations

from . import jammer
from . import uav


def uav_access_jammer(u, j):
    """ 无人机与干扰机交互. """
    if isinstance(u, uav.Uav) and isinstance(j, jammer.Jammer):
        if j.power_on and j.in_range(u.position):
            u.access_results['jam'] = True