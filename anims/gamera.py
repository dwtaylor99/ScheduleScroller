import random

import pygame

from funbase import FunBase


class Gamera(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/gamera2.png').convert_alpha()
        self.x = -(self.img.get_width()) - 10
        self.y = random.randrange(30, 450)
        self.vel_x = 4
        self.vel_y = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width() or self.y > self.screen.get_height() / 2:
                self.anim_step = 0
