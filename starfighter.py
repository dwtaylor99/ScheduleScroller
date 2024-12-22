import random

import pygame


class Starfighter:
    img = None
    x = 0
    y = 0
    velocity = -6

    def __init__(self):
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/starfighter.png').convert_alpha(), 0.5)
        self.x = 1920 + self.img.get_width() + 10 + random.randrange(50, 250)
        self.y = random.randrange(30, 500)
