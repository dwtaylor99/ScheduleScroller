import pygame
from pygame import Color, Surface


class DeathRayCrow:
    RAY_COLOR = Color(200, 0, 200, 20)

    screen = None
    img = None
    img2 = None
    x = 0
    y = 0
    velocity = -1

    ticks = 0
    anim_step = 1  # track the steps of the animation, step 0 means no animation is running

    height_half = 0

    def __init__(self, screen: Surface):
        self.screen = screen
        self.height_half = screen.get_height() / 2
        self.img = pygame.transform.smoothscale_by(pygame.image.load('images/fun/deathray.png'), 1.2).convert_alpha()
        self.x = 300
        self.y = 540
        self.img2 = pygame.transform.smoothscale_by(pygame.transform.flip(pygame.image.load('images/fun/crow.png'), True, False), 0.2).convert_alpha()

        flames = pygame.image.load('images/fun/flames.png').convert_alpha()

        self.flame_alpha = 255
        self.flame_index = 0
        self.flame_loop = []
        fx = 22
        for i in range(10):
            flames.set_clip((fx, 48, 79, 172))
            self.flame_loop.append(flames.subsurface(flames.get_clip()).convert_alpha())
            fx += 87

        fx = 22
        for i in range(10):
            flames.set_clip((fx, 278, 79, 172))
            self.flame_loop.append(flames.subsurface(flames.get_clip()).convert_alpha())
            fx += 87

    def animate(self):
        offset = 52

        # Step 0: Animation is off - do nothing!

        # Step 1: Raise the Death Ray
        if self.anim_step == 1:
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img2, (1133, self.y - 50))
            if self.y >= self.height_half - self.img.get_height():
                self.y += self.velocity
            else:
                self.anim_step += 1  # move the next step of animation

        # Step 2: Fire the Death Ray
        if self.anim_step == 2:
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img2, (1133, 357))
            if self.ticks % 3 == 0:
                for i in range(9):
                    pygame.draw.aaline(self.screen, self.RAY_COLOR,
                                       (self.x + self.img.get_width() - 6, self.y + i + offset),
                                       (self.x + self.img.get_width() + 650, self.y + i + (offset - 28)))
            if self.ticks > 200:
                self.anim_step += 1

        # Step 3: Explosion and flames
        if self.anim_step == 3:
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img2, (1133, 357))

            self.screen.blit(self.flame_loop[int(self.flame_index)], (1190, 280))
            self.flame_index = (self.flame_index + 0.5) % len(self.flame_loop)

            if self.ticks > 360:
                self.anim_step += 1

        # Step 4: Lower the Death Ray
        if self.anim_step == 4:
            self.screen.blit(self.img, (self.x, self.y))
            self.screen.blit(self.img2, (1133, 357))

            self.screen.blit(self.flame_loop[int(self.flame_index)], (1190, 280))
            self.flame_index = (self.flame_index + 0.5) % len(self.flame_loop)

            if self.y <= self.height_half:
                self.y += -self.velocity
            else:
                self.anim_step += 1  # move the next step of animation

        # Step 5: Fade out crow
        if self.anim_step == 5:
            self.img2.set_alpha(self.img2.get_alpha() - 2)
            self.screen.blit(self.img2, (1133, 357))

            self.flame_loop[int(self.flame_index)].set_alpha(self.flame_alpha)
            self.screen.blit(self.flame_loop[int(self.flame_index)], (1190, 280))
            self.flame_index = (self.flame_index + 0.5) % len(self.flame_loop)
            self.flame_alpha -= 2

            if self.img2.get_alpha() <= 0:
                self.anim_step = 0  # Stop the animation

        self.ticks += 1
        if self.ticks >= 60000:
            self.ticks = 0
