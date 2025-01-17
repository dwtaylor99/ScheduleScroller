import random

import pygame

from funbase import FunBase


class WhiteDot(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/white_dot.png').convert_alpha(), 1.0)
        self.x = -(self.img.get_width()) - 10
        self.y = random.randrange(100, screen.get_height() // 2 - 200)
        self.vel_x = 2
        self.vel_y = 0
        self.scale = 1.0
        self.swing = 0.005  # negative = swinging left, positive = swinging right

    def animate(self):
        if self.anim_step == 1:
            # super().animate()

            self.scale += self.swing
            if self.scale <= 1.0 or self.scale >= 1.25:
                self.swing = -self.swing

            temp_img = pygame.transform.smoothscale_by(self.img, self.scale).convert_alpha()
            self.screen.blit(temp_img, (self.x, self.y))
            self.x += self.vel_x
            self.y += self.vel_y

            if self.x > self.screen.get_width():
                self.anim_step = 0
