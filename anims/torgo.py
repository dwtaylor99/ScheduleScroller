import pygame

from funbase import FunBase

FPS = 60
clock = pygame.time.Clock()
delta = 0


class Torgo(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.image.load('images/fun/torgo01.png').convert_alpha()
        self.img_loop = [
            pygame.image.load('images/fun/torgo01.png').convert_alpha(),
            pygame.image.load('images/fun/torgo02.png').convert_alpha(),
            pygame.image.load('images/fun/torgo03.png').convert_alpha(),
            pygame.image.load('images/fun/torgo04.png').convert_alpha(),
            pygame.image.load('images/fun/torgo03.png').convert_alpha(),
            pygame.image.load('images/fun/torgo02.png').convert_alpha()
        ]
        self.x = screen.get_width()
        self.y = screen.get_height() // 2 - self.img.get_height()
        self.vel_x = -0.6
        self.vel_y = 0
        self.img_index = 0

    def animate(self):
        global delta

        if self.anim_step == 1:
            self.img = self.img_loop[self.img_index]
            super().animate()

            delta += clock.tick(FPS)
            if delta >= 240:
                self.img_index = (self.img_index + 1) % len(self.img_loop)
                delta = 0

            if self.x < -100:
                self.anim_step = 0
