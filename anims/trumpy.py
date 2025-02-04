import random

import pygame

from funbase import FunBase


class Trumpy(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/trumpy.png').convert_alpha()
        self.img_simon = pygame.transform.smoothscale_by(pygame.image.load('images/fun/simon.png'), 0.1).convert_alpha()
        self.img_chair = pygame.transform.smoothscale_by(pygame.image.load('images/fun/chair.png'), 0.3).convert_alpha()

        self.x = random.randrange(100, self.screen.get_width() - 1000)
        self.y = 539
        self.vel_x = 0
        self.vel_y = -2

        self.simon_x = random.randrange(30, self.screen.get_width() - 300)
        self.simon_y = -30
        # self.simon_vel_x = 2 - (random.randrange(0, 4))
        self.simon_vel_x = 2
        self.simon_vel_y = 2
        self.simon_angle = 0
        self.simon_rot = random.randrange(1, 4)

        self.chair_x = random.randrange(30, self.screen.get_width() - 300)
        self.chair_y = -30
        # self.chair_vel_x = 2 - (random.randrange(0, 4))
        self.chair_vel_x = 2
        self.chair_vel_y = 3
        self.chair_angle = 0
        self.chair_rot = random.randrange(1, 4)

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.y <= self.img.get_height():
                self.vel_x = 0
                self.vel_y = 0
                self.anim_step += 1

        elif self.anim_step == 2:
            super().animate()

            self.simon_angle = (self.simon_angle + self.simon_rot) % 360
            old_center_simon = self.img_simon.get_rect().center
            new_simon = pygame.transform.rotate(self.img_simon, self.simon_angle)
            new_simon_rect = new_simon.get_rect()
            new_simon_rect.center = old_center_simon
            new_simon_rect.x = self.simon_x
            new_simon_rect.y = self.simon_y

            self.screen.blit(new_simon, new_simon_rect)
            self.simon_x += self.simon_vel_x
            self.simon_y += self.simon_vel_y

            self.chair_angle = (self.chair_angle + self.chair_rot) % 360
            old_center_chair = self.img_chair.get_rect().center
            new_chair = pygame.transform.rotate(self.img_chair, self.chair_angle)
            new_chair_rect = new_chair.get_rect()
            new_chair_rect.center = old_center_chair
            new_chair_rect.x = self.chair_x
            new_chair_rect.y = self.chair_y

            self.screen.blit(new_chair, new_chair_rect)
            self.chair_x += self.chair_vel_x
            self.chair_y += self.chair_vel_y

            if self.simon_y > self.screen.get_height() // 2 and self.chair_y > self.screen.get_height() // 2:
                self.vel_y = 2
                self.anim_step += 1

        elif self.anim_step == 3:
            super().animate()
            if self.y > self.screen.get_height() // 2:
                self.anim_step = 0
