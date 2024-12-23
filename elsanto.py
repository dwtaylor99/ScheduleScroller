import random

import pygame

from funbase import FunBase


class ElSanto(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/el_santo.png').convert_alpha()
        self.x = random.randrange(100, 1800)
        self.y = 539
        self.vel_x = 0
        self.vel_y = -0.7

    def animate(self):
        super().animate()
        if self.y + self.img.get_height() < self.screen.get_height() / 2:
            self.vel_y = -self.vel_y
            if self.y > self.screen.get_height() / 2:
                self.anim_step = 0
