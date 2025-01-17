import random

import pygame

from funbase import FunBase


class Starfighter(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/starfighter.png').convert_alpha(), 0.5)
        self.x = screen.get_width() + self.img.get_width() + 10 + random.randrange(50, 500)
        self.y = random.randrange(30, 450)
        self.vel_x = -8
        self.vel_y = 0

        # 50% chance of changing direction and flying left-to-right
        if random.randint(1, 2) > 0:
            self.img = pygame.transform.flip(self.img, True, False)
            self.x = -10 - random.randrange(50, 500)
            self.y = random.randrange(30, 450)
            self.vel_x = -self.vel_x

    def animate(self):
        if self.anim_step == 1:
            super().animate()

            # stop if moving right-to-left
            if self.vel_x < 0 and self.x < -self.img.get_width():
                self.anim_step = 0

            # stop if moving left-to-right
            if self.vel_x > 0 and self.x > self.screen.get_width():
                self.anim_step = 0
