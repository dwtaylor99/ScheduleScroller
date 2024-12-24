"""https://github.com/plemaster01/pygamePhysics"""

import pygame
from pygame import Surface

WIDTH = 1920
HEIGHT = 1080
wall_thickness = 10
gravity = 0.5
bounce_stop = 0.3


class Ball:
    def __init__(self, screen: Surface, x_pos, y_pos, radius, color, mass, retention, y_speed, x_speed, id, friction):
        self.screen = screen
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.color = color
        self.mass = mass
        self.retention = retention
        self.y_speed = y_speed
        self.x_speed = x_speed
        self.id = id
        self.circle: pygame.Rect = pygame.Rect(0, 0, 1, 1)
        self.coll_rect: pygame.Rect = pygame.Rect(0, 0, 1, 1)
        self.selected = False
        self.friction = friction

    def draw(self):
        self.circle = pygame.draw.circle(self.screen, self.color, (self.x_pos, self.y_pos), self.radius)
        self.coll_rect = pygame.Rect(self.x_pos - self.radius, self.y_pos - self.radius, self.radius * 2, self.radius * 2)

    def check_collisions(self, balls, x_push, y_push):
        if not self.selected:

            # Wall collisions
            if self.y_pos < HEIGHT - self.radius - (wall_thickness / 2):
                self.y_speed += gravity
            else:
                if self.y_speed > bounce_stop:
                    self.y_speed = self.y_speed * -1 * self.retention
                else:
                    if abs(self.y_speed) <= bounce_stop:
                        self.y_speed = 0
            if (self.x_pos < self.radius + (wall_thickness/2) and self.x_speed < 0) or \
                    (self.x_pos > WIDTH - self.radius - (wall_thickness/2) and self.x_speed > 0):
                self.x_speed *= -1 * self.retention
                if abs(self.x_speed) < bounce_stop:
                    self.x_speed = 0

            # Ball collisions
            for ball in balls:
                if self.id != ball.id:
                    collision = self.coll_rect.colliderect(ball.coll_rect)
                    if collision:
                        self.x_speed *= -self.retention
                        if abs(self.x_speed) < bounce_stop:
                            self.x_speed = 0
                        ball.x_speed = (self.x_speed / 2) * ball.retention
                        if abs(ball.x_speed) < bounce_stop:
                            ball.x_speed = 0

            if self.y_speed == 0 and self.x_speed != 0:
                if self.x_speed > 0:
                    self.x_speed -= self.friction
                elif self.x_speed < 0:
                    self.x_speed += self.friction
        else:
            self.x_speed = x_push
            self.y_speed = y_push
        return self.y_speed

    def update_pos(self, mouse):
        if not self.selected:
            self.y_pos += self.y_speed
            self.x_pos += self.x_speed
        else:
            self.x_pos = mouse[0]
            self.y_pos = mouse[1]

    def check_select(self, pos):
        self.selected = False
        if self.circle.collidepoint(pos):
            self.selected = True
        return self.selected
