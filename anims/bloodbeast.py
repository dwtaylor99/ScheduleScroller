import random

import pygame

from funbase import FunBase

SCALE = 1.5


class BloodBeast(FunBase):
    def __init__(self, screen):
        super().__init__(screen)

        filename = "images/fun/bloodbeast_xray_0" + str(random.randint(1, 4)) + ".png"
        self.img = pygame.transform.smoothscale_by(pygame.image.load(filename), SCALE).convert_alpha()

        rand_scale = random.randrange(1, 4) * 0.4
        self.img = pygame.transform.smoothscale_by(self.img, rand_scale)

        self.rotate_speed = (2 - (random.randrange(0, 4)))
        self.angle = 0

        self.x = random.randrange(0, screen.get_width())
        self.y = -random.randrange(30, 500)
        self.vel_x = (2 - (random.randrange(0, 4))) * 0.2
        self.vel_y = 2 + (2 - (random.randrange(0, 4))) * 0.2

    def animate(self):
        if self.anim_step == 1:
            old_center = self.img.get_rect().center
            self.angle = (self.angle + self.rotate_speed) % 360
            new_image = pygame.transform.rotate(self.img, self.angle)
            new_rect = new_image.get_rect()
            new_rect.center = old_center
            new_rect.x += self.x
            new_rect.y += self.y

            self.screen.blit(new_image, new_rect)
            self.x += self.vel_x
            self.y += self.vel_y

            if self.y > self.screen.get_height() // 2:
                self.anim_step = 0
