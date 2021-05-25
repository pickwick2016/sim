import copy
from sim.basic import Scenario

import sim
from sim import vec, Scenario


class ResultRecord:
    """ 结果记录器. """

    def __init__(self, obj_ref, attr='results', active=False) -> None:
        self.ref = obj_ref
        self.results = []
        self.counter: int = 0
        self.attr: str = attr
        self.active = active

    def __call__(self, scene: Scenario):
        self.counter += 1
        if obj := scene.find(self.ref, active=self.active):
            if hasattr(obj, self.attr):
                ret = getattr(obj, self.attr)
                if ret is not None:
                    ret2 = copy.copy(ret)
                    self.results.append(ret2)


class Target(sim.Entity):
    """ 测试目标. """

    def __init__(self, name: str='', pos=(0, 0), vel=None, **kwargs):
        """ 创建函数.

        :param kwargs: 可以动态创建属性，配合测试.
        """
        super().__init__(name=name, **kwargs)
        self.position = vec.vec(pos)
        self.velocity = vec.zeros_like(self.position) if vel is None else vec.vec(vel) 
        self.life = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def step(self, tt):
        _, dt = tt
        if self.life is not None:
            self.life -= dt
            if self.life <= 0.0:
                self.deactive()
        if self.is_active:
            self.position += self.velocity * dt
