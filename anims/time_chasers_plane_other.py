import random

import pygame

from funbase import FunBase


class TimeChasersPlaneOther(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/time_chasers_plane_other.png'), 0.2).convert_alpha()
        self.x = screen.get_width() + 500
        self.y = random.randrange(30, 450)
        self.vel_x = -7
        self.vel_y = (2 - (random.randrange(0, 4))) * 0.2

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x < -self.img.get_width():
                self.anim_step = 0
