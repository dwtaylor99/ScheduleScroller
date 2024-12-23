import random

import pygame

from funbase import FunBase


class VampireWoman(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/santo_vs_vampire_women.png').convert_alpha()
        self.x = random.randrange(100, 1200)
        self.y = 539
        self.vel_x = 0
        self.vel_y = -0.5
        self.angle = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.y + (self.img.get_height() / 2) < self.screen.get_height() / 2:
                self.vel_x = 0
                self.vel_y = 0
                self.anim_step += 1

        elif self.anim_step == 2:
            self.angle += 10
            if self.angle >= 90:
                self.angle = 90
            self.img = pygame.transform.rotate(self.img, self.angle)
            self.screen.blit(self.img, (self.x, self.y))
            self.x -= 100
            self.y += 10

            if self.y > self.screen.get_height() / 2:
                self.anim_step = 0
