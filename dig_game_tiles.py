from enum import Enum

import pygame

from colors import WHITE
from dig_game_drops import DiamondDrop, GoldDrop, SilverDrop, IronDrop, Drops, DirtDrop, StoneDrop, ClayDrop, \
    CopperDrop, RewardUrnDrop


FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)

TILE_W = TILE_H = 42
TILE_SCALE = 0.3

IMG_DIRT = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/brown_dirt.png"), TILE_SCALE).convert_alpha()
IMG_STONE = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/stone_block.png"), TILE_SCALE).convert_alpha()
IMG_CLAY = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/clay_block.png"), TILE_SCALE).convert_alpha()
IMG_COPPER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/copper_block.png"), TILE_SCALE).convert_alpha()
IMG_IRON = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/iron_block.png"), TILE_SCALE).convert_alpha()
IMG_SILVER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/silver_block.png"), TILE_SCALE).convert_alpha()
IMG_GOLD = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/gold_block.png"), TILE_SCALE).convert_alpha()
IMG_DIAMOND = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/diamond_block.png"), TILE_SCALE).convert_alpha()

IMG_URN = FONT_EMOJI_MD.render("🏺", True, WHITE)
IMG_TORCH = FONT_EMOJI_MD.render("🔦", True, WHITE)

# IMG_DIRT = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/brown_dirt.png"), TILE_SCALE).convert_alpha()
# IMG_STONE = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/gray_wall.png"), TILE_SCALE).convert_alpha()
# IMG_CLAY = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/red_wall.png"), TILE_SCALE).convert_alpha()
# IMG_COPPER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/yellow_wall.png"), TILE_SCALE).convert_alpha()
# IMG_IRON = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/blue_wall.png"), TILE_SCALE).convert_alpha()
# IMG_SILVER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/cobble.png"), TILE_SCALE).convert_alpha()
# IMG_GOLD = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/yellow_cobble.png"), TILE_SCALE).convert_alpha()
# IMG_DIAMOND = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/mixed.png"), TILE_SCALE).convert_alpha()


class Tile:
    img = None
    drop = Drops.NONE
    dig_level = 0


class Air(Tile):
    img = None


class Dirt(Tile):
    img = IMG_DIRT
    drop = DirtDrop()


class Stone(Tile):
    img = IMG_STONE
    drop = StoneDrop()


class Clay(Tile):
    img = IMG_CLAY
    drop = ClayDrop()


class Copper(Tile):
    img = IMG_COPPER
    drop = CopperDrop()
    dig_level = 1


class Iron(Tile):
    img = IMG_IRON
    drop = IronDrop()
    dig_level = 2


class Silver(Tile):
    img = IMG_SILVER
    drop = SilverDrop()
    dig_level = 2


class Gold(Tile):
    img = IMG_GOLD
    drop = GoldDrop()
    dig_level = 2


class Diamond(Tile):
    img = IMG_DIAMOND
    drop = DiamondDrop()
    dig_level = 2


class RewardUrn(Tile):
    img = IMG_URN
    drop = RewardUrnDrop()
    dig_level = 1


class Tiles(Enum):
    AIR = Air()
    DIRT = Dirt()
    STONE = Stone()
    CLAY = Clay()
    COPPER = Copper()
    IRON = Iron()
    SILVER = Silver()
    GOLD = Gold()
    DIAMOND = Diamond()
    REWARD_URN = RewardUrn()
