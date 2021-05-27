"""
常用交互规则.
"""

from __future__ import annotations, absolute_import
import math

from sim import Entity, vec
from sim.common import Laser, Receiver, Jammer, JammerType, Radar, Uav


def uav_access_jammer(uav: Uav, jammer: Jammer):
    """ 无人机与干扰机交互. """
    if isinstance(uav, Uav) and isinstance(jammer, Jammer):
        if jammer.power_on and jammer.in_range(uav.position):
            if jammer.type == JammerType.DataLink:
                d_j = vec.dist(uav.position, jammer.position)
                d_s = vec.dist(uav.position, uav.home_position)
                if d_j <= 0.0 or \
                    (d_s > 0.0 and (jammer.power - 20 * math.log(d_j) > uav.power_tm - 20 * math.log(d_s))):
                    uav._access_results['jam_dl'] = True
            if jammer.type == JammerType.GPS:
                uav._access_results['jam_gps'] = True


def radar_access_rcs(radar: Radar, obj):
    """ 雷达探测其他RCS属性物体. """
    if isinstance(radar, radar.Radar) and isinstance(obj, Entity):
        if radar.need_detect(obj):
            ret = radar.detect(obj)
            radar.access_results[obj.id] = ret


def receiver_access_signal(recv: Receiver, obj):
    """ 电子侦察设备探测物体. """
    if isinstance(recv, Receiver) and isinstance(obj, Entity):
        if ret := recv.detect(obj):
            recv.result[obj.id] = ret


def entity_access_laser(obj, laser: Laser):
    """ 实体与激光交互. """
    if isinstance(obj, Entity) and isinstance(laser, Laser):
        if hasattr(obj, 'damage') and hasattr(obj, 'position') and laser.power_on:
            if laser.in_dir(obj):
                _, dt = laser.clock_info
                obj.damage = obj.damage - dt * laser.power
                if obj.damage <= 0.0:
                    obj.deactive()


