import random

import pygame

from colors import RED
from funbase import FunBase


pygame.init()
SCALE = 0.8

PATH = "images/fun/"
HEARTS = ["candy_heart_green.png", "candy_heart_blue.png", "candy_heart_purple.png", "candy_heart_yellow.png",
          "candy_heart_orange.png", "candy_heart_pink.png"]
PHRASES = ["YOU'LL DO", "THAT HAIR", "WEIRD|FACE", "BITE ME", "MY NEEDS", "LIKE A|BROTHER", "GET OUT",
           "OWIE|OWIE|OWIE", "LOVE ME", "STILL MAD", "DROP 'EM", "I'M|TESTED", "CAN'T|LEAVE|COUNTY"]
FONT = pygame.font.Font("fonts/Inter.ttf", 24)


class CandyHeartSnow(FunBase):
    def __init__(self, screen):
        super().__init__(screen)

        filename = PATH + random.choice(HEARTS)
        self.img = pygame.transform.smoothscale_by(pygame.image.load(filename).convert_alpha(), SCALE)
        phrase = random.choice(PHRASES)
        lines = phrase.split("|")

        y = 40
        if len(lines) == 2:
            y = 22
        elif len(lines) == 3:
            y = 12
        for line in lines:
            txt = FONT.render(line, True, RED)
            self.img.blit(txt, ((self.img.get_width() - txt.get_width()) // 2, y))
            y += 30

        rand_scale = random.randrange(1, 4) * 0.15
        # rand_scale = random.randrange(1, 4) * 0.4
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
