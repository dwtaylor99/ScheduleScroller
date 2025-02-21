from enum import Enum

import pygame

from colors import WHITE
from dig_game_drops import Drops
from fonts import FONT_EMOJI_XL

FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)

TILE_W = TILE_H = 42
TILE_SCALE = 0.3

IMG_GRASS_DIRT = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/grass_dirt_block.png"), TILE_SCALE).convert_alpha()
IMG_DIRT = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/dirt_block.png"), TILE_SCALE).convert_alpha()
IMG_STONE = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/stone_block.png"), TILE_SCALE).convert_alpha()
IMG_CLAY = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/clay_block.png"), TILE_SCALE).convert_alpha()
IMG_COAL = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/coal_block.png"), TILE_SCALE).convert_alpha()
IMG_COPPER = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/copper_block.png"), TILE_SCALE).convert_alpha()
IMG_IRON = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/iron_block.png"), TILE_SCALE).convert_alpha()
IMG_SILVER = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/silver_block.png"), TILE_SCALE).convert_alpha()
IMG_GOLD = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/gold_block.png"), TILE_SCALE).convert_alpha()
IMG_DIAMOND = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/diamond_block.png"), TILE_SCALE).convert_alpha()

IMG_GREEN_VINES = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/green_wall.png"), TILE_SCALE).convert_alpha()
IMG_BLUE_BRICKS = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/blue_wall.png"), TILE_SCALE).convert_alpha()
IMG_RED_BRICKS = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/red_wall.png"), TILE_SCALE).convert_alpha()
IMG_GRAY_BRICKS = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/bricks.png"), TILE_SCALE).convert_alpha()

IMG_GRASS = pygame.image.load("images/game/tiles/grass.png").convert_alpha()
IMG_TREE_01 = pygame.image.load("images/game/tiles/tree_01.png").convert_alpha()
IMG_TREE_02 = pygame.image.load("images/game/tiles/tree_02.png").convert_alpha()
IMG_TREE_03 = pygame.image.load("images/game/tiles/tree_03.png").convert_alpha()
IMG_TREE_04 = pygame.image.load("images/game/tiles/tree_04.png").convert_alpha()

IMG_BUSH_01 = pygame.image.load("images/game/tiles/bush_01.png").convert_alpha()
IMG_BUSH_02 = pygame.image.load("images/game/tiles/bush_02.png").convert_alpha()
IMG_BUSH_03 = pygame.image.load("images/game/tiles/bush_03.png").convert_alpha()
IMG_BUSH_04 = pygame.image.load("images/game/tiles/bush_04.png").convert_alpha()

IMG_URN = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/amphora.png").convert_alpha(), 0.15)
IMG_CHALICE = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/golden_chalice.png").convert_alpha(), 0.15)

IMG_TORCH = FONT_EMOJI_MD.render("🔦", True, WHITE)
IMG_VOLTAGE = FONT_EMOJI_MD.render("⚡", True, WHITE)
IMG_BATTERY = FONT_EMOJI_MD.render("🔋", True, WHITE)
IMG_HOUSE_01 = FONT_EMOJI_XL.render("🏚️", True, WHITE)
IMG_HOUSE_02 = FONT_EMOJI_XL.render("🏠️", True, WHITE)
IMG_HOUSE_03 = FONT_EMOJI_XL.render("🏡", True, WHITE)
IMG_HOUSE_04 = FONT_EMOJI_XL.render("🏛️", True, WHITE)


class Tile:
    img = None
    img_offset_x = 0
    img_offset_y = 0
    is_solid = True
    drop = Drops.NONE
    dig_level = 1
    dig_ticks = 100


class Air(Tile):
    img = None
    is_solid = False
    dig_level = 0


class GrassDirt(Tile):
    img = IMG_GRASS_DIRT
    drop = Drops.DIRT
    dig_ticks = 500


class Dirt(Tile):
    img = IMG_DIRT
    drop = Drops.DIRT
    dig_ticks = 500


class Stone(Tile):
    img = IMG_STONE
    drop = Drops.STONE
    dig_ticks = 1000


class Clay(Tile):
    img = IMG_CLAY
    drop = Drops.CLAY
    dig_ticks = 1500


class Coal(Tile):
    img = IMG_COAL
    drop = Drops.COAL
    dig_ticks = 1500


class Copper(Tile):
    img = IMG_COPPER
    drop = Drops.COPPER
    dig_ticks = 2000


class Iron(Tile):
    img = IMG_IRON
    drop = Drops.IRON
    dig_level = 2
    dig_ticks = 2500


class Silver(Tile):
    img = IMG_SILVER
    drop = Drops.SILVER
    dig_level = 2
    dig_ticks = 2500


class Gold(Tile):
    img = IMG_GOLD
    drop = Drops.GOLD
    dig_level = 2
    dig_ticks = 3000


class Diamond(Tile):
    img = IMG_DIAMOND
    drop = Drops.DIAMOND
    dig_level = 2
    dig_ticks = 5000


class RewardUrn(Tile):
    img = IMG_URN
    img_offset_x = 3
    img_offset_y = 5
    is_solid = False
    drop = Drops.REWARD_URN
    dig_ticks = 1000


class RewardChalice(Tile):
    img = IMG_CHALICE
    img_offset_x = 5
    img_offset_y = 5
    is_solid = False
    drop = Drops.REWARD_CHALICE
    dig_ticks = 1000


class Tree01(Tile):
    img = IMG_TREE_01
    img_offset_x = -65
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.TREE_DROP
    dig_level = 1
    dig_ticks = 1000


class Tree02(Tile):
    img = IMG_TREE_02
    img_offset_x = -40
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.TREE_DROP
    dig_level = 1
    dig_ticks = 1000


class Tree03(Tile):
    img = IMG_TREE_03
    img_offset_x = -40
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.TREE_DROP
    dig_level = 1
    dig_ticks = 1000


class Tree04(Tile):
    img = IMG_TREE_04
    img_offset_x = -40
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.TREE_DROP
    dig_level = 1
    dig_ticks = 1000


class House1(Tile):
    img = IMG_HOUSE_01
    img_offset_x = -40
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.HOUSE_1
    dig_level = 1
    dig_ticks = 5000


class House2(Tile):
    img = IMG_HOUSE_02
    img_offset_x = -40
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.HOUSE_2
    dig_level = 1
    dig_ticks = 5000


class House3(Tile):
    img = IMG_HOUSE_03
    img_offset_x = -40
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.HOUSE_3
    dig_level = 1
    dig_ticks = 5000


class House4(Tile):
    img = IMG_HOUSE_04
    img_offset_x = -40
    img_offset_y = TILE_H - img.get_height()
    is_solid = False
    drop = Drops.HOUSE_4
    dig_level = 1
    dig_ticks = 5000


class Tiles(Enum):
    AIR = Air()
    GRASS_DIRT = GrassDirt()
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
    REWARD_CHALICE = RewardChalice()
    TREE_01 = Tree01()
    TREE_02 = Tree02()
    TREE_03 = Tree03()
    TREE_04 = Tree04()
    HOUSE_1 = House1()
    HOUSE_2 = House2()
    HOUSE_3 = House3()
    HOUSE_4 = House4()
