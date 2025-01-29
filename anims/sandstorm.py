import random

import pygame

from funbase import FunBase


class SandStorm(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        scale = 0.3 * random.randrange(1, 6)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/sand_storm.png'), scale).convert_alpha()
        self.x = -self.img.get_width() - random.randrange(50, 250)
        self.y = random.randrange(30, 500)
        self.vel_x = random.randrange(4, 6)
        self.vel_y = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width() or self.y > self.screen.get_height() / 2:
                self.anim_step = 0
