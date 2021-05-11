import time
import math
import pygame

from sim.common import Uav, Jammer, Radar
from sim import vec


class PgPainter:
    """ 绘图器.
    """

    def __init__(self, sr=(600, 600), wr=(300, 300), dt=0.1):
        self.screen_rect = sr
        self.world_rect = wr
        self.screen = None
        self.dt = dt
        self.inited = False

    def init(self):
        if not self.inited:
            pygame.init()
            self.screen = pygame.display.set_mode(self.screen_rect)
            self.inited = True
        return self.inited

    def render(self, scene):
        if self.init():
            self.draw_background()
            for e in scene.entities:
                draw_entity(self, e)
            self.update()

    def fill(self, color=(255, 255, 255)):
        self.screen.fill(color)

    def circle(self, pt, color, r=4, w=1):
        pt2 = self._transform((pt[0], pt[1]))
        pygame.draw.circle(self.screen, color, pt2, r, w)

    def rect(self, pt, color, r=2, w=1):
        pt2 = self._transform((pt[0], pt[1]))
        rect_ = pygame.Rect((pt2[0] - r, pt2[1] - r), (2 * r, 2 * r))
        pygame.draw.rect(self.screen, color, rect_, w)

    def update(self):
        # pygame.display.update()
        pygame.display.flip()
        if self.dt > 0:
            time.sleep(self.dt)

    def draw_background(self):
        self.fill()
        sr, wr = self.screen_rect, self.world_rect
        pt0, pt1 = self._transform((0, wr[1] / 2)), self._transform((0, -wr[1] / 2))
        pygame.draw.line(self.screen, (0, 0, 0), pt0, pt1, 2)
        pt0, pt1 = self._transform((wr[0] / 2, 0)), self._transform((-wr[0] / 2, 0))
        pygame.draw.line(self.screen, (0, 0, 0), pt0, pt1, 2)

    def _transform(self, pt):
        sr, wr = self.screen_rect, self.world_rect
        x = pt[0] * sr[0] / float(wr[0]) + sr[0] / 2.0
        y = - pt[1] * sr[1] / float(wr[1]) + sr[1] / 2.0
        return x, y


def draw_entity(painter, e):
    if isinstance(e, Uav):
        draw_uav(painter, e)
    elif isinstance(e, Radar):
        draw_radar(painter, e)
    elif isinstance(e, Jammer):
        draw_jammer(painter, e)


def draw_uav(painter, uav):
    if uav.is_active():
        painter.circle((uav.position[0], uav.position[1]), (0, 0, 255))


def draw_radar(painter, radar):
    if radar.is_active():
        color = (255, 0, 0)
        painter.rect((radar.position[0], radar.position[1]), color, 4)
        for _, ret in radar.results.items():
            d, a = ret[1]
            pt = radar.position + vec.vec([d * math.cos(a), d * math.sin(a)])
            painter.rect(pt, color, 1)


def draw_jammer(painter, jammer):
    if jammer.is_active():
        color = (200, 0, 0)
        painter.rect((jammer.position[0], jammer.position[1]), color, 4)
