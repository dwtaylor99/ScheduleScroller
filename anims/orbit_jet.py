import random

import pygame
from pygame import Surface

from funbase import FunBase

XOFFSET = 0
IW = 64
IH = 300
SMOKE_SCALE = 0.5


class OrbitJet(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/orbit_jet.png').convert_alpha(), 0.1)
        self.x = random.randrange(200, screen.get_width() - 300)
        self.y = -200
        self.vel_x = 0
        self.vel_y = 1
        self.alpha = 255
        self.frames = []
        self.frame_index = 0
        self.ticks = 0

        img_sheet = pygame.transform.smoothscale_by(pygame.image.load('images/fun/rocket_smoke_sheet3.png').convert_alpha(), SMOKE_SCALE)

        for i in range(5):
            x = (i * IW + XOFFSET) * SMOKE_SCALE
            y = 0
            w = IW * SMOKE_SCALE
            h = IH * SMOKE_SCALE
            img_sheet.set_clip(pygame.Rect(x, y, w, h))
            self.frames.append(img_sheet.subsurface(img_sheet.get_clip()))

    def animate(self):
        if self.anim_step == 1:
            # Land the Orbit Jet
            super().animate()

            self.frame_index = (self.frame_index + 1) % len(self.frames)
            frame = self.frames[self.frame_index]
            self.screen.blit(frame, (self.x + 17, self.y + self.img.get_height()))

            # Stop the animation?
            if self.y > (self.screen.get_height() // 2) - self.img.get_height():
                self.vel_y = 0
                self.anim_step += 1

        elif self.anim_step == 2:
            # Pause briefly before fading
            super().animate()
            self.ticks += 1
            if self.ticks >= 120:
                self.anim_step += 1

        elif self.anim_step == 3:
            # Fade out
            self.img.set_alpha(self.alpha)
            super().animate()

            self.alpha -= 5
            if self.alpha <= 0:
                self.anim_step = 0
