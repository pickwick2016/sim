""" 
接收机.
"""

from __future__ import annotations
from typing import List, Any, Optional

from .. import basic
from .. import vec
from . import util
from . import rules


class Receiver(basic.Entity):
    """ 接收机. """

    def __init__(self, name: str = '', pos=[0, 0], **kwargs):
        """ 初始化.

        :param name: 实体名称.
        :param pos: 位置.
        :see: AerRange.
        """
        super().__init__(name=name, **kwargs)
        self.access_rules.append(rules.receiver_access_signal)

        self.aer_range = util.AerRange(**kwargs)

        self.position = vec.vec(pos)
        self.results = {}

    def reset(self):
        self.results.clear()

    def access(self, others: List[basic.Entity]) -> None:
        self.results.clear()
        super().access(others)

    def detect(self, other) -> Optional[Any]:
        """ 检测目标.  """
        if hasattr(other, 'position') and hasattr(other, 'signal'):
            aer = util.polar(self.position, other.position)
            if self.aer_range.contains(aer):
                return aer[0]

    def __str__(self) -> str:
        if self.results:
            return 'receiver [{}] : {}'.format(self.id, str(self.results))
        return ''
