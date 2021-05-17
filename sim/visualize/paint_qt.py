"""
基于 PyQt 的可视化界面.
"""

from __future__ import annotations

import sys
from threading import Thread

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen, QTransform
from PyQt5.QtCore import QPointF, QRectF

from .basic import RenderView, Painter
from .paint_scene_simple import SimplePaint


class QtRenderView(RenderView):
    """ 基于 QT 的显示窗口. """

    def __init__(self, win_size=(800, 600), world=None, **kwargs) -> None:
        """ 初始化.
        
        :param win_size: 窗口大小. (sx, sy)
        :param world: 世界范围 (left, top, right, bottom)
        """
        super().__init__()
        self.win_size = win_size
        self.world_rect = world

        self.app = QApplication(sys.argv)
        self.win = SceneWidget(self.win_size, self.world_rect)
        self.ui_thread = Thread(target=self.loop)

    def loop(self):
        sys.exit(self.app.exec_())

    def render(self, scene):
        self.win.scene = scene
        self.win.update()
        QApplication.processEvents()


class QtPainter(Painter):
    """ QT 绘图设备. """

    def __init__(self, qp: QPainter):
        super().__init__()
        self.qp = qp

    def draw_point(self, pt):
        self.qp.drawPoint(QPointF(pt[0], pt[1]))

    def draw_line(self, p0, p1):
        self.qp.drawLine(QPointF(p0[0], p0[1]), QPointF(p1[0], p1[1]))

    def draw_circle(self, center, radius):
        top_left = QPointF(center[0] - radius, center[1] + radius)
        bottom_right = QPointF(center[0] + radius, center[1] - radius)
        r = QRectF(top_left, bottom_right)
        self.qp.drawEllipse(r)

    def draw_rect(self, xy, wh):
        top_left = QPointF(xy[0] - wh[0], xy[1] + wh[1])
        bottom_right = QPointF(xy[0] + wh[0], xy[1] - wh[1])
        r = QRectF(top_left, bottom_right)
        self.qp.drawRect(r)

    def set_pen(self, color=None, width=1):
        pen_color = QColor(0, 0, 0) if color is None else QColor(
            color[0], color[1], color[2])
        pen = QPen(pen_color, width)
        self.qp.setPen(pen)


class SceneWidget(QWidget):
    """ 场景显示窗口. """

    def __init__(self, window_size, world):
        super().__init__()
        self.win_size = (max(window_size[0], 600), max(window_size[1], 400))
        self.world_rect = world
        self.paint_policy = SimplePaint()
        self.scene = None
        self.initUI()

    def initUI(self):
        self.resize(self.win_size[0], self.win_size[1])
        self.setWindowTitle('sim framework')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.scene:
            if self.world_rect is None:
                s = self.rect().size()
                w, h = s.width(), s.height()
                qp.setWindow(-w / 2, h / 2, w, -h)
            else:
                r = self.world_rect
                qp.setWindow(r[0], r[1], r[2]-r[0], r[3]-r[1])

            qp2 = QtPainter(qp)
            self.drawScene(qp2)
        qp.end()

    def drawScene(self, qp):
        for e in self.scene.active_entities:
            self.paint_policy.paint(qp, e)
