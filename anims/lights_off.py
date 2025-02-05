import pygame

from fonts import FONT_XL, FONT_XXL, FONT_LG
from funbase import FunBase


class LightsOff(FunBase):

    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/lightbulb_off.png'), 0.75).convert_alpha()
        self.img2 = pygame.transform.smoothscale_by(pygame.image.load('images/fun/lightbulb_off.png'), 0.75).convert_alpha()
        self.off1 = pygame.transform.smoothscale_by(pygame.image.load('images/fun/lightbulb_off.png'), 0.75).convert_alpha()
        self.off2 = pygame.transform.smoothscale_by(pygame.image.load('images/fun/lightbulb_off.png'), 0.75).convert_alpha()

        # FONT_XXL.set_bold(True)
        self.turn_down = FONT_XXL.render("TURN DOWN YOUR LIGHTS", True, (161, 35, 14))
        self.where_app = FONT_XL.render("(Where applicable)", True, (52, 51, 194))
        self.loading = FONT_LG.render("Loading...", True, (192, 192, 192))

        self.x = (self.screen.get_width() - self.img.get_width()) // 2
        self.y = 450

        self.x2 = (self.screen.get_width() - self.img.get_width()) // 2
        self.y2 = 450

        self.vel_x = -6
        self.vel_y = 0

        self.vel_x2 = 6
        self.vel_y2 = 0

    def animate(self):
        if self.anim_step == 1:
            self.screen.fill((0, 0, 0))

            self.screen.blit(self.img, (300, self.y))
            self.screen.blit(self.img2, (self.screen.get_width() - self.img2.get_width() - 300, self.y2))

            self.screen.blit(self.turn_down, ((self.screen.get_width() - self.turn_down.get_width()) // 2, self.y + 50))
            self.screen.blit(self.where_app, ((self.screen.get_width() - self.where_app.get_width()) // 2, self.y + 150))
            self.screen.blit(self.loading, (100, self.screen.get_height() - 100))

            self.x2 += self.vel_x2
            self.y2 += self.vel_y2

            if self.x < 300:
                self.anim_step += 1
            self.anim_step = 0
