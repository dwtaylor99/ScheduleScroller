from enum import Enum

import pygame

from dig_game_tiles import Tile, Tiles

GIRL_SCALE = 0.7
GIRL_W = 75
GIRL_H = 60
GIRL_SPRITE_SHEET1 = pygame.image.load("images/game/tiles/girl_sheet_1.png").convert_alpha()
GIRL_SPRITE_SHEET2 = pygame.image.load("images/game/tiles/girl_sheet_2.png").convert_alpha()

GIRL_IDLE_ANIM = []
GIRL_JUMP_ANIM = []
for i in range(4):
    GIRL_SPRITE_SHEET2.set_clip((i * GIRL_W + 174, 160, GIRL_W, GIRL_H))
    GIRL_IDLE_ANIM.append(pygame.transform.smoothscale_by(GIRL_SPRITE_SHEET2.subsurface(GIRL_SPRITE_SHEET2.get_clip()), GIRL_SCALE).convert_alpha())

    GIRL_SPRITE_SHEET2.set_clip((i * GIRL_W + 174, 230, GIRL_W, GIRL_H))
    GIRL_JUMP_ANIM.append(pygame.transform.smoothscale_by(GIRL_SPRITE_SHEET2.subsurface(GIRL_SPRITE_SHEET2.get_clip()), GIRL_SCALE).convert_alpha())

GIRL_RUN_ANIM = []
for i in range(6):
    GIRL_SPRITE_SHEET2.set_clip((i * GIRL_W + 174, 385, GIRL_W, GIRL_H))
    GIRL_RUN_ANIM.append(pygame.transform.smoothscale_by(GIRL_SPRITE_SHEET2.subsurface(GIRL_SPRITE_SHEET2.get_clip()), GIRL_SCALE).convert_alpha())

GIRL_ATTACK_ANIM = []
for i in range(7):
    GIRL_SPRITE_SHEET1.set_clip((i * GIRL_W + 174, 160, GIRL_W, GIRL_H))
    GIRL_ATTACK_ANIM.append(pygame.transform.smoothscale_by(GIRL_SPRITE_SHEET1.subsurface(GIRL_SPRITE_SHEET1.get_clip()), GIRL_SCALE).convert_alpha())

GIRL_IDLE_ANIM_DELAY = 200
GIRL_JUMP_ANIM_DELAY = 200
GIRL_RUN_ANIM_DELAY = 100
GIRL_ATTACK_ANIM_DELAY = 100

PLAYER_W = 14
PLAYER_H = 36
PLAYER_W2 = PLAYER_W // 2
PLAYER_H2 = PLAYER_H // 2


class Facing(Enum):
    LEFT = -1
    RIGHT = 1


class Player:
    # position and movement
    x = 42 * 14
    y = 160.0  # start on Tile 5 which allows player a little build height.
    # emoji_index = random.randrange(len(WALKING))
    facing = Facing.RIGHT
    vel_x = 0.0
    vel_y = 0.0
    on_ground = True
    ticks = 0
    anim_step = 0
    anim_ticks = 0

    # stats
    view_dist = 100
    house_index = 0
    inventory: [Tile] = []
    inv_dict = {}
    inv_selected = 0
    torches = []
    tool_level = 1
    tool_charge = 100

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
        return pygame.Rect(self.x, self.y + 6, PLAYER_W, PLAYER_H)


# Torches
TORCH_DIST = 100  # Default distance to light up (radius of circle)
TORCH_ANIM_DELAY = 100
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
