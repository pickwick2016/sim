from sim import Entity


class Jammer(Entity):
    """ 干扰器. """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.power_on = False
        self.position = kwargs['pos']

    def info(self) -> str:
        if self.power_on:
            return 'jammer [{}] : on'.format(self.id)
        return ''
