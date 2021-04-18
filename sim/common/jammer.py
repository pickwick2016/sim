""" 
常见处置设备.
"""

from .. import basic
from .. import vec


class Jammer(basic.Entity):
    """ 干扰器. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.power_on = False
        self.position = kwargs['pos'] if 'pos' in kwargs else vec.vec([0, 0])

    def info(self) -> str:
        if self.power_on:
            return 'jammer [{}] : on'.format(self.id)
        return ''
