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
    data = struct.pack('BBBB', 0xeb, 0x90, 0x5a, 0x4c)

    obj_ids = [obj.id for obj in scene.entities]
    data = data + struct.pack('fI', scene.clock_info[0], len(obj_ids))

    fmt = '{}I'.format(len(obj_ids))
    data = data + struct.pack(fmt, * obj_ids)
    return data


def pack_radar(radar):
    data = struct.pack('II', radar.id, TypeIds[Radar])
    data = data + struct.pack('3f', * radar.position)
    return data


def pack_jammer(jammer):
    data = struct.pack('II', jammer.id, TypeIds[Jammer])
    data = data + struct.pack('3f', * jammer.position)
    return data


def pack_eo(eo):
    data = struct.pack('II', eo.id, TypeIds[EoDetector])
    data = data + struct.pack('3f', * eo.position)
    return data


def pack_laser(laser):
    data = struct.pack('II', laser.id, TypeIds[Laser])
    data = data + struct.pack('3f', * laser.position)
    return data


def pack_receiver(recv):
    data = struct.pack('II', recv.id, TypeIds[Receiver])
    data = data + struct.pack('3f', * recv.position)
    return data


def pack_uav(uav: Uav):
    data = struct.pack('II', uav.id, TypeIds[Uav])
    data = data + struct.pack('3f3f', * uav.position, * uav.velocity)
    return data
