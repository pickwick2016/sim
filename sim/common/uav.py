from __future__ import annotations
import copy
from enum import Enum
from typing import List

from .. import basic
from .. import move
from . import rules
from .. import vec


class Uav(basic.Entity):
    """ 无人机.

    Attributes:
        position: 当前位置.
        velocity: 当前速度.
        life: 总寿命（电池）
        rcs: 辐射反射面积.
        start_point: 起飞点坐标.
    """

    def __init__(self, name:str='', tracks=[], speed:float=1.0, \
            two_way:bool=True, life:float=60.0, rcs:float=0.1, **kwargs):
        """ 初始化. 
        
        :param name: 实体名称.
        :param tracks: 轨迹.
        :param speed: 速度值.
        :param two_way: 双向飞行（需要返航）.
        :param life: 飞机电池寿命（飞行时长）.
        :param rcs: 飞机 RCS.
        """
        super().__init__(name=name, **kwargs)
        self.access_rules.append(rules.uav_access_jammer)
        self.access_results = {}

        self.controller = UavController(
            uav=self, tracks=tracks, speed=speed, two_way=two_way, **kwargs)

        self.position = None
        self.velocity = None

        self.signal = 1

        self.life = life
        self.__current_life = self.life

        self.damage = 10.0

        self.rcs = rcs
        self.reset()

    @property
    def start_point(self):
        """ 起飞点坐标. """
        return self.controller.start_point

    def step(self, tt):
        _, dt = tt

        # 处理电池电量.
        self.__current_life -= dt
        if self.__current_life <= 0:
            self.deactive()
        if self.damage <= 0.:
            self.deactive()

        # 飞控/飞行.
        prev_pos = copy.copy(self.position)
        if self.is_active:
            self.controller.step(tt)
        self.velocity = (self.position - prev_pos) / dt \
            if dt > 0.0 else vec.zeros_like(self.position)

    def reset(self):
        self.controller.reset()
        self.__current_life = self.life
        if self.controller.is_available:
            self.position = self.controller.start_point
            self.velocity = vec.zeros_like(self.position)
        else:
            self.deactive()
            self.position, self.velocity = None, None

    def access(self, others):
        self.access_results.clear()
        super().access(others)
        self.controller.take(self.access_results)

    def __str__(self) -> str:
        if self.is_active:
            return 'uav [{}] : {} --- {}'.format(self.id, self.position, self.velocity)
        return ''


class UavState(Enum):
    """ 无人机状态. """
    Normal = 0  # 正常飞行.
    Home = 1  # 返回起飞点.
    Back = 2  # 返航.
    GPS_LOST = 3  # GPS 丢失.
    Over = -1  # 生命结束.


class UavController:
    """ 无人机飞控. """

    def __init__(self, uav: Uav, tracks: List = [], speed=1.0, two_way=True, **kwargs):
        """ 初始化.

        :param tracks: 轨迹.
        :param speed: 速度值.
        :param two_way: 双向飞行（需要返航）
        """
        self._uav: Uav = uav

        self._tracks = list([vec.vec(pt) for pt in tracks])
        self._track_no = 0
        self.speed = speed
        self.two_way = two_way

        self._state = UavState.Normal
        self._state_handlers = {
            UavState.Normal: UavController._step_on_normal,
            UavState.Over: UavController._step_on_over,
            UavState.Back: UavController._step_on_back,
            UavState.Home: UavController._step_on_home,
        }

    @property
    def start_point(self):
        """ 获取出发点. """
        return copy.copy(self._tracks[0]) if self.is_available else None

    @property
    def is_available(self) -> bool:
        return len(self._tracks) >= 2

    def reset(self):
        self._state = UavState.Normal
        self._track_no = 0

    def step(self, tt):
        if self._state in self._state_handlers:
            self._state_handlers[self._state](self, tt)

    def take(self, acts):
        if 'jam_gps' in acts:
            if self._state != UavState.GPS_LOST:
                self._state = UavState.GPS_LOST
        elif 'jam_dl' in acts:
            if self._state != UavState.Back:
                self._state = UavState.Back
        else:
            # self._state = UavState.Normal
            if self._state == UavState.Back and not self._is_track_over():
                self._state = UavState.Normal
            if self._state == UavState.GPS_LOST:
                self._state = UavState.Normal

    def _is_track_over(self) -> bool:
        return self._track_no >= len(self._tracks)

    def _step_on_normal(self, tt):
        _, dt = tt
        if self._track_no >= len(self._tracks):
            # 跑完所有航点.
            self._state = UavState.Back if self.two_way else UavState.Over
        else:
            # 跑完所有航点.
            step, left = move.step_v(
                self._uav.position, self._tracks[self._track_no], dt * self.speed)
            self._uav.position += step
            if left <= 0.0:
                self._track_no += 1

    def _step_on_over(self, tt):
        self._uav.deactive()

    def _step_on_back(self, tt):
        _, dt = tt
        step, left = move.step_v(
            self._uav.position, self._tracks[0], dt * self.speed)
        self._uav.position += step
        if left <= 0.0:
            self._state = UavState.Home

    def _step_on_home(self, tt):
        self._uav.deactive()
