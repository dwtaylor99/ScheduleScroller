import random

import pygame
from pygame import Surface

from funbase import FunBase


class ScreamingSkull(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/skull.png').convert_alpha(), 1.0)
        self.x = random.randrange(100, screen.get_width() - 200)
        self.y = screen.get_height() // 4
        self.vel_x = 0
        self.vel_y = 0
        self.scale = 0.1

    def animate(self):
        if self.anim_step == 1:
            self.scale += 0.05

            old_center = self.img.get_rect().center
            new_image = pygame.transform.smoothscale_by(self.img, self.scale)
            new_rect = new_image.get_rect()
            new_rect.center = old_center
            new_rect.x += self.x
            new_rect.y += self.y

            self.screen.blit(new_image, new_rect)
            self.x += self.vel_x
            self.y += self.vel_y

            if self.scale >= 2.5:
                self.anim_step = 0
