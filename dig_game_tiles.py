from enum import Enum

import pygame

from colors import WHITE
from dig_game_drops import DiamondDrop, GoldDrop, SilverDrop, IronDrop, Drops, DirtDrop, StoneDrop, ClayDrop, \
    CopperDrop, RewardUrnDrop, CoalDrop

FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)

TILE_W = TILE_H = 42
TILE_SCALE = 0.3

IMG_DIRT = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/brown_dirt.png"), TILE_SCALE).convert_alpha()
IMG_STONE = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/stone_block.png"), TILE_SCALE).convert_alpha()
IMG_CLAY = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/clay_block.png"), TILE_SCALE).convert_alpha()
IMG_COAL = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/coal_block.png"), TILE_SCALE).convert_alpha()
IMG_COPPER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/copper_block.png"), TILE_SCALE).convert_alpha()
IMG_IRON = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/iron_block.png"), TILE_SCALE).convert_alpha()
IMG_SILVER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/silver_block.png"), TILE_SCALE).convert_alpha()
IMG_GOLD = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/gold_block.png"), TILE_SCALE).convert_alpha()
IMG_DIAMOND = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/diamond_block.png"), TILE_SCALE).convert_alpha()

IMG_BLUE_BRICKS = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/blue_wall.png"), TILE_SCALE).convert_alpha()
IMG_RED_BRICKS = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/red_wall.png"), TILE_SCALE).convert_alpha()
IMG_GRAY_BRICKS = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/bricks.png"), TILE_SCALE).convert_alpha()

IMG_URN = FONT_EMOJI_MD.render("🏺", True, WHITE)
IMG_TORCH = FONT_EMOJI_MD.render("🔦", True, WHITE)


class Tile:
    img = None
    drop = Drops.NONE
    dig_level = 0
    dig_ticks = 100


class Air(Tile):
    img = None


class Dirt(Tile):
    img = IMG_DIRT
    drop = DirtDrop()
    dig_ticks = 500


class Stone(Tile):
    img = IMG_STONE
    drop = StoneDrop()
    dig_ticks = 1000


class Clay(Tile):
    img = IMG_CLAY
    drop = ClayDrop()
    dig_ticks = 1500


class Coal(Tile):
    img = IMG_COAL
    drop = CoalDrop()
    dig_level = 1
    dig_ticks = 1500


class Copper(Tile):
    img = IMG_COPPER
    drop = CopperDrop()
    dig_level = 1
    dig_ticks = 2000


class Iron(Tile):
    img = IMG_IRON
    drop = IronDrop()
    dig_level = 2
    dig_ticks = 2500


class Silver(Tile):
    img = IMG_SILVER
    drop = SilverDrop()
    dig_level = 2
    dig_ticks = 2500


class Gold(Tile):
    img = IMG_GOLD
    drop = GoldDrop()
    dig_level = 2
    dig_ticks = 3000


class Diamond(Tile):
    img = IMG_DIAMOND
    drop = DiamondDrop()
    dig_level = 2
    dig_ticks = 5000


class RewardUrn(Tile):
    img = IMG_URN
    drop = RewardUrnDrop()
    dig_level = 1
    dig_ticks = 1000


class Tiles(Enum):
    AIR = Air()
    DIRT = Dirt()
    STONE = Stone()
    CLAY = Clay()
    COAL = Coal()
    COPPER = Copper()
    IRON = Iron()
    SILVER = Silver()
    GOLD = Gold()
    DIAMOND = Diamond()
    REWARD_URN = RewardUrn()
