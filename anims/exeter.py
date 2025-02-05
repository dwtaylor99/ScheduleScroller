import random

import pygame

from funbase import FunBase

GRAY = (127, 127, 127)
DK_GRAY = (100, 100, 100)
RED = (192, 30, 40)


class Exeter(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/exeter.png'), 0.5).convert_alpha()
        self.x = random.randrange(30, 1200)
        self.y = random.randrange(20, 40)
        self.vel_x = 1
        self.vel_y = 0.4
        self.alpha = 0
        self.delay = 180

    def interocitor(self):
        pygame.draw.polygon(self.screen, GRAY, [(self.x, self.y),
                                                (self.x + 230, self.y),
                                                (self.x + 115, self.y + 215),
                                                (self.x, self.y)])

        self.screen.blit(self.img, (self.x + 1, self.y + 5))

        pygame.draw.polygon(self.screen, DK_GRAY, [(self.x, self.y),
                                                   (self.x + 230, self.y),
                                                   (self.x + 115, self.y + 215),
                                                   (self.x, self.y)], 10)

        pygame.draw.circle(self.screen, DK_GRAY, (self.x + 4, self.y + 4), 10)
        pygame.draw.circle(self.screen, RED, (self.x + 4, self.y + 4), 7)

        pygame.draw.circle(self.screen, DK_GRAY, (self.x + 227, self.y + 4), 10)
        pygame.draw.circle(self.screen, RED, (self.x + 227, self.y + 4), 7)

        pygame.draw.circle(self.screen, DK_GRAY, (self.x + 115, self.y + 211), 10)
        pygame.draw.circle(self.screen, RED, (self.x + 115, self.y + 211), 7)

    def animate(self):
        if self.anim_step == 1:
            self.interocitor()
            self.img.set_alpha(self.alpha)
            self.x += self.vel_x
            self.y += self.vel_y
            self.alpha += 1

            if self.alpha >= 255:
                self.anim_step += 1

        elif self.anim_step == 2:
            self.interocitor()
            self.x += self.vel_x
            self.y += self.vel_y
            self.delay -= 1

            if self.delay <= 0:
                self.anim_step += 1

        elif self.anim_step == 3:
            self.interocitor()
            self.img.set_alpha(self.alpha)
            self.x += self.vel_x
            self.y += self.vel_y
            self.alpha -= 1

            if self.alpha <= 0:
                self.anim_step = 0
