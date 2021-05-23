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

    def __init__(self, name='', **kwargs) -> None:
        super().__init__(name=name, **kwargs)
        self.access_rules.append(Detector._access_detect_result)
        self._results = {}

    def reset(self):
        super().reset()
        self._results.clear()

    def access(self, others: List[sim.Entity]):
        """ 传感器的默认交互. 
        
        1. 探测和收集每一个实体，收集结果
        2. 处理探测结果，加工生成用户所需探测结果.
        """
        super().access(others)
        self._update_results()

    def need_detect(self, other) -> bool:
        """ 判断是否需要检测. """
        return True

    def detect(self, other) -> Optional[Any]:
        """ 获取单次探测结果. """
        return None

    def _access_detect_result(self, other):
        """ 收集有效探测结果. """
        assert other.is_active
        
        if self.need_detect(other):
            ret = self.detect(other)
            if ret is not None:
                self._results[other.id] = ret

    def _update_results(self):
        """ 更新/处理探测结果. 
        
        处理当前交互产生的有效探测结果，生成最终探测结果.
        """
        pass
