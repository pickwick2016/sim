"""
RenderView 工厂
"""

from . import basic
from . import paint_qt

def make_view(typename=None, **kwargs) -> basic.RenderView:
    """ 创建渲染窗口.
    """
    if typename == 'qt':
        return paint_qt.QtRenderView(**kwargs)

    return basic.RenderView(**kwargs)
