"""
场景基本类定义.

1. 实体 (Entity)
2. 场景 (Scenario)
"""

from __future__ import annotations

import copy
from typing import Optional, Tuple, List, Callable, Any


class Entity:
    """ 仿真实体.

    Attributes:
        name: 实体名称.
        id: 实体 ID.
        step_handlers: 步进处理列表. List[ step_handle(entity) ]
        msg_handlers: 消息处理列表. List[ msg_handle(sender, msg) -> bool]
    """

    def __init__(self, **kwargs):
        self.step_handlers: List[Callable[[Entity, Any], bool]] = []
        self.msg_handlers: List[Callable[[Entity], None]] = []
        self._id: int = EntityId.gen()
        self._name: str = '' if 'name' not in kwargs else kwargs['name']
        self._scene: Optional[Scenario] = None
        self._active: bool = True

    @property
    def id(self) -> int:
        """ 实体 id. """
        return self._id

    @property
    def name(self) -> str:
        """ 实体名称. """
        return self._name

    @property
    def scene(self) -> Optional[Scenario]:
        """ 实体相关联的场景. """
        return self._scene

    @property
    def clock_info(self) -> Tuple[float, float]:
        return self._scene.clock_info if self._scene else None

    def attach(self, scene=None):
        """ 关联场景. """
        self._scene = scene

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

    def reset(self):
        """ 重置状态. """
        pass

    def step(self, tt):
        """ 步进. """
        pass

    def on_step(self):
        """ 步进消息处理. """
        for handle in self.step_handlers:
            handle(self)

    def access(self, others):
        """ 与其他实体交互，改变自己状态. """
        pass

    def send_msg(self, reciever: Optional[Entity, id, str], msg) -> bool:
        """ 发送消息. 

        :param reciever: 收消息的实体. 可以通过 Entity、id 或者 name 指定.
        :return: 是否发送成功.
        """
        if self._scene:
            if recv_obj := self.scene.find(reciever):
                self.scene.post_msg(self, recv_obj, msg)
                return True
        return False

    def on_msg(self, sender: Entity, msg):
        """ 接收和处理消息. """
        for handler in self.msg_handlers:
            if not handler(sender, msg):
                break


class Scenario:
    """ 场景.

    Attributes:
        step_handlers: 步进处理器列表.: List[ step_handle(Scenario) ]
    """

    def __init__(self, **kwargs):
        self._entities = []
        self.clock = SimClock(**kwargs)
        self.step_handlers = []
        self._msg_queue = []  # 消息队列.

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

    def find(self, ref: Optional[Entity, int, str]) -> Optional[Entity]:
        """ 查找实体.

        :param ref: 查找条件. 可以是 obj, id, name  
        :return: 符合条件的实体，找不到返回None  
        """
        obj_v = ref if isinstance(ref, Entity) else None
        id_v = ref if isinstance(ref, int) else None
        name_v = ref if isinstance(ref, str) else None
        for e in self._entities:
            if (obj_v and e is obj_v) or (id_v and e.id == id_v) or (name_v and e.name == name_v):
                return e
        return None

    def add(self, obj: Entity) -> Optional[Entity]:
        """ 增加实体. """
        if not isinstance(obj, Entity):
            return None
        ids = [e.id for e in self._entities]
        if obj.id not in ids:
            obj.attach(self)
            self._entities.append(obj)
        return obj

    def remove(self, obj):
        """ 移除对象. """
        if obj and isinstance(obj, Entity):
            obj.attach(None)
            self._entities.remove(obj)

    def clear(self):
        """ 移除所有对象. """
        for obj in self._entities:
            obj.attach(None)
        self._entities.clear()

    def step(self):
        """ 步进.

        :return: 当前时间信息 (now, dt)， None表示执行完毕.
        :see: SimClock.step()
        """
        if self.clock.is_over():
            return None

        tt = self.clock.info()
        active_entities = self.active_entities

        for e in active_entities:
            e.step(tt)

        shadow_entities = copy.deepcopy(active_entities)
        for e in active_entities:
            others = [se for se in shadow_entities if se.id != e.id]
            e.access(others)

        self._dispatch_msgs()

        for handler in self.step_handlers:
            handler(self)
        for e in active_entities:
            e.on_step()

        ret = self.clock.step()
        return ret

    def run(self):
        """ 连续运行. """
        while self.step():
            pass

    def reset(self):
        """ 重置场景. """
        self.clock.reset()
        for e in self._entities:
            e.reset()
        return self.clock_info

    @property
    def clock_info(self) -> Tuple[float, float]:
        return self.clock.info()

    def post_msg(self, sender, reciever, msg):
        """ 消息入列. """
        self._msg_queue.append((sender, reciever, msg))

    def _dispatch_msgs(self):
        """ 分发消息. """
        msg_queue = copy.copy(self._msg_queue)
        self._msg_queue.clear()
        for sender, reciever, msg in msg_queue:
            if reciever and reciever.is_active():
                reciever.on_msg(sender, msg)

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
        return self.info() if not self.is_over() else None

    def info(self) -> Tuple[float, float]:
        """ 当前时钟信息 
        
        :return: (now, dt)
                now: 当前时间.
                dt: 上一步到当前时间经过的时长. 起始时是0，后续是dt。
        """
        return self.now, (0.0 if self.now == self.start else self.dt)

    def is_over(self) -> bool:
        """ 是否结束. """
        return self.now > self.end


class EntityId:
    """ 实体 ID 生成. """
    __id = 0

    @staticmethod
    def gen():
        EntityId.__id += 1
        return EntityId.__id
