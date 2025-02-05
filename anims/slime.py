import pygame

from funbase import FunBase


class Slime(FunBase):

    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/slime.png').convert_alpha()
        self.img.set_alpha(127)
        self.x = 0
        self.y = -self.img.get_height()
        self.vel_x = 0
        self.vel_y = 5
        self.temp_surf = pygame.Surface((self.screen.get_width(), self.screen.get_height() // 2))

    def animate(self):
        if self.anim_step == 1:

            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img, (self.x + 720, self.y))
            self.screen.blit(self.img, (self.x + 1440, self.y))

            pygame.draw.rect(self.temp_surf, (115, 178, 3), (0, 0, self.temp_surf.get_width(), self.temp_surf.get_height()))
            self.temp_surf.set_alpha(127)
            self.screen.blit(self.temp_surf, (0, self.y - self.temp_surf.get_height()))

            self.x += self.vel_x
            self.y += self.vel_y

            if self.y - self.temp_surf.get_height() > self.screen.get_height() // 2:
                self.anim_step = 0
