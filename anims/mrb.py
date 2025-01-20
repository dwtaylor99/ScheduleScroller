import random

import pygame

from funbase import FunBase


class MrB(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/mrb_body.png').convert_alpha()
        self.img2 = pygame.image.load('images/fun/mrb_head.png').convert_alpha()
        self.img3 = pygame.image.load('images/fun/mrb_l_arm.png').convert_alpha()
        self.img4 = pygame.image.load('images/fun/mrb_r_arm.png').convert_alpha()
        self.img5 = pygame.image.load('images/fun/mrb_l_leg.png').convert_alpha()
        self.img6 = pygame.image.load('images/fun/mrb_r_leg.png').convert_alpha()
        self.x = random.randrange(100, 1800)
        self.y = 539
        self.vel_x = 0
        self.vel_y = -0.7

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.y + self.img.get_height() < self.screen.get_height() / 2:
                self.vel_y = -self.vel_y
                if self.y > self.screen.get_height() / 2:
                    self.anim_step = 0
