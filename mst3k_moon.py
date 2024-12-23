import random

import pygame

from funbase import FunBase


class MST3KMoon(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/mst3k_moon.png').convert_alpha(), 0.5)
        self.x = -(self.img.get_width()) - 10
        self.y = random.randrange(10, 400)
        self.vel_x = 3
        self.vel_y = 1 + (random.randrange(-2, 2) * 0.01)

    def animate(self):
        super().animate()
        if self.x > self.screen.get_width():
            self.anim_step = 0
