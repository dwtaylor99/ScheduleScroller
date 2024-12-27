import random

import pygame
from pygame import Surface

from funbase import FunBase


class Skydiver(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/skydiver.png').convert_alpha(), 0.5)
        self.x = random.randrange(500, screen.get_width() - 300)
        self.y = -500
        self.vel_x = -2
        self.vel_y = 2
        self.angle = 0
        self.swing = 0.2  # negative = swinging left, positive = swinging right

    def animate(self):
        if self.anim_step == 1:
            self.angle += self.swing
            if self.angle <= -10 or self.angle >= 10:
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
            if self.x < -self.img.get_width() or self.y > self.screen.get_height() // 2:
                self.anim_step = 0
