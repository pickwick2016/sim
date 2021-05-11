"""
简易绘制策略.
"""

from __future__ import annotations
from sim.visualize import paint_qt

from .basic import Painter
from sim.common import Uav, Jammer, Radar


class SimplePaint:
    """ 简单绘制策略. """

    def __init__(self):
        pass

    def paint(self, painter, obj):
        """ 绘制实体. """
        if isinstance(obj, Uav):
            self.paint_uav(painter, obj)
        elif isinstance(obj, Jammer):
            self.paint_jammer(painter, obj)
        elif isinstance(obj, Radar):
            self.paint_radar(painter, obj)
        else:
            self.paint_default(painter, obj)

    def paint_uav(self, painter: Painter, uav):
        pos = uav.position
        painter.set_pen(color=(0, 0, 225), width=2)
        painter.draw_point(pos)
        painter.draw_circle(pos, 5)

    def paint_radar(self, painter, radar):
        pos = radar.position
        painter.set_pen(color=(0, 225, 0), width=2)
        painter.draw_rect(pos, [3, 3])

    def paint_jammer(self, painter, jammer):
        pos = jammer.position
        color = (225, 0, 0) if jammer.power_on else (0, 225, 0)
        painter.set_pen(color=color, width=2)
        painter.draw_rect(pos, [3, 3])

    def paint_default(self, painter, obj):
        pass
