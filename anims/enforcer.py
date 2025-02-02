import pygame

from funbase import FunBase


class Enforcer(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/enforcer.png'), 0.3).convert_alpha()
        self.x = screen.get_width()
        self.y = screen.get_height() // 2 - self.img.get_height()
        self.vel_x = -5
        self.vel_y = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x < -400:
                self.anim_step = 0


class EnforcerReverse(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.flip(pygame.transform.smoothscale_by(pygame.image.load('images/fun/enforcer.png'), 0.3), True, False).convert_alpha()
        self.x = -self.img.get_width()
        self.y = screen.get_height() // 2 - self.img.get_height()
        self.vel_x = 5
        self.vel_y = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width():
                self.anim_step = 0
