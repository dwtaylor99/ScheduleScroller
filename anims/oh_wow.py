import pygame
from pygame import Surface

from funbase import FunBase

pygame.init()
FONT = pygame.font.Font("fonts/HandelGo.ttf", 36)
WOW = FONT.render("Oh, wow!", True, (0, 0, 0))


class OhWow(FunBase):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/oh_wow.png'), 0.25).convert_alpha()
        self.x = -self.img.get_width()
        self.y = (self.screen.get_height() // 2) - self.img.get_height()
        self.vel_x = 1

    def animate(self):
        if self.anim_step == 1:
            super().animate()

            # Oh, wow!
            pygame.draw.rect(self.screen, (192, 192, 192), (self.x, self.y - 30, WOW.get_width() + 40, WOW.get_height() + 40), 0, 10)
            self.screen.blit(WOW, (self.x + 20, self.y - 20))

            self.screen.blit(self.img, (self.x, self.y))
            self.x += self.vel_x
            if self.x >= 10:
                self.vel_x = -self.vel_x

            # Stop the animation?
            if self.x < -self.img.get_width():
                self.anim_step = 0
