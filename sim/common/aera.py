"""
封闭区域.
"""

from typing import Optional, Iterable

from sim import vec, Entity


class Area(Entity):
    """ 区域. """

    def __init__(self, name: str = '', path: Iterable = None, **kwargs):
        """ 初始化.

        :param path: 区域的路径（多边形）.
        """
        super().__init__(name=name, **kwargs)
        self._path = [] if path is None else list([vec.vec3(p) for p in path])

    @property
    def path(self):
        return self.path
