import random

import pygame

from funbase import FunBase

SCALE = 0.15
XOFFSET = 200 * SCALE
YOFFSET = 188 * SCALE
IW = 116 * SCALE
IH = 128 * SCALE


class SnowFlake(FunBase):
    def __init__(self, screen):
        super().__init__(screen)

        img_sheet = pygame.transform.smoothscale_by(pygame.image.load('images/fun/snowflakes2.png'), SCALE).convert_alpha()
        i = random.randint(1, 9)
        if i == 1:
            img_sheet.set_clip(pygame.Rect(0, 0, IW, IH))
        elif i == 2:
            img_sheet.set_clip(pygame.Rect(XOFFSET, 0, IW, IH))
        elif i == 3:
            img_sheet.set_clip(pygame.Rect(XOFFSET * 2, 0, IW, IH))
        elif i == 4:
            img_sheet.set_clip(pygame.Rect(0, YOFFSET, IW, IH))
        elif i == 5:
            img_sheet.set_clip(pygame.Rect(XOFFSET, YOFFSET, IW, IH))
        elif i == 6:
            img_sheet.set_clip(pygame.Rect(XOFFSET * 2, YOFFSET, IW, IH))
        elif i == 7:
            img_sheet.set_clip(pygame.Rect(0, YOFFSET * 2, IW, IH))
        elif i == 8:
            img_sheet.set_clip(pygame.Rect(XOFFSET, YOFFSET * 2, IW, IH))
        elif i == 9:
            img_sheet.set_clip(pygame.Rect(XOFFSET * 2, YOFFSET * 2, IW, IH))

        rand_scale = random.randrange(1, 4) * 0.4
        self.img = pygame.transform.smoothscale_by(img_sheet.subsurface(img_sheet.get_clip()), rand_scale)

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
