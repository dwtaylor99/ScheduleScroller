import random

import pygame

from funbase import FunBase


class SantaSleigh(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/santa_sleigh.png').convert_alpha(), 0.25)
        self.x = -(self.img.get_width()) - 10
        self.y = random.randrange(300, 400)
        self.vel_x = 4
        self.vel_y = 1

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width():
                self.anim_step = 0
