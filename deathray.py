import pygame
from pygame import Color, Surface


class DeathRay:
    RAY_COLOR = Color(200, 0, 200, 20)

    screen = None
    img = None
    hole_img = None
    x = 0
    y = 0
    velocity = -1

    ticks = 0
    anim_step = 1  # track the steps of the animation, step 0 means no animation is running

    height_half = 0

    def __init__(self, screen: Surface):
        self.screen = screen
        self.height_half = screen.get_height() / 2
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/deathray.png').convert_alpha(), 1.2)
        self.x = 300
        self.y = 540
        self.hole_img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/hole_sm.png').convert_alpha(), 1.0)

    def animate(self):
        offset = 52

        # Step 0: Animation is off - do nothing!

        # Step 1: Raise the Death Ray
        if self.anim_step == 1:
            self.screen.blit(self.img, (self.x, self.y))
            if self.y >= self.height_half - self.img.get_height():
                self.y += self.velocity
            else:
                self.anim_step += 1  # move the next step of animation

        # Step 2: Fire the Death Ray
        if self.anim_step == 2:
            self.screen.blit(self.img, (self.x, self.y))
            if self.ticks % 3 == 0:
                for i in range(9):
                    pygame.draw.aaline(self.screen, self.RAY_COLOR,
                                       (self.x + self.img.get_width() - 6, self.y + i + offset),
                                       (self.x + self.img.get_width() + 650, self.y + i + (offset - 28)))
            if self.ticks > 200:
                self.anim_step += 1

        # Step 3: Explosion and hole
        if self.anim_step == 3:
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.hole_img, (1133, 367))
            if self.ticks > 360:
                self.anim_step += 1

        # Step 4: Lower the Death Ray
        if self.anim_step == 4:
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.hole_img, (1133, 367))
            if self.y <= self.height_half:
                self.y += -self.velocity
            else:
                self.anim_step += 1  # move the next step of animation

        # Step 5: Fade out the hole
        if self.anim_step == 5:
            self.hole_img.set_alpha(self.hole_img.get_alpha() - 2)
            self.screen.blit(self.hole_img, (1133, 367))
            if self.hole_img.get_alpha() == 0:
                self.anim_step = 0  # Stop the animation

        self.ticks += 1
        if self.ticks >= 60000:
            self.ticks = 0
