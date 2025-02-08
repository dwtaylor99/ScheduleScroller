import random
from pickle import REDUCE

import pygame

from colors import DK_GRAY, WHITE, RED
from funbase import FunBase

BALL_RADIUS = 8
RADIUS = 28
XOFFSET = 73
YOFFSET = 40
XOFFSET_TOP = 58
YOFFSET_TOP = 6


class ServoLottery(FunBase):
    def __init__(self, screen):
        super().__init__(screen)
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/mood_servo.png'), 0.25).convert_alpha()
        self.img_top = pygame.transform.smoothscale_by(pygame.image.load('images/fun/mood_servo_top.png'), 0.25).convert_alpha()
        self.x = random.randrange(screen.get_width() // 2 + 100, screen.get_width() - 600)
        self.y = 400
        self.vel_x = 0
        self.vel_y = -2
        self.ball_count = 0
        self.ball_x = 0
        self.ball_y = 0
        self.ball_vel_x = 0
        self.ball_vel_y = -8
        self.balls = []

    def animate(self):
        if self.anim_step == 1:
            # Raise Servo
            pygame.draw.circle(self.screen, DK_GRAY, (self.x + XOFFSET, self.y + YOFFSET), RADIUS, 2)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET + 12, self.y + YOFFSET - 12), 5)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET - 12, self.y + YOFFSET + 12), 3)
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img_top, (self.x + XOFFSET_TOP, self.y + YOFFSET_TOP))
            self.x += self.vel_x
            self.y += self.vel_y

            if self.y <= 270:
                self.vel_y = 0
                self.ball_x = self.x + 75
                self.ball_y = self.y + 50
                self.anim_step += 1

        elif self.anim_step == 2:
            pygame.draw.circle(self.screen, DK_GRAY, (self.x + XOFFSET, self.y + YOFFSET), RADIUS, 2)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET + 12, self.y + YOFFSET - 12), 5)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET - 12, self.y + YOFFSET + 12), 3)
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img_top, (self.x + XOFFSET_TOP, self.y + YOFFSET_TOP))

            ball_color = WHITE
            if self.ball_count == 7:
                ball_color = (192, 0, 0)
            pygame.draw.circle(self.screen, ball_color, (self.ball_x, self.ball_y), BALL_RADIUS)

            self.ball_x += self.ball_vel_x
            self.ball_y += self.ball_vel_y

            if self.ball_y <= -20 and self.ball_count < 8:
                self.ball_count += 1
                self.ball_x = self.x + 75
                self.ball_y = self.y + 50

            if self.ball_count == 8:
                for _ in range(100):
                    self.balls.append({'x': random.randrange(self.x - 500, self.x + 500), 'y': random.randrange(-100, -10)})

                self.ball_vel_y = 12
                self.vel_y = 2
                self.anim_step += 1

        elif self.anim_step == 3:
            for ball in self.balls:
                pygame.draw.circle(self.screen, WHITE, (ball['x'], ball['y']), BALL_RADIUS)
                ball['y'] += self.ball_vel_y

            # Lower Servo
            pygame.draw.circle(self.screen, DK_GRAY, (self.x + XOFFSET, self.y + YOFFSET), 28, 2)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET + 12, self.y + YOFFSET - 12), 5)
            pygame.draw.circle(self.screen, WHITE, (self.x + XOFFSET - 12, self.y + YOFFSET + 12), 3)
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img_top, (self.x + XOFFSET_TOP, self.y + YOFFSET_TOP))
            self.x += self.vel_x
            self.y += self.vel_y

            if self.y >= self.screen.get_height() // 2:
                self.anim_step = 0
