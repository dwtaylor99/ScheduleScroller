import pygame
from pygame import Color


class DeathRay:
    RAY_COLOR = Color(200, 0, 200, 20)

    img = None
    x = 0
    y = 0
    velocity = -1
    ticks = 0
    anim_step = 0  # track the steps of the animation

    def __init__(self):
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/deathray.png').convert_alpha(), 1.2)
        self.x = 300
        self.y = 540
