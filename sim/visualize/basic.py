"""
可视化基础类：
1. RenderView：绘制窗口.
2. Painter：绘制接口.
"""


class Painter:
    """ 绘制接口. """

    def __init__(self):
        """ 初始化. """
        pass

    def draw_circle(self, center, radius):
        """ 绘制圆. """
        pass

    def draw_line(self, p0, p1):
        """ 绘制线. """
        pass

    def draw_rect(self, xy, wh):
        """ 绘制矩形. """
        pass

    def draw_point(self, pt):
        """ 绘制点. """
        pass

    def set_pen(self, color=(0, 0, 0), width=1):
        """ 设置画笔. """
        pass


class RenderView:
    """ 渲染窗口. """

    def __init__(self, **kwargs):
        """ 初始化. """
        pass

    def render(self, scene):
        """ 渲染场景. """
        pass
