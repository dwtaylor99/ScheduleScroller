import random

import pygame
from pygame import Surface

from funbase import FunBase


class Pumaman(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/pumaman.png').convert_alpha(), 0.5)
        self.x = -400
        self.y = random.randrange(40, screen.get_height() // 2 - 100)
        self.vel_x = 7
        self.vel_y = 0
        self.angle = 0
        self.swing = 0.5  # negative = swinging left, positive = swinging right

    def animate(self):
        if self.anim_step == 1:
            self.angle += self.swing
            if self.angle <= -20 or self.angle >= 20:
                self.swing = -self.swing

            old_center = self.img.get_rect().center
            new_image = pygame.transform.rotate(self.img, self.angle)
            new_rect = new_image.get_rect()
            new_rect.center = old_center
            new_rect.x += self.x
            new_rect.y += self.y

            self.screen.blit(new_image, new_rect)
            self.x += self.vel_x
            self.y += self.vel_y

            # Stop the animation?
            if self.x > self.screen.get_width():
                self.anim_step = 0
