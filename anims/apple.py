import random

import pygame

from funbase import FunBase


class Apple(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.angle = 0
        self.scale = 0.5
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/apple.png').convert_alpha(), self.scale)
        self.x = 800
        self.y = screen.get_height() / 2
        self.vel_x = -6
        self.vel_y = -6

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            # self.img = pygame.transform.rotozoom(self.img, self.angle, self.scale)
            self.img = pygame.transform.smoothscale_by(self.img, self.scale)
            # self.angle += 1
            self.scale -= 0.001
            if self.scale < 0.00001:
                self.scale = 0.00001
            # print(self.scale)
            if self.y <= 200:
                # self.img = pygame.transform.rotozoom(self.img, self.angle, 0.94)
                self.vel_x = 0
                self.vel_y = 5
                self.anim_step += 1

        elif self.anim_step == 2:
            super().animate()
            print(self.x, self.y, self.scale)
            if self.y > self.screen.get_height() / 2:
                self.anim_step = 0
