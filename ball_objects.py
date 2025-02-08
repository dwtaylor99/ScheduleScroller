import math

import pygame

from ball_constants import DRAG_CALC, AG_MULT_GRAV, FPS_FRACTION
from colors import YELLOW, WHITE, BLACK
from fonts import FONT_LG, FONT_MD
from util_text import drop_shadow


class Bot:
    def __init__(self, name, color):
        self.name: str = name
        self.color = color


class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.e = -0.7  # has no units
        self.mass = 10.0
        self.vel_x = 1.0  # m/s
        self.vel_y = 1.0  # m/s
        self.area = (math.pi * radius * radius) / 10000  # m^2
        self.username = ""
        self.hit = False
        self.place = 0
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.x + self.radius,
                                self.y + self.radius)

    def draw(self, scrn, camera_y):
        new_y = self.y - camera_y
        self.rect = pygame.draw.circle(scrn, self.color, (self.x, new_y), self.radius)
        pygame.draw.circle(scrn, WHITE, (self.x, new_y), self.radius, 2)
        tt = FONT_MD.render(self.username, True, self.color)
        drop_shadow(scrn, FONT_MD, self.username, self.color, self.x - tt.get_width() // 2, self.y - (self.radius * 3) - camera_y)

    def update(self):
        fx = DRAG_CALC * self.area * self.vel_x * self.vel_x * (self.vel_x / abs(self.vel_x))
        fy = DRAG_CALC * self.area * self.vel_y * self.vel_y * (self.vel_y / abs(self.vel_y))

        fx = 0 if math.isnan(fx) else fx
        fy = 0 if math.isnan(fy) else fy

        # Calculating the accleration of the ball, F = ma or a = F / m
        ax = fx / self.mass
        ay = AG_MULT_GRAV + (fy / self.mass)

        # Calculating the ball velocity
        self.vel_x += ax * FPS_FRACTION
        self.vel_y += ay * FPS_FRACTION

        # Calculating the position of the ball
        self.x += self.vel_x * FPS_FRACTION / 4
        self.y += self.vel_y * FPS_FRACTION / 4


class Bumper(Ball):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)

    def circle_a(self, scrn, color, camera_y):
        glow_dist = 10
        glow_dist_half = glow_dist // 2

        surf = pygame.Surface((self.radius * 2 + glow_dist, self.radius * 2 + glow_dist))
        surf.set_alpha(64)
        surf.set_colorkey((0, 0, 0))

        # glow
        pygame.draw.circle(surf, color, (self.radius - glow_dist_half, self.radius - glow_dist_half), self.radius + glow_dist_half, 5)
        scrn.blit(surf, (self.x - self.radius, self.y - self.radius - camera_y))

        new_y = self.y - camera_y
        white = (255, 242, 255)
        pink1 = (249, 182, 252)
        pink2 = (221, 37, 199)
        pygame.draw.circle(scrn, pink2, (self.x, new_y), self.radius - 5, 1)
        pygame.draw.circle(scrn, pink1, (self.x, new_y), self.radius - 4, 1)
        pygame.draw.circle(scrn, white, (self.x, new_y), self.radius - 2, 2)
        pygame.draw.circle(scrn, pink1, (self.x, new_y), self.radius - 1, 1)
        pygame.draw.circle(scrn, pink2, (self.x, new_y), self.radius, 1)

    def draw(self, scrn, camera_y):
        new_y = self.y - camera_y
        white = (255, 242, 255)
        pink1 = (249, 182, 252)
        pink2 = (221, 37, 199)
        pink3 = (201, 20, 180)

        pygame.draw.circle(scrn, pink3, (self.x, new_y), self.radius)  # background circle (filled)
        pygame.draw.circle(scrn, pink2, (self.x, new_y), self.radius - 2, 2)
        pygame.draw.circle(scrn, pink1, (self.x, new_y), self.radius - 1, 2)
        pygame.draw.circle(scrn, white, (self.x, new_y), self.radius, 2)
        pygame.draw.circle(scrn, pink1, (self.x, new_y), self.radius + 1, 2)
        pygame.draw.circle(scrn, pink2, (self.x, new_y), self.radius + 2, 2)

    def move(self):
        pass


class MovingBumper(Bumper):
    def __init__(self, x, y, radius, color, stop_pos):
        super().__init__(x, y, radius, color)
        self.start_pos = (self.x, self.y)
        self.stop_pos = stop_pos
        self.vel_x = 0.2
        self.vel_y = 0

    def move(self):
        self.x += self.vel_x
        self.y += self.vel_y

        x1 = self.start_pos[0]
        y1 = self.start_pos[1]
        x2 = self.stop_pos[0]
        y2 = self.stop_pos[1]
        if self.x < x1 or self.x > x2:
            self.vel_x = -self.vel_x
        if self.y < y1 or self.y > y2:
            self.vel_y = -self.vel_y


class Player:
    def __init__(self, username, color, total):
        self.username = username
        self.color = color
        self.total = total

    def add_points(self, points):
        self.total += points


if __name__ == '__main__':
    scr = pygame.display.set_mode((1920 // 2, 1080 // 2))
    clk = pygame.time.Clock()
    is_running = True

    while is_running:
        scr.fill(BLACK)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

    pygame.quit()
