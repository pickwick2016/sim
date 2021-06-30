from __future__ import annotations
from collections import namedtuple
import copy
from enum import Enum
from typing import Optional, Tuple, Any


from sim import Entity, vec
from . import util
from .sensor import Sensor, SensorType


class Laser(Entity):
    """ 激光. """

    def __init__(self, name: str = '', pos=(0, 0), fov=util.rad(1.0), min_cap=(200, 5), max_cap=(1000, 10), battery: Tuple[float, float] = (120, 300), **kwargs):
        """ 初始化. 

        :param pos: 激光位置.
        :param fov: （粗跟踪）视场大小.
        :param min_cap: 近端拦截能力（距离，时间）
        :param max_cap: 远端拦截能力（距离，时间）
        :param battery: 电池信息. (放电时间，充电时间)
        :param capacity: 毁伤能力.
        """
        super().__init__(name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.position = vec.vec3(pos)
        self._atp = Sensor(self, type=SensorType.Conic, params=fov)
        self._power_on: bool = False
        self._capacity = LaserCapacity(min=min_cap, max=max_cap)
        self._battery_info = BatteryInfo(*battery)
        self._battery: float = 1.0
        self._state = LaserState.StandBy
        self._target: Optional[LaserTarget] = None
        self._guide_dir = None
        self.reset()

    def reset(self):
        """ 重置. """
        self._battery = 1.0
        self._power_on: bool = False
        self._target = None
        self._state = LaserState.StandBy

    def step(self, clock: Tuple[float, float]) -> None:
        """ 步进. """
        _, dt = clock
        self._take_guide()
        self._update_battery(dt)

    def access(self, others) -> None:
        """ 交互. """
        if self._state == LaserState.Guide:
            self._access_on_guide(others)
        elif self._state == LaserState.Lock:
            self._access_on_lock(others)

    @property
    def battery(self) -> float:
        """ 当前电池电量（百分比）"""
        return self._battery

    @property
    def state(self) -> LaserState:
        """ 当前状态. """
        return self._state

    @property
    def direction(self):
        """ 激光指向. """
        return self._atp.direction

    @property
    def power_on(self) -> bool:
        """ 出光状态. """
        return self._power_on

    @property
    def capacity(self):
        """ 毁伤能力. """
        return self._capacity

    @property
    def result(self) -> Optional[LaserTarget]:
        """ 当前跟踪目标情况. 
        
        如果没有被跟踪（锁定）的目标，返回None.
        """
        return self._target

    def damage(self, obj) -> float:
        """ 返回对目标单位时间内的损伤率（单位时间内的损伤值）.

        :return: <= 0.0 表示不会造成损伤.
        """
        # TODO: 完善毁伤效果.
        if self.is_target(obj):
            r = self._target.value[-1]
            if r > self._capacity.max[0]:
                return 0.0
            elif r < self._capacity.min[0]:
                return 1.0 / self._capacity.min[1]
            else:
                a = (r - self._capacity.min[0]) / \
                    (self._capacity.max[0] - self._capacity.min[0])
                t = a * \
                    (self._capacity.max[1] - self._capacity.min[1]
                     ) + self._capacity.min[1]
                return 1.0 / t
        return 0.0

    def switch(self, power_on: Optional[bool] = None) -> bool:
        """ 开关. 
        :param power_on: None表示切换开关状态. True表示开，False表示关.
        """
        if power_on is None:
            self._power_on = not self._power_on
        else:
            self._power_on = power_on
        return self._power_on

    def guide(self, ae, update=False):
        """ 接收引导. 
        :param ae: 引导方位/俯仰. 单位：度.
        """
        self._guide_dir = vec.vec2(ae)
        if update:
            self._take_guide()

    def is_target(self, obj) -> bool:
        """ 判断是否瞄准指定物体. """
        return self._target is not None and self._target.obj_id == obj.id

    def _take_guide(self):
        """ 接收引导信息. """
        if self._guide_dir is not None:
            if self._state in (LaserState.StandBy, LaserState.Guide):
                self._atp.direction = copy.copy(self._guide_dir)
                self._guide_dir = None
                self._state = LaserState.Guide

    def _update_battery(self, dt):
        """ 更新电池状态. """
        if self._power_on:
            self._battery -= dt / self._battery_info.full
        else:
            self._battery += dt / self._battery_info.recover
        self._battery = util.clip((0.0, 1.0), self._battery)
        if self._battery <= 0.0:
            self._power_on = False

    def _access_on_lock(self, others):
        """ Lock 状态下交互处理. """
        assert self._state == LaserState.Lock
        assert self._target is not None

        lock_flag = False
        if target := util.find(others, lambda obj: obj.id == self._target.obj_id):
            if (ret := self._detect(target)) is not None:
                self._atp.direction = vec.vec2(ret)
                self._target = LaserTarget(self.clock_info[0], ret, target.id)
                lock_flag = True

        if lock_flag:
            self._state = LaserState.Lock
        else:
            self._state = LaserState.StandBy
            self._target = None

    def _access_on_guide(self, others):
        """ Guide 状态下交互处理. """
        assert self._state == LaserState.Guide

        found, min_val = False, 100000.0
        for other in others:
            if (ret := self._detect(other)) is not None:
                ae_val = vec.norm(vec.vec2(ret))
                if ae_val < min_val:
                    found, min_val = True, ae_val
                    self._target = LaserTarget(
                        self.clock_info[0], ret, other.id)
        self._state = LaserState.Lock if found else LaserState.Guide

    def _detect(self, obj) -> Optional[Any]:
        """ 检测目标是否在视场内. 
        :return: 在视场，返回AER；不在视场，返回None.
        """
        if hasattr(obj, 'position'):
            aer = util.xyz2aer(self.position, obj.position)
            if self.aer_range.contain(aer) and self._atp.contain(obj.position):
                return aer
        return None


BatteryInfo = namedtuple(
    'BatteryInfo', ['full', 'recover'], defaults=[120, 300])
""" 电池信息. 

:prop full: 满电情况下放电时间（s）
:prop recover: 空电情况下充电时间（s）
"""


LaserTarget = namedtuple('LaserTarget', ['time', 'value', 'obj_id'])
""" 激光探测结果. 

:prop time: 时戳.
:prop value: 探测结果 A,E
:prop obj_id: 关联目标的 id.
"""

LaserCapacity = namedtuple('LaserCapacity', ['min', 'max'])
""" 激光拦截能力

:prop min: 近端距离能力. (距离 m，时间 s)
:prop max: 远端距离能力. (距离 m，时间 s)
"""


class LaserState(Enum):
    """ 光电状态. """
    StandBy = 0  # 待机.
    Guide = 1  # 导引.
    Lock = 2  # 跟踪.
