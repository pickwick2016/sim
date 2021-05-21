""" 
接收机.
"""

from __future__ import annotations
from typing import List, Any, Optional, overload

from .. import basic
from .. import vec
from . import util
from . import rules
from . import detector


class Receiver(detector.Detector):
    """ 接收机. 
    
    可以探测作用范围内以下实体：
    * 具有属性：signal
    * 具有属性：position

    探测结果：
    * 目标方位
    """

    def __init__(self, name: str = '', pos=[0, 0], **kwargs):
        """ 初始化.

        :param name: 实体名称.
        :param pos: 位置.
        :see: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.aer_range = util.AerRange(**kwargs)
        self.position = vec.vec(pos)

    def detect(self, other) -> Optional[Any]:
        """ 检测目标.  """
        if hasattr(other, 'position') and hasattr(other, 'signal'):
            aer = util.polar(self.position, other.position)
            if self.aer_range.contains(aer):
                return aer[0]
        return None

    def __str__(self) -> str:
        if self.results:
            return 'receiver [{}] : {}'.format(self.id, str(self.results))
        return ''
