import random

import pygame
from pygame import Surface

from funbase import FunBase


class Pizza(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/pizza.png').convert_alpha(), 0.5)
        self.img2 = pygame.image.load('images/fun/munchie.png')
        self.x = -700
        self.y = random.randrange(10, 450)
        self.vel_x = 6
        self.vel_y = 0
        self.angle = 0
        self.x2 = screen.get_width()
        self.y2 = screen.get_height() // 2 - self.img2.get_height()
        self.vel_x2 = -1.5

    def animate(self):
        if self.anim_step == 1:
            self.angle -= 5 % 360

            old_center = self.img.get_rect().center
            new_image = pygame.transform.rotate(self.img, self.angle)
            new_rect = new_image.get_rect()
            new_rect.center = old_center
            new_rect.x += self.x
            new_rect.y += self.y

            self.screen.blit(new_image, new_rect)
            self.x += self.vel_x
            self.y += self.vel_y

            self.screen.blit(self.img2, (self.x2, self.y2))
            self.x2 += self.vel_x2
            if self.x2 <= self.screen.get_width() - 200:
                self.vel_x2 = -self.vel_x2

            if self.x >= self.screen.get_width():
                self.anim_step = 0
