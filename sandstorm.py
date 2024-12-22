import random

import pygame


class SandStorm:
    img = None
    x = 0
    y = 0
    velocity = 3

    def __init__(self):
        scale = random.randrange(1, 10)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/sand_storm.png').convert_alpha(), .3 * scale)
        self.x = -self.img.get_width() - random.randrange(50, 250)
        self.y = random.randrange(30, 500)
        self.velocity = random.randrange(4, 6)
