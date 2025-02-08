import random

import pygame
from pygame import Surface

from funbase import FunBase


class Shuriken(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        rn = random.randint(1, 4)
        if rn == 1:
            self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/shuriken.png'), 0.5).convert_alpha()
        elif rn == 2:
            self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/shuriken2.png'), 0.4).convert_alpha()
        elif rn == 3:
            self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/shuriken3.png'), 0.4).convert_alpha()
        else:
            self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/shuriken4.png'), 0.4).convert_alpha()

        self.x = random.randrange(-500, -150)
        self.y = random.randrange(50, screen.get_height() // 2 - 200)
        self.vel_x = 10 + (random.randrange(0, 3))
        self.vel_y = (2 - (random.randrange(0, 4))) * 0.2
        self.angle = random.randrange(0, 359)
        self.alpha = 255

    def animate(self):
        if self.anim_step == 1:
            self.angle -= 15 % 360

            old_center = self.img.get_rect().center
            new_image = pygame.transform.rotate(self.img, self.angle)
            new_rect = new_image.get_rect()
            new_rect.center = old_center
            new_rect.x += self.x
            new_rect.y += self.y
            self.screen.blit(new_image, new_rect)

            if self.x >= self.screen.get_width() - 90:
                self.x = self.screen.get_width() - 90
                self.vel_x = 0
                self.vel_y = 0
                self.img = new_image.subsurface(new_image.get_clip())
                self.anim_step += 1

            self.x += self.vel_x
            self.y += self.vel_y

        elif self.anim_step == 2:
            self.img.set_alpha(self.alpha)
            self.screen.blit(self.img, (self.x, self.y))
            self.alpha -= 4
            if self.alpha <= 0:
                self.anim_step = 0
