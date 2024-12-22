import random

import pygame


class Gamera:
    img = None
    x = 0
    y = 0
    velocity = 4

    def __init__(self):
        self.img = pygame.image.load('images/fun/gamera.png').convert_alpha()
        self.x = -(self.img.get_width()) - 10
        self.y = random.randrange(30, 500)
