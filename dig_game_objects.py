import random
from enum import Enum

import pygame

from dig_game_tiles import Tile, Tiles

STANDING = ["🧍‍♂️", "🧍🏻‍♂️", "🧍🏼‍♂️", "🧍🏽‍♂️", "🧍🏾‍♂️", "🧍🏿‍♂️", "🧍‍♀️", "🧍🏻‍♀️", "🧍🏼‍♀️", "🧍🏽‍♀️", "🧍🏾‍♀️", "🧍🏿‍♀️"]
WALKING = ["🚶‍♂️", "🚶🏻‍♂️", "🚶🏼‍♂️", "🚶🏽‍♂️", "🚶🏾‍♂️", "🚶🏿‍♂️", "🚶‍♀️", "🚶🏻‍♀️", "🚶🏼‍♀️", "🚶🏽‍♀️", "🚶🏾‍♀️", "🚶🏿‍♀️"]
RUNNING = ["🏃‍♂️", "🏃🏻‍♂️", "🏃🏼‍♂️", "🏃🏽‍♂️", "🏃🏾‍♂️", "🏃🏿‍♂️", "🏃‍♀️", "🏃🏻‍♀️", "🏃🏼‍♀️", "🏃🏽‍♀️", "🏃🏾‍♀️", "🏃🏿‍♀️"]
# BIKING = ["🚴‍♂️", "🚴🏻‍♂️", "🚴🏼‍♂️", "🚴🏽‍♂️", "🚴🏾‍♂️", "🚴🏿‍♂️", "🚴‍♀️", "🚴🏻‍♀️", "🚴🏼‍♀️", "🚴🏽‍♀️", "🚴🏾‍♀️", "🚴🏿‍♀️"]
# HOUSES = ["🏚️", "🏠", "🏡", "🏛️"]

PLAYER_W = 14
PLAYER_H = 36


class Facing(Enum):
    LEFT = -1
    RIGHT = 1


class Player:
    # position and movement
    x = 0.0
    y = 0.0
    emoji_index = random.randrange(len(WALKING))
    facing = Facing.RIGHT
    vel_x = 0.0
    vel_y = 0.0
    on_ground = True
    ticks = 0

    # stats
    view_dist = 100
    house_index = 0
    inventory: [Tile] = []
    inv_dict = {}
    inv_selected = 0
    torches = []

    def add_inv(self, tile: Tiles):
        if tile in self.inv_dict.keys():
            self.inv_dict[tile] += 1
        else:
            self.inv_dict[tile] = 1

    def remove_inv(self, tile: Tiles):
        if tile in self.inv_dict.keys():
            self.inv_dict[tile] -= 1
            if self.inv_dict[tile] == 0:
                del self.inv_dict[tile]

    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + 6, PLAYER_W, PLAYER_H)


# Torches
TORCH_DIST = 100  # Default distance to light up (radius of circle)
TORCH_SHEET = pygame.image.load("images/game/torch_sheet.png")
TORCH_SCALE = 0.05
TORCH_X = 64
TORCH_Y = 115
TORCH_W = 260
TORCH_H = 520
TORCH_W_SCALED = TORCH_W * TORCH_SCALE
TORCH_H_SCALED = TORCH_H * TORCH_SCALE

TORCH_ANIM = []
for i in range(7):
    TORCH_SHEET.set_clip((TORCH_X + (TORCH_W * i), TORCH_Y, TORCH_W, TORCH_H))
    TORCH_ANIM.append(pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha())
