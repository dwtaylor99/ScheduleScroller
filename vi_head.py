import random

import pygame

from funbase import FunBase


class ViHead(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/vi_head.png').convert_alpha()
        self.x = random.randrange(100, self.screen.get_width() - 200)
        self.y = random.randrange(100, self.screen.get_height() // 2 - 200)
        self.vel_x = (2 - (random.randrange(0, 4))) * 0.2
        self.vel_y = (2 - (random.randrange(0, 4))) * 0.2
        self.alpha = 0

    def animate(self):
        if self.anim_step == 1:
            self.img.set_alpha(self.alpha)
            super().animate()
            self.alpha += 1
            if self.alpha >= 220:
                self.anim_step += 1

        elif self.anim_step == 2:
            self.img.set_alpha(self.alpha)
            super().animate()
            self.alpha -= 1
            if self.alpha <= 0:
                self.anim_step = 0
