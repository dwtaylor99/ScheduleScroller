import random

import pygame
from pygame import Surface

from funbase import FunBase


class Forklift(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/forklift.png'), 0.75).convert_alpha()
        self.x = -self.img.get_width()
        self.y = random.randrange(50, screen.get_height() // 2 - 200)
        self.vel_x = 5
        self.vel_y = (2 - (random.randrange(0, 4))) * 0.2
        self.angle = 0

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

            if self.x >= self.screen.get_width():
                self.anim_step = 0
