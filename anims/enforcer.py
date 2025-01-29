import pygame

from funbase import FunBase


class Enforcer(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/enforcer.png').convert_alpha(), 0.3)
        self.x = screen.get_width()
        self.y = screen.get_height() // 2 - self.img.get_height()
        self.vel_x = -5
        self.vel_y = 0

    def animate(self):
        if self.anim_step == 1:
            super().animate()
            if self.x > self.screen.get_width():
                self.anim_step = 0
