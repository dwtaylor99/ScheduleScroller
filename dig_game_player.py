import random
from enum import Enum

import pygame

from dig_game_tiles import Tile

STANDING = ["🧍‍♂️", "🧍🏻‍♂️", "🧍🏼‍♂️", "🧍🏽‍♂️", "🧍🏾‍♂️", "🧍🏿‍♂️", "🧍‍♀️", "🧍🏻‍♀️", "🧍🏼‍♀️", "🧍🏽‍♀️", "🧍🏾‍♀️", "🧍🏿‍♀️"]
WALKING = ["🚶‍♂️", "🚶🏻‍♂️", "🚶🏼‍♂️", "🚶🏽‍♂️", "🚶🏾‍♂️", "🚶🏿‍♂️", "🚶‍♀️", "🚶🏻‍♀️", "🚶🏼‍♀️", "🚶🏽‍♀️", "🚶🏾‍♀️", "🚶🏿‍♀️"]
RUNNING = ["🏃‍♂️", "🏃🏻‍♂️", "🏃🏼‍♂️", "🏃🏽‍♂️", "🏃🏾‍♂️", "🏃🏿‍♂️", "🏃‍♀️", "🏃🏻‍♀️", "🏃🏼‍♀️", "🏃🏽‍♀️", "🏃🏾‍♀️", "🏃🏿‍♀️"]
# BIKING = ["🚴‍♂️", "🚴🏻‍♂️", "🚴🏼‍♂️", "🚴🏽‍♂️", "🚴🏾‍♂️", "🚴🏿‍♂️", "🚴‍♀️", "🚴🏻‍♀️", "🚴🏼‍♀️", "🚴🏽‍♀️", "🚴🏾‍♀️", "🚴🏿‍♀️"]
HOUSES = ["🏚️", "🏠", "🏡", "🏛️"]

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
    jumping = False
    ticks = 0

    # stats
    view_dist = 100
    house_index = 0
    inventory: [Tile] = []
    inv_dict = {}
    inv_selected = 0
    torches = []  # [pygame.Rect(200, 500, 100, 100)]

    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + 6, PLAYER_W, PLAYER_H)
