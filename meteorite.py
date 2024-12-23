import random

import pygame
from pygame import Surface

from funbase import FunBase


class Meteorite(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/meteorite.png').convert_alpha()
        self.x = screen.get_width() + random.randrange(10, 400)
        self.y = -random.randrange(10, 300)
        self.vel_x = -5
        self.vel_y = 1.6

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            self.screen.blit(self.img, (self.x, self.y))

            # Stop the animation?
            if self.x < -self.img.get_width() or self.y > self.screen.get_height() / 2:
                self.anim_step = 0
