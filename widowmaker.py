import random

import pygame

from funbase import FunBase


class Widowmaker(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/widowmaker.png').convert_alpha(), 0.25)
        self.x = -(self.img.get_width()) - 600
        self.y = random.randrange(10, 400)
        self.vel_x = 2.5
        self.vel_y = (2 - (random.randrange(0, 4))) * 0.2

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width():
                self.anim_step = 0
