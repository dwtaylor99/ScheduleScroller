import random

import pygame


class VampireWoman:
    img = None
    x = 0
    y = 0
    velocity = -0.5

    def __init__(self):
        self.img = pygame.image.load('images/fun/santo_vs_vampire_women.png').convert_alpha()
        self.x = random.randrange(100, 1800)
        self.y = 539
