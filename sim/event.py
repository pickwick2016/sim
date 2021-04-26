"""
场景事件辅助处理模块.
"""

from .basic import Scenario


class TimeEvent:
    """ 时间事件. 
    
    配合 Scene 和 Entity 的 step_handlers 使用的时间时间处理辅助类.

    Usages:
        entity.step_handlers.append(TimeEvent(time=1, evt=lambda e: e.do_something()))
        ...
        scene.step_handlers.append(TimeEvent(time=5, evt=lambda e: e.do_something()))
        ...
    """

    def __init__(self, time=None, times=None, evt=None):
        """ 初始化.

        :param time: 触发事件的时间.     
        :param times: 触发事件的时间序列.  
        :param evt: 事件处理句柄.  调用原型为 evt(obj), 要求 obj 有 clock_info 属性.
        """
        self.time = time
        self.times = times
        self.evt = evt

    def __call__(self, obj):
        if self.evt is not None:
            if self.time is not None:
                self.__on_time(obj)
            elif self.times is not None:
                self.__on_times(obj)

    def __on_time(self, obj):
        """ 处理定时消息. """
        now, dt = obj.clock_info
        if abs(now - self.time) <= 0.1 * dt:
            self.evt(obj)

    def __on_times(self, obj):
        """ 处理事件序列消息. """
        now, dt = obj.clock_info
        for t in self.times:
            if abs(now - t) < 0.1 * dt:
                self.evt(obj)
                break
