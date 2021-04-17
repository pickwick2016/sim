"""
场景相关内容.
1. 实体 (Entity)
2. 场景 (Scenario)
"""

import copy
from typing import Optional, Tuple


class EntityId:
    """ 实体 ID 生成. """
    __id = 0

    @staticmethod
    def gen():
        EntityId.__id += 1
        return EntityId.__id


class Entity:
    """ 仿真实体.

    Attributes:
        name: 实体名称.
        id: 实体 ID.
    """

    def __init__(self, **kwargs):
        self._id = EntityId.gen()
        self._active = True
        self.name = '' if 'name' not in kwargs else kwargs['name']

    @property
    def id(self) -> int:
        """ 实体 id. """
        return self._id

    def reset(self):
        """ 重置状态. """
        pass

    def access(self, others):
        """ 与其他实体交互，改变自己状态. """
        pass

    def step(self, tt):
        """ 步进. """
        pass

    def is_active(self) -> bool:
        """ 检查活动状态. """
        return self._active

    def deactive(self):
        """ 退出活动状态.
        退出活动状态后，实体将不再参与仿真.
        """
        self._active = False

    def info(self) -> str:
        """ 实体信息. """
        return ''


class SimClock:
    """ 仿真时钟. """

    def __init__(self, **kwargs):
        """ 初始化.

        :param start: 起始时间.
        :param end: 结束时间.
        :param step: 时间步进.
        """
        self.start = 0.0
        self.end = 10.0
        self.dt = 0.1
        self.set_params(**kwargs)
        self.now = self.start

    def set_params(self, **kwargs):
        self.start = kwargs['start'] if 'start' in kwargs else self.start
        self.end = kwargs['end'] if 'end' in kwargs else self.end
        self.dt = kwargs['step'] if 'step' in kwargs else self.dt

    def reset(self):
        self.now = self.start

    def step(self) -> Optional[Tuple[float, float]]:
        """ 步进.

        :return: (now, dt)
        """
        self.now += self.dt
        return self.info() if self.now < self.end else None

    def info(self) -> Tuple[float, float]:
        """ 当前时钟信息 (now, dt)"""
        return self.now, self.dt


class Scenario:
    """ 场景.

    Attributes:
        step_handlers: 步进处理器列表.
                    步进处理函数 step_handle(scene)
    """

    def __init__(self, **kwargs):
        self._entities = []
        self.clock = SimClock(**kwargs)
        self.step_handlers = []

    def set_params(self, **kwargs):
        self.clock.set_params(**kwargs)

    @property
    def entities(self) -> list:
        """ 场景中的实体列表. """
        return self._entities

    @property
    def active_entities(self) -> list:
        """ 场景中活动实体列表. """
        return list([e for e in self._entities if e.is_active()])

    def find(self, name=None, id_=None) -> Optional[Entity]:
        """ 查找实体.

        :param name: 实体名称.
        :param id_: 实体 id.
        :return: 符合条件的实体，或者 None.
        """
        for e in self._entities:
            id_match = (e.id == id_) if id_ is not None else True
            name_match = (e.name == name) if name is not None else True
            if id_match and name_match:
                return e
        return None

    def add(self, obj: Entity):
        """ 增加实体. """
        assert obj is not None
        ids = [e.id for e in self._entities]
        if obj.id not in ids:
            self._entities.append(obj)
        return obj

    def remove(self, obj):
        """ 移除对象. """
        if obj and isinstance(obj, Entity):
            self._entities.remove(obj)

    def clear(self):
        """ 移除所有对象. """
        self._entities.clear()

    def step(self):
        """ 步进.

        :return: 当前时间信息 (now, dt)， None表示执行完毕.
        :see: SimClock.step()
        """
        tt = self.clock.step()
        if tt is not None:
            active_entities = self.active_entities

            # 更新实体状态.
            for e in active_entities:
                e.step(tt)

            # 交互更新实体状态.
            shadow_entities = copy.deepcopy(active_entities)
            for e in active_entities:
                others = [se for se in shadow_entities if se.id != e.id]
                e.access(others)

            # 处理步进消息.
            for handler in self.step_handlers:
                handler(self)
        return tt

    def run(self):
        """ 连续运行. """
        while self.step():
            pass

    def reset(self):
        """ 重置场景. """
        self.clock.reset()
        for e in self._entities:
            e.reset()
        return self.clock_info()

    def clock_info(self) -> Tuple[float, float]:
        return self.clock.info()

    def accept_actions(self, actions):
        """ 接收和执行指令.

        :param actions: 指令集. { object.property = value }
        """
        for k, v in actions.items():
            str_s = k.split('.')
            if len(str_s) == 2:
                name, attr = str_s[0], str_s[1]
                if obj := self.find(name):
                    if hasattr(obj, attr):
                        setattr(obj, attr, v)

