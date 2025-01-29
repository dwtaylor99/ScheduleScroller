import random

import pygame

from funbase import FunBase


class ZapBeer(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/ZapRowsdower.png').convert_alpha()
        self.img2 = pygame.transform.smoothscale_by(pygame.image.load('images/fun/beer_on_sun.png'), 0.75).convert_alpha()
        self.x = random.randrange(100, self.screen.get_width() - 1000)
        self.y = 539
        self.vel_x = 0
        self.vel_y = -1
        self.alpha = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.y <= self.img.get_height():
                self.vel_x = 0
                self.vel_y = 0
                self.anim_step += 1

        elif self.anim_step == 2:
            super().animate()
            self.img2.set_alpha(self.alpha)
            self.screen.blit(self.img2, (self.x + 220, self.y - 280))
            self.alpha += 1
            if self.alpha >= 255:
                self.anim_step += 1

        elif self.anim_step == 3:
            super().animate()
            self.img2.set_alpha(self.alpha)
            self.screen.blit(self.img2, (self.x + 220, self.y - 280))
            self.alpha -= 1
            if self.alpha <= 0:
                self.vel_y = 1
                self.anim_step += 1

        elif self.anim_step == 4:
            super().animate()
            if self.y > self.screen.get_height() / 2:
                self.anim_step = 0
