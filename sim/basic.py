"""
场景基本类定义.

1. 实体 (Entity)
2. 场景 (Scenario)
"""

from __future__ import annotations

import copy
import time
from typing import Optional, Tuple, List, Callable, Union, Any


class Entity:
    """ 仿真实体.

    Attributes:
        name: 实体名称.
        id: 实体 ID.
        scene: 实体所关联的场景.
        clock_info: 实体相关的仿真时间信息.
        is_active: 实体是否处于活动状态.
        access_rules: 交互规则列表.
        step_rules: 步进规则列表.
    """

    def __init__(self, name: str = '', **kwargs):
        """ 初始化.

        :param name: 实体名称.        
        """
        self.__id: int = EntityId.gen()
        self.__name: str = name
        self.__active: bool = True
        self.__scene: Optional[Scenario] = None
        self.step_rules: List[
            Callable[[Entity, Tuple[float, float]], None]] = []
        self.access_rules: List[Callable[[Entity, Entity], None]] = []

    @property
    def id(self) -> int:
        """ 实体 id. """
        return self.__id

    @property
    def name(self) -> str:
        """ 实体名称. """
        return self.__name

    @property
    def clock_info(self) -> Tuple[float, float]:
        return self.__scene.clock_info if self.__scene else None

    @property
    def is_active(self) -> bool:
        """ 检查活动状态. """
        return self.__active

    def deactive(self) -> None:
        """ 退出活动状态.

        退出活动状态后，实体将不再参与仿真.
        """
        self.__active = False

    def attach(self, scene=None) -> None:
        """ 关联场景. """
        self.__scene = scene

    def reset(self) -> None:
        """ 重置状态. """
        self.__active = True

    def step(self, clock: Tuple[float, float]) -> None:
        """ 步进.
        
        :param clock: 当前时钟信息.
        """
        for rule in self.step_rules:
            rule(self, clock)

    def access(self, others: List[Entity]) -> None:
        """ 与其他实体交互，改变自己状态. 

        :param others: 其他实体.
        """
        for other in others:
            for rule in self.access_rules:
                rule(self, other)


class Scenario:
    """ 场景.  """

    def __init__(self, start=0.0, end=10.0, step=0.1, mode='', **kwargs):
        """ 初始化. 
        
        :param start: 场景起始时间.  默认值是0s。  
        :param end: 仿真结束时间.  默认值是10s。  
        :param step: 仿真步长.默认值是0.1s。  
        :param mode: 运行模式.
        """
        self.__entities: List[Entity] = []
        self.__clock = SimClock(start=start, end=end,
                                step=step, mode=mode, **kwargs)
        self.step_listeners: List[Callable[[Scenario], None]] = []

    def set_params(self, **kwargs):
        """ 设置场景参数.
        """
        self.__clock.set_params(**kwargs)

    def add_step_listener(self, listener: Callable) -> Any:
        """ 增加步进消息监听器.

        :param listener: 步进消息监听器.
        :return: 新增的步进消息监听器.
        """
        assert listener is not None
        self.step_listeners.append(listener)
        return listener

    @property
    def entities(self) -> List[Entity]:
        """ 场景中的实体列表. """
        return self.__entities

    @property
    def active_entities(self) -> List[Entity]:
        """ 场景中活动实体列表. """
        return list([e for e in self.__entities if e.is_active])

    @property
    def clock_info(self) -> Tuple[float, float]:
        return self.__clock.info()

    def add(self, obj: Entity) -> Optional[Entity]:
        """ 增加实体. """
        if isinstance(obj, Entity):
            ids = [e.id for e in self.__entities]
            if obj.id not in ids:
                obj.attach(self)
                self.__entities.append(obj)
            return obj
        return None

    def remove(self, obj_ref: Union[Entity, int, str]) -> bool:
        """ 移除对象. """
        if obj := self.find(obj_ref):
            obj.attach(None)
            self.__entities.remove(obj)
        return obj is not None

    def clear(self):
        """ 移除所有实体. """
        for obj in self.__entities:
            obj.attach(None)
        self.__entities.clear()

    def find(self, obj_ref: Union[Entity, int, str], active=True) -> Optional[Entity]:
        """ 查找实体.

        :param ref: 查找条件. 可以是实体、实体id、实体名字.    
        :return: 符合条件的实体，找不到返回None  
        """
        obj_v = obj_ref if isinstance(obj_ref, Entity) else None
        id_v = obj_ref if isinstance(obj_ref, int) else None
        name_v = obj_ref if isinstance(obj_ref, str) else None
        for e in self.__entities:
            if (obj_v and e is obj_v) or (id_v and e.id == id_v) or (name_v and e.name == name_v):
                return e if (not active) or e.is_active else None
        return None

    def reset(self) -> Tuple[float, float]:
        """ 重置场景. 
        
        :return: 场景起始时钟信息.
        """
        self.__clock.reset()
        for e in self.__entities:
            e.reset()
        return self.clock_info

    def step(self) -> Optional[Tuple[float, float]]:
        """ 步进.

        :return: 当前时钟信息 (now, dt)， None表示执行完毕.
        :see: SimClock.step()
        """
        tt = self.__clock.step()
        if tt is not None:
            active_entities = self.active_entities
            for e in active_entities:
                e.step(tt)

            active_entities = self.active_entities
            shadow_entities = copy.deepcopy(active_entities)
            for obj in active_entities:
                others = [
                    other for other in shadow_entities if other.id != obj.id]
                obj.access(others)

            for handler in self.step_listeners:
                handler(self)
        return tt

    def run(self, reset=True):
        """ 连续运行. 

        :param reset: 是否自动重置.
        """
        if reset:
            self.reset()
        while self.step():
            pass


class SimClock:
    """ 仿真时钟. """

    def __init__(self, start=0.0, end=10.0, step=0.1, mode='', **kwargs):
        """ 初始化.

        :param start: 起始时间.
        :param end: 结束时间.
        :param step: 时间步进.
        :param mode: 时钟模式.
        """
        self.start = start
        self.end = end
        self.dt = step
        self.mode = mode
        self.realtime = None
        self.__now = 0.0
        self.reset()

    def reset(self):
        self.__now = self.start
        if self.mode == 'realtime':
            self.realtime = time.time()

    def step(self) -> Optional[Tuple[float, float]]:
        """ 步进.

        :return: (now, dt)
        """
        if self.mode == 'realtime':
            time_used = time.time() - self.realtime
            time_left = max(self.__now - time_used, 0.001)
            if time_left > 0.001:
                time.sleep(time_left)

        self.__now += self.dt
        return self.info() if not self.is_over() else None

    def info(self) -> Tuple[float, float]:
        """ 当前时钟信息 
        
        :return: (now, dt)
                now: 当前时间.
                dt: 上一步到当前时间经过的时长. 起始时是0，后续是dt。
        """
        return self.__now, (0.0 if self.__now == self.start else self.dt)

    def is_over(self) -> bool:
        """ 是否结束. """
        if self.end is None:
            return False
        return self.__now > self.end


class EntityId:
    """ 实体 ID 生成. """
    __id = 0

    @staticmethod
    def reset():
        EntityId.__id = 0

    @staticmethod
    def gen():
        EntityId.__id += 1
        return EntityId.__id
