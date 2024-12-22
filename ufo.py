import random

import pygame


class Ufo:
    img = None
    x = 0
    y = 0
    velocity = 4

    def __init__(self):
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/ufo.png').convert_alpha(), 0.5)
        self.x = -(self.img.get_width()) - 10
        self.y = random.randrange(30, 500)
