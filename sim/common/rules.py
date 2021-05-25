"""
常用交互规则.
"""

from __future__ import annotations
from sim.common import receiver

from . import jammer
from . import uav
from . import radar
from sim import Entity
from sim.common import Laser


def uav_access_jammer(uav_o, jammer_o):
    """ 无人机与干扰机交互. """
    if isinstance(uav_o, uav.Uav) and isinstance(jammer_o, jammer.Jammer):
        if jammer_o.power_on and jammer_o.in_range(uav_o.position):
            if jammer_o.type == jammer.JammerType.DataLink:
                uav_o.access_results['jam_dl'] = True
            if jammer_o.type == jammer.JammerType.GPS:
                uav_o.access_results['jam_gps'] = True


def radar_access_rcs(radar_o, obj):
    """ 雷达探测其他RCS属性物体. """
    if isinstance(radar_o, radar.Radar) and isinstance(obj, Entity):
        if radar_o.need_detect(obj):
            ret = radar_o.detect(obj)
            radar_o.access_results[obj.id] = ret


def receiver_access_signal(recv_o, obj):
    """ 电子侦察设备探测物体. """
    if isinstance(recv_o, receiver.Receiver) and isinstance(obj, Entity):
        if ret := recv_o.detect(obj):
            recv_o.results[obj.id] = ret

def entity_access_laser(obj, laser: Laser):
    """ 实体与激光交互. """
    if isinstance(obj, Entity) and isinstance(laser, Laser):
        if hasattr(obj, 'damage') and hasattr(obj, 'position') and laser.power_on:
            if laser.in_dir(obj):
                _, dt = laser.clock_info
                obj.damage = obj.damage - dt * laser.power
                if obj.damage <= 0.0:
                    obj.deactive()


# def access_detect_results(obj, target):
#     """ 检测结果.
#     """
#     assert hasattr(obj, '_results') and hasattr(obj, 'detect')
#     if ret := obj.detect(target):
#         obj._results[target.id] = ret