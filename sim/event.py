"""
场景事件辅助处理模块.
"""

from .basic import Scenario


class TimeEvent:
    """ 时间事件. """

    def __init__(self, time=None, times=None, evt=None):
        """ 初始化.

        :param time: 触发事件的时间.     
        :param times: 触发事件的时间序列.  
        :param evt: 事件处理句柄. 
                    调用原型为 evt(scene)
        """
        self.time = time
        self.times = times
        self.evt = evt

    def __call__(self, scene):
        if self.evt is not None:
            if self.time is not None:
                self.__on_time(scene)
            elif self.times is not None:
                self.__on_times(scene)

    def __on_time(self, scene):
        """ 处理定时消息. """
        now, dt = scene.clock_info
        if abs(now - self.time) <= 0.1 * dt:
            self.evt(scene)

    def __on_times(self, scene):
        """ 处理事件序列消息. """
        now, dt = scene.clock_info
        for t in self.times:
            if abs(now - t) < 0.1 * dt:
                self.evt(scene)
                break
