from math import floor

import pygame

from funbase import FunBase

XOFFSET = 142
YOFFSET = 120
IW = 142
IH = 80


class HorseRunning(FunBase):
    def __init__(self, screen):
        super().__init__(screen)

        img_sheet = pygame.image.load('images/fun/horse_running.png').convert_alpha()
        self.frames = []

        for i in range(12):
            if i == 0:
                img_sheet.set_clip(pygame.Rect(16, 32, IW, IH))
            elif i == 1:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET, 32, IW, IH))
            elif i == 2:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET * 2, 32, IW, IH))
            elif i == 3:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET * 3, 32, IW, IH))
            elif i == 4:
                img_sheet.set_clip(pygame.Rect(16, 32 + YOFFSET, IW, IH))
            elif i == 5:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET, 32 + YOFFSET, IW, IH))
            elif i == 6:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET * 2, 32 + YOFFSET, IW, IH))
            elif i == 7:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET * 3, 32 + YOFFSET, IW, IH))
            elif i == 8:
                img_sheet.set_clip(pygame.Rect(16, 32 + YOFFSET * 2, IW, IH))
            elif i == 9:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET, 32 + YOFFSET * 2, IW, IH))
            elif i == 10:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET * 2, 32 + YOFFSET * 2, IW, IH))
            elif i == 11:
                img_sheet.set_clip(pygame.Rect(16 + XOFFSET * 3, 32 + YOFFSET * 2, IW, IH))
            self.frames.append(pygame.transform.smoothscale_by(img_sheet.subsurface(img_sheet.get_clip()), 1.5).convert_alpha())

        self.img = self.frames[0]
        self.x = 0
        self.y = screen.get_height() // 2 - (IH * 1.5)
        self.vel_x = 10
        self.vel_y = 0
        self.frame_index = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            self.frame_index += 0.5
            if self.frame_index >= len(self.frames):
                self.frame_index = 0
            self.img = self.frames[floor(self.frame_index)]
            if self.x > self.screen.get_width():
                self.anim_step = 0
