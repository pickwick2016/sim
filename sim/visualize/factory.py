"""
RenderView 工厂
"""

from . import basic
from . import paint_qt


def make_view(typename:str='', **kwargs) -> basic.RenderView:
    """ 创建渲染窗口.

    :param typename: 窗口类型， 'qt' 表示创建Qt类型窗口，其他表示默认无窗口.
    """
    if typename == 'qt':
        return paint_qt.QtRenderView(**kwargs)

    return basic.RenderView(**kwargs)
