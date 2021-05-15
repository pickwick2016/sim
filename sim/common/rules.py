"""
常用交互规则.
"""

from __future__ import annotations

from . import jammer
from . import uav
from . import radar
from sim import Entity


def uav_access_jammer(uav_o, jammer_o):
    """ 无人机与干扰机交互. """
    if isinstance(uav_o, uav.Uav) and isinstance(jammer_o, jammer.Jammer):
        if jammer_o.power_on and jammer_o.in_range(uav_o.position):
            uav_o.access_results['jam'] = True


def radar_access_rcs(radar_o, obj):
    """ 雷达探测其他RCS属性物体. """
    if isinstance(radar_o, radar.Radar) and isinstance(obj, Entity):
        ret = radar_o.detect(obj)
        if ret is not None:
            radar_o.access_results[obj.id] = ret