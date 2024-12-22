import pygame


class ElSanto:
    img = None
    x = 0
    y = 0
    velocity = -0.7

    def __init__(self):
        self.img = pygame.image.load('images/fun/el_santo.png').convert_alpha()
        self.x = -(self.img.get_width()) - 10
        self.y = 660
