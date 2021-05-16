from __future__ import annotations
import copy
from enum import Enum

from .. import basic
from .. import move
from . import rules
from .. import vec


class Uav(basic.Entity):
    """ 无人机.

    Attributes:
        position: 当前位置.
        velocity: 当前速度.
        sensor_position: 传感器位置.
        life: 总寿命（电池）
        current_life: 当前寿命.
        rcs: 辐射反射面积.
    """

    def __init__(self, **kwargs):
        """ 初始化. """
        super().__init__(**kwargs)

        self.controller = UavController(uav=self, **kwargs)

        self.access_results = {}
        self.access_rules.append(rules.uav_access_jammer)

        self.position = None
        self.velocity = None

        self.life = kwargs['life'] if 'life' in kwargs else 60.0
        self.current_life = self.life

        self.rcs = kwargs['rcs'] if 'rcs' in kwargs else 0.01
        self.reset()

    def step(self, tt):
        _, dt = tt

        # 处理电池电量.
        self.current_life -= dt
        if self.current_life <= 0:
            self.deactive()

        # 飞控/飞行.
        prev_pos = copy.copy(self.position)
        if self.is_active():
            self.controller.step(tt)
        self.velocity = (self.position - prev_pos) / dt \
            if dt > 0.0 else vec.zeros_like(self.position)

    def reset(self):
        self.controller.reset()
        self.current_life = self.life
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

    def info(self) -> str:
        if self.is_active():
            return 'uav [{}] : {} --- {}'.format(self.id, self.position, self.velocity)
        return ''


class UavState(Enum):
    """ 无人机状态. """
    Normal = 0  # 正常飞行.
    Home = 1  # 返回起飞点.
    Back = 2  # 返航.
    Over = -1  # 生命结束.


class UavController:
    """ 无人机飞控. """

    def __init__(self, uav: Uav, **kwargs):
        """ 初始化.

        :param tracks: 轨迹.
        :param speed: 速度值.
        """
        self.uav: Uav = uav

        self._tracks = list(
            [vec.vec(pt) for pt in kwargs['tracks']]) if 'tracks' in kwargs else []
        self.track_no = 0
        self.speed = kwargs['speed'] if 'speed' in kwargs else 1.0
        self.two_way = kwargs['two_way'] if 'two_way' in kwargs else True

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
        self.track_no = 0

    def step(self, tt):
        if self._state in self._state_handlers:
            self._state_handlers[self._state](self, tt)

    def take(self, acts):
        if 'jam' in acts:
            if self._state == UavState.Normal:
                self._state = UavState.Back
        else:
            if self._state == UavState.Back and self.track_no < len(self._tracks):
                self._state = UavState.Normal

    def _step_on_normal(self, tt):
        _, dt = tt
        if self.track_no >= len(self._tracks):
            # 跑完所有航点.
            self._state = UavState.Back if self.two_way else UavState.Over
        else:
            # 跑完所有航点.
            step, left = move.step_v(
                self.uav.position, self._tracks[self.track_no], dt * self.speed)
            self.uav.position += step
            if left <= 0.0:
                self.track_no += 1

    def _step_on_over(self, tt):
        self.uav.deactive()

    def _step_on_back(self, tt):
        _, dt = tt
        step, left = move.step_v(
            self.uav.position, self._tracks[0], dt * self.speed)
        self.uav.position += step
        if left <= 0.0:
            self._state = UavState.Home

    def _step_on_home(self, tt):
        self.uav.deactive()
