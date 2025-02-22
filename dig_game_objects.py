from enum import Enum

import pygame

from dig_game_tiles import Tile, Tiles, Diamond

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
GIRL_RUN_ANIM_DELAY = 50
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
    beam_ticks = 0
    anim_step = 0
    anim_ticks = 0

    # stats
    # { Tiles.X: int }
    inv_dict = {
        Tiles.STONE: 10
    }
    view_dist = 100  # when underground
    house_index = 0
    inv_selected = 0
    torches = []

    tool_dist = 2  # tiles
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
TORCH_SHEET = pygame.image.load("images/game/torch_sheet.png").convert_alpha()
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


# Enemy 1
IMG_OGRE_SHEET = pygame.image.load("images/game/tiles/enemy_01.png").convert_alpha()
OGRE_W = 83
OGRE_H = 75
OGRE_IDLE_ANIM = []
OGRE_WALK_ANIM = []
OGRE_ATTACK_ANIM = []
OGRE_HURT_ANIM = []
OGRE_DEATH_ANIM = []
for i in range(4):
    if i < 4:
        IMG_OGRE_SHEET.set_clip((i * OGRE_W + 170, 12, OGRE_W, OGRE_H))
        OGRE_IDLE_ANIM.append(pygame.transform.smoothscale_by(IMG_OGRE_SHEET.subsurface(IMG_OGRE_SHEET.get_clip()), 0.7).convert_alpha())

        IMG_OGRE_SHEET.set_clip((i * OGRE_W + 170, 194, OGRE_W, OGRE_H))
        OGRE_ATTACK_ANIM.append(pygame.transform.smoothscale_by(IMG_OGRE_SHEET.subsurface(IMG_OGRE_SHEET.get_clip()), 0.7).convert_alpha())

        IMG_OGRE_SHEET.set_clip((i * OGRE_W + 170, 285, OGRE_W, OGRE_H))
        OGRE_HURT_ANIM.append(pygame.transform.smoothscale_by(IMG_OGRE_SHEET.subsurface(IMG_OGRE_SHEET.get_clip()), 0.7).convert_alpha())

        IMG_OGRE_SHEET.set_clip((i * OGRE_W + 170, 376, OGRE_W, OGRE_H))
        OGRE_DEATH_ANIM.append(pygame.transform.smoothscale_by(IMG_OGRE_SHEET.subsurface(IMG_OGRE_SHEET.get_clip()), 0.7).convert_alpha())

    IMG_OGRE_SHEET.set_clip((i * OGRE_W + 170, 104, OGRE_W, OGRE_H))
    OGRE_WALK_ANIM.append(pygame.transform.smoothscale_by(IMG_OGRE_SHEET.subsurface(IMG_OGRE_SHEET.get_clip()), 0.7).convert_alpha())


class EnemyAction(Enum):
    IDLE = 0
    WALK = 1
    ATTACK = 2
    HURT = 3
    DEATH = 4


class Enemy:
    x: float = 0.0
    y: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    facing: Facing = Facing.LEFT
    action: EnemyAction = EnemyAction.IDLE
    health: int = 1
    damage: int = 1
    ticks: int = 0
    anim_step: int = 0
    idle_anim = []
    walk_anim = []
    attack_anim = []
    hurt_anim = []
    death_anim = []

    def get_anim(self):
        return self.idle_anim

    def get_delay(self):
        if self.action == EnemyAction.IDLE:
            return 0
        return 0


class Ogre(Enemy):
    offset_x: float = -12.0
    offset_y: float = -12.0
    heath = 10
    damage = 2
    idle_anim = OGRE_IDLE_ANIM
    walk_anim = OGRE_WALK_ANIM
    attack_anim = OGRE_ATTACK_ANIM
    hurt_anim = OGRE_HURT_ANIM
    death_anim = OGRE_DEATH_ANIM

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_anim(self):
        if self.action == EnemyAction.IDLE:
            return self.idle_anim
        elif self.action == EnemyAction.WALK:
            return self.walk_anim
        elif self.action == EnemyAction.ATTACK:
            return self.attack_anim
        elif self.action == EnemyAction.HURT:
            return self.hurt_anim
        elif self.action == EnemyAction.DEATH:
            return self.death_anim
        return []

    def get_delay(self):
        if self.action == EnemyAction.IDLE:
            return 150
        elif self.action == EnemyAction.WALK:
            return 200
        elif self.action == EnemyAction.ATTACK:
            return 100
        elif self.action == EnemyAction.HURT:
            return 150
        elif self.action == EnemyAction.DEATH:
            return 150
        return 0
