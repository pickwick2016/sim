"""
光电探测设备.
"""

from __future__ import annotations
from typing import List, Any, Optional
from enum import Enum

from .. import basic
from .. import vec
from . import util


class EoState(Enum):
    StandBy = 0
    Guide = 1
    Track = 2


class EoDetector(basic.Entity):
    """ 光电探测设备. """

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)
        self.results = {}
        self.aer_range = util.AerRange(**kwargs)
        self.delta = util.rad(0.5)

        self.ae = vec.vec([0, 0])
        self.state = EoState.StandBy
        self.guide_ae = None

    def step(self, clock):
        if self.state == EoState.Guide:
            if self.guide_ae is not None:
                self.ae = self.guide_ae

    def access(self, others: List[basic.Entity]) -> None:
        self.results.clear()
        super().access(others)

    def detect(self, other) -> Optional[Any]:
        """ 检测目标. """
        if hasattr(other, 'position'):
            aer = util.polar(self.position, other.position)
            if self.aer_range.contains(aer):
                pass
