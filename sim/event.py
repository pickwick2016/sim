"""
场景事件辅助处理模块.
"""

import collections
from typing import Callable, Iterable, Union, Optional, Any

from numpy import iterable

from .basic import Scenario, Entity


class StepEvent:
    """ 时间事件. 
    
    配合 Scene 的 step_handlers 使用的时间时间处理辅助类.

    Usages:
        # 在1.3秒，对场景，执行打印时钟信息
        scene.step_handlers.append(TimeEvent(times=1.3, evt=lambda s: print(s.clock_info)))
        
        # 在1、2秒，对场景，执行打印时钟信息
        scene.step_handlers.append(TimeEvent(times=[1, 2], evt=lambda s: print(s.clock_info)))

        # 在每次步进，对场景，执行打印时钟信息
        scene.step_handlers.append(TimeEvent(evt=lambda s: print(s.clock_info)))
        
        # 在每次步进，对jammer-1实体，执行打印时钟信息
        scene.step_handlers.append(TimeEvent(entity='jammer-1', evt=lambda e: print(e.clock_info)))

        # 在1.3秒，对jammer-1实体，执行打印时钟信息
        scene.step_handlers.append(TimeEvent(times=1.3, entity='jammer-1', evt=lambda e: print(e.clock_info)))
    """

    def __init__(self, evt: Callable[[Any], None], times: Union[float, Iterable[float], None] = None,
                 entity: Optional[Entity] = None):
        """ 初始化.

        :param evt: 事件处理句柄.  
            entity不是None时，调用原型为 evt(entity).    
            entity是None时，调用原型为 evt(scenario).    
        :param times: 触发事件的时间或事件序列.  
        :param entity: 具体调用的对象.
        """
        self.times = times
        self.entity = entity
        self.evt = evt

    def __call__(self, scene: Scenario):
        assert scene

        if self.evt is not None:
            obj = scene if self.entity is None else scene.find(
                obj_ref=self.entity)
            if obj and self.__check_time(obj):
                self.evt(obj)

    def __check_time(self, obj):
        """ 检查时间是否满足. """
        if self.times is None:
            return True

        now, dt = obj.clock_info
        if isinstance(self.times, (float, int)):
            if abs(now - self.times) <= 0.1 * dt:
                return True
        elif isinstance(self.times, collections.Iterable):
            for t in self.times:
                if abs(now - t) < 0.1 * dt:
                    return True
        return False
