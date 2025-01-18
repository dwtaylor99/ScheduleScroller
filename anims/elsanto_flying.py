import random

import pygame

from funbase import FunBase


class ElSantoFlying(FunBase):

    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/santo_flying.png').convert_alpha(), 2.0)
        self.x = random.randrange(500, 1200)
        self.y = -300

        self.vel_x = -4
        self.vel_y = 10

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.y > self.screen.get_height() / 2:
                self.anim_step = 0
