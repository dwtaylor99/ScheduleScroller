import random

import pygame

from funbase import FunBase


class SOL(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/sol.png').convert_alpha(), 0.25)
        self.x = -(self.img.get_width()) - 10
        self.y = random.randrange(10, 400)
        self.vel_x = 3
        self.vel_y = (2 - (random.randrange(0, 4))) * 0.2

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width():
                self.anim_step = 0
