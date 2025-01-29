import random

import pygame
from pygame import Surface

from funbase import FunBase


class Fingal(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/fingal2.png'), 0.5).convert_alpha()
        self.x = random.randrange(1000, screen.get_width())
        self.y = screen.get_height() // 2
        self.vel_x = -4
        self.vel_y = -4
        self.angle = 0
        self.scale = 1.0

    def animate(self):
        if self.anim_step == 1:
            self.angle -= 5 % 360
            self.scale -= 0.005
            if self.scale < 0.001:
                self.scale = 0.001

            old_center = self.img.get_rect().center
            new_image = pygame.transform.smoothscale_by(pygame.transform.rotate(self.img, self.angle), self.scale)
            new_rect = new_image.get_rect()
            new_rect.center = old_center
            new_rect.x += self.x
            new_rect.y += self.y

            self.screen.blit(new_image, new_rect)
            self.x += self.vel_x
            self.y += self.vel_y

            if self.scale <= 0.001:
                self.anim_step = 0
