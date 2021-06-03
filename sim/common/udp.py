"""
UDP 发送设备.
"""

import binascii
import socket
import struct
from typing import Union

from sim import Scenario, Entity
from sim.common import Uav, Radar, EoDetector, Jammer, Laser, Receiver


class UdpSender:
    """ UDP 发送设备.
    """

    def __init__(self, ip='127.0.0.1', port=8000) -> None:
        """ 初始化.

        :param ip: 目标 ip
        :param port: 目标端口.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (ip, port)
        self.socket.connect(self.addr)
        self.packers = {
            Scenario: pack_scene,
            Uav: pack_uav,
            Radar: pack_radar,
            Receiver: pack_receiver,
            EoDetector: pack_eo,
            Jammer: pack_jammer,
            Laser: pack_laser
        }

    def __call__(self, scene: Scenario):
        """ 发送场景状态. """
        assert scene
        self.send_obj(scene)
        for obj in scene.entities:
            self.send_obj(obj)

    def send_obj(self, obj):
        """ 发送对象. """
        data = self._pack_data(obj)
        self._send_data(data)

    def _send_data(self, data):
        if data and len(data) > 0:
            print('send : {}'.format(binascii.b2a_hex(data)))
            self.socket.send(data)

    def _pack_data(self, obj: Union[Scenario, Entity]):
        to = type(obj)
        if to in self.packers:
            return self.packers[to](obj)
        return None


TypeIds = {
    Uav: 1,
    Radar: 2,
    EoDetector: 3,
    Receiver: 4,
    Jammer: 5,
    Laser: 6,
}


def pack_scene(scene: Scenario):
    """ 场景信息打包. """
    data = struct.pack('BBBB', 0xeb, 0x90, 0x5a, 0x4c)

    obj_ids = [obj.id for obj in scene.entities]
    data = data + struct.pack('fI', scene.clock_info[0], len(obj_ids))

    fmt = '{}I'.format(len(obj_ids))
    data = data + struct.pack(fmt, * obj_ids)
    return data


def pack_radar(radar: Radar):
    """ 雷达信息打包. """
    data = struct.pack('II', radar.id, TypeIds[Radar])
    data = data + struct.pack('3f', * radar.position)
    num = 0 if radar.result is None else len(radar.result)
    data = data + struct.pack('I', num)
    for _ in range(num):
        pass
    return data


def pack_jammer(jammer: Jammer):
    """ 干扰机信息打包. """
    data = struct.pack('II', jammer.id, TypeIds[Jammer])
    data = data + struct.pack('3f', * jammer.position)
    data = data + struct.pack('H', 1 if jammer.power_on else 0)
    return data


def pack_eo(eo: EoDetector):
    """ 光电信息打包. """
    data = struct.pack('II', eo.id, TypeIds[EoDetector])
    data = data + struct.pack('3f', * eo.position)
    num = 0 if eo.result is None else 1
    data = data + struct.pack('HH', eo.state, num)
    return data


def pack_laser(laser):
    """ 激光信息打包. """
    data = struct.pack('II', laser.id, TypeIds[Laser])
    data = data + struct.pack('3f', * laser.position)
    num = 0 if laser.result is None else 1
    data = data + struct.pack('HH', laser.state, num)
    return data


def pack_receiver(recv):
    """ 接收机信息打包. """
    data = struct.pack('II', recv.id, TypeIds[Receiver])
    data = data + struct.pack('3f', * recv.position)
    num = 0 if recv.result is None else len(recv.result)
    data = data + struct.pack('I', num)
    for _ in range(num):
        pass
    return data


def pack_uav(uav: Uav):
    """ 无人机信息打包. """
    data = struct.pack('II', uav.id, TypeIds[Uav])
    data = data + struct.pack('3f3f', * uav.position, * uav.velocity)
    return data
