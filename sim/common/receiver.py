""" 
接收机.
"""

from __future__ import annotations
from collections import namedtuple
from typing import Any, Optional

from .. import vec
from . import util
from . import detector


class Receiver(detector.Detector):
    """ 接收机. 
    
    可以探测作用范围内以下实体：
    * 具有属性：signal
    * 具有属性：position

    设备属性:
    * position: 设备位置.  
    * result: 探测结果. List[(time, value)]. 其中，value 是方位角度.
    """

    def __init__(self, name: str = '', pos=[0, 0], rate=1.0, **kwargs):
        """ 初始化.

        :param name: 实体名称.
        :param pos: 位置.
        :param rate: 更新频率.
        :see: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.position = vec.vec3(pos)
        self.rate = rate
        self._outputs = {}

    @property
    def result(self) -> Optional[list]:
        """ 获取当前探测结果. """
        now = self.clock_info[0]
        ret = list([v for v in self._outputs.values() if v[0] == now])
        return ret if ret else None

    def need_detect(self, other) -> bool:
        """ 判断是否应该检测目标. """
        if hasattr(other, 'position') and hasattr(other, 'signal'):
            if other.id in self._outputs:
                now = self.clock_info[0]
                if self.rate > 0.0 and (now - self._outputs[other.id].time) < self.rate:
                    return False
            return True
        return False

    def detect(self, other) -> Optional[Any]:
        """ 检测目标.  """
        if hasattr(other, 'position') and hasattr(other, 'signal'):
            aer = util.polar(self.position, other.position)
            if self.aer_range.contain(aer):
                return aer[0]
        return None

    def _update_results(self):
        now = self.clock_info[0]
        for k, v in self._results.items():
            self._outputs[k] = ReceiverResult(now, v, k)

        for k, v in self._outputs.copy().items():
            if now - v[0] > self.rate:
                self._outputs.pop(k)

        self._results.clear()

    def __str__(self) -> str:
        return 'receiver [{}] : {}'.format(self.id, self.result)


# 侦察设备探测结果.
ReceiverResult = namedtuple('ReceiverResult', ['time', 'value', 'obj_id'])
