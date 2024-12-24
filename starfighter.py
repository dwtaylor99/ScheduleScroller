import random

import pygame

from funbase import FunBase


class Starfighter(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/starfighter.png').convert_alpha(), 0.5)
        self.x = screen.get_width() + self.img.get_width() + 10 + random.randrange(50, 350)
        self.y = random.randrange(30, 450)
        self.vel_x = -8
        self.vel_y = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x < -self.img.get_width():
                self.anim_step = 0
