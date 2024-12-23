import random

import pygame

from funbase import FunBase


class ElSantoFlying(FunBase):
    def __init__(self, screen, target_x, target_y):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/santo_flying.png').convert_alpha(), 2.0)
        self.target_x = target_x
        self.target_y = target_y
        self.x = target_x + 1400
        self.y = -3300
        self.vel_x = -4
        self.vel_y = 10

    def animate(self):
        super().animate()
        if self.y > self.screen.get_height() / 2:
            self.anim_step = 0
