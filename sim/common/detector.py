"""
探测器.
"""

from typing import Optional, Any, List
import sim


class Detector(sim.Entity):
    """ 侦察/检测设备. 
    
    通过扩展以下接口，实现探测功能：
    * Detector.detect(other)：获取单次探测结果.
    * Detector._update_results(): 在交互过后，整体更新探测结果.
    * Detector._results: 获取当前临时处理结果，经处理后可以生成用户所需探测结果.
    """

    def __init__(self, name='') -> None:
        super().__init__(name=name)
        self.access_rules.append(Detector._access_detect_result)
        self._results = {}

    def reset(self):
        super().reset()
        self._results.clear()

    def access(self, others: List[sim.Entity]):
        self._results.clear()
        super().access(others)
        self._update_results()

    def detect(self, other) -> Optional[Any]:
        """ 获取单次探测结果. """
        return None

    def _access_detect_result(self, other):
        if ret := self.detect(other):
            self._results[other.id] = ret

    def _update_results(self):
        """ 更新/处理侦察结果. """
        pass
