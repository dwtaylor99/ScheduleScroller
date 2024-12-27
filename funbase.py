from pygame import Surface


class FunBase:
    screen = None
    img = None
    x = 0
    y = 0
    vel_x = 0
    vel_y = 0
    anim_step = 1

    def __init__(self, screen: Surface):
        self.screen = screen

    def animate(self):
        if self.anim_step >= 1:
            self.screen.blit(self.img, (self.x, self.y))
            self.x += self.vel_x
            self.y += self.vel_y
