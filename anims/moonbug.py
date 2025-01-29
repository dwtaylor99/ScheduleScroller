import pygame

from funbase import FunBase


class MoonBug(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/moon_bug.png'), 2.0).convert_alpha()
        self.x = -(self.img.get_width()) - 10
        self.y = screen.get_height() // 2 - self.img.get_height()
        self.vel_x = 5
        self.vel_y = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width():
                self.anim_step = 0
