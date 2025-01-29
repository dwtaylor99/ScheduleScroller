import itertools
import random

import pygame

from funbase import FunBase

RADIUS = 28

XOFFSET = 73
YOFFSET = 40

XOFFSET_TOP = 58
YOFFSET_TOP = 6

GRAY = pygame.Color(160, 160, 160)
YELLOW = pygame.Color(210, 200, 0)
ORANGE = pygame.Color(210, 100, 0)
PURPLE = pygame.Color(100, 50, 230)
BLUE = pygame.Color(30, 135, 215)
WHITE = pygame.Color(192, 192, 192)

CHANGE_EVERY = 3
NUM_STEPS = CHANGE_EVERY * 60  # fps=60


class MoodServo(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/mood_servo.png'), 0.25).convert_alpha()
        self.img_top = pygame.transform.smoothscale_by(pygame.image.load('images/fun/mood_servo_top.png'), 0.25).convert_alpha()
        self.x = random.randrange(screen.get_width() // 2 + 100, screen.get_width() - 600)
        self.y = 400
        self.vel_x = 0
        self.vel_y = -2
        self.step = 1
        # Cycle colors: yellow (happy) -> orange (confident) -> purple (validation) -> blue (calm)
        self.colors = itertools.chain([GRAY, YELLOW, ORANGE, PURPLE, BLUE, GRAY])
        self.base_color = next(self.colors)
        self.next_color = next(self.colors)
        self.current_color = self.base_color

    def animate(self):
        if self.anim_step == 1:
            # Raise Servo
            pygame.draw.circle(self.screen, GRAY, (self.x + XOFFSET, self.y + YOFFSET), 28)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET + 12, self.y + YOFFSET - 12), 5)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET - 12, self.y + YOFFSET + 12), 3)
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img_top, (self.x + XOFFSET_TOP, self.y + YOFFSET_TOP))
            self.x += self.vel_x
            self.y += self.vel_y

            if self.y <= 270:
                self.vel_y = 0
                self.anim_step += 1

        elif self.anim_step == 2:
            self.step += 1
            if self.step < NUM_STEPS:
                self.current_color = [x + (((y - x) / NUM_STEPS) * self.step) for x, y in zip(pygame.color.Color(self.base_color), pygame.color.Color(self.next_color))]
            else:
                self.step = 1
                self.base_color = self.next_color
                try:
                    self.next_color = next(self.colors)
                except StopIteration:
                    self.vel_y = 2
                    self.anim_step += 1

            pygame.draw.circle(self.screen, self.current_color, (self.x + XOFFSET, self.y + YOFFSET), 28)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET + 12, self.y + YOFFSET - 12), 5)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET - 12, self.y + YOFFSET + 12), 3)
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img_top, (self.x + XOFFSET_TOP, self.y + YOFFSET_TOP))

        elif self.anim_step == 3:
            # Lower Servo
            pygame.draw.circle(self.screen, GRAY, (self.x + XOFFSET, self.y + YOFFSET), 28)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET + 12, self.y + YOFFSET - 12), 5)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET - 12, self.y + YOFFSET + 12), 3)
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img_top, (self.x + XOFFSET_TOP, self.y + YOFFSET_TOP))
            self.x += self.vel_x
            self.y += self.vel_y

            if self.y >= self.screen.get_height() // 2:
                self.anim_step = 0
