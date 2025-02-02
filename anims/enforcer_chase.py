import pygame

import triviavox
from funbase import FunBase

clock = pygame.time.Clock()


class EnforcerChase(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/enforcer.png'), 0.3).convert_alpha()
        self.ryder = pygame.transform.smoothscale_by(pygame.image.load('images/fun/ryder_head.png'), 0.2).convert_alpha()
        self.kalgan = pygame.transform.smoothscale_by(pygame.image.load('images/fun/kalgan_head.png'), 0.3).convert_alpha()
        self.x = screen.get_width()
        self.y = screen.get_height() // 2 - self.img.get_height()
        self.vel_x = -5
        self.vel_y = 0
        self.laser_x = self.x + 570
        self.laser_vel_x = -15
        self.delta = 0.0

    def animate(self):
        if self.anim_step == 1:
            super().animate()

            self.screen.blit(self.kalgan, (self.x + 185, self.y - 25))
            self.screen.blit(self.img, (self.x + 500, self.y))
            self.screen.blit(self.ryder, (self.x + 685, self.y - 25))

            pygame.draw.rect(self.screen, (60, 160, 220), (self.laser_x, self.y + 120, 50, 5))
            self.laser_x += self.laser_vel_x

            self.delta += clock.tick(triviavox.FPS) / 1000
            if self.delta > 2.5:
                self.delta = 0
                self.laser_x = self.x + 570

            if self.x < -900:
                print("Done")
                self.anim_step = 0
