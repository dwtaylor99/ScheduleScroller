from enum import Enum

import pygame

from colors import WHITE

pygame.init()
screen = pygame.display.set_mode((1920 // 2, 1080))
FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)

IMG_DIRT_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/dirt_drop.png").convert_alpha(), 0.3)
IMG_STONE_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/stone_drop.png").convert_alpha(), 0.42)
IMG_CLAY_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/clay_drop.png").convert_alpha(), 0.42)
IMG_COAL_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/coal_drop.png").convert_alpha(), 0.15)
IMG_COPPER_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/copper_drop.png").convert_alpha(), 0.3)
IMG_IRON_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/iron_drop.png").convert_alpha(), 0.3)
IMG_SILVER_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/silver_drop.png").convert_alpha(), 0.3)
IMG_GOLD_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/gold_drop.png").convert_alpha(), 0.3)
IMG_DIAMOND_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/diamond_drop.png").convert_alpha(), 0.32)
IMG_LOG_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/log_drop.png").convert_alpha(), 0.42)
IMG_URN_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/amphora.png").convert_alpha(), 0.15)
IMG_CHALICE_DROP = pygame.transform.smoothscale_by(pygame.image.load("images/game/tiles/golden_chalice.png").convert_alpha(), 0.15)


class Drop:
    name = ""
    value = 0
    img = None


class NoneDrop(Drop):
    name = "None"


class DirtDrop(Drop):
    name = "Dirt"
    value = 1
    img = IMG_DIRT_DROP
    # img = FONT_EMOJI_MD.render("🟫", True, WHITE).convert_alpha()


class StoneDrop(Drop):
    name = "Stone"
    value = 1
    img = IMG_STONE_DROP
    # img = FONT_EMOJI_MD.render("⚪", True, WHITE).convert_alpha()


class ClayDrop(Drop):
    name = "Clay"
    value = 2
    img = IMG_CLAY_DROP
    # img = FONT_EMOJI_MD.render("🟤", True, WHITE).convert_alpha()


class CoalDrop(Drop):
    name = "Coal"
    value = 3
    img = IMG_COAL_DROP
    # img = FONT_EMOJI_MD.render("⚫", True, WHITE).convert_alpha()


class CopperDrop(Drop):
    name = "Copper"
    value = 5
    img = IMG_COPPER_DROP
    # img = FONT_EMOJI_MD.render("🔶", True, WHITE).convert_alpha()


class IronDrop(Drop):
    name = "Iron"
    value = 10
    img = IMG_IRON_DROP
    # img = FONT_EMOJI_MD.render("🔷", True, WHITE).convert_alpha()


class SilverDrop(Drop):
    name = "Silver"
    value = 15
    img = IMG_SILVER_DROP
    # img = FONT_EMOJI_MD.render("⬜", True, WHITE).convert_alpha()


class GoldDrop(Drop):
    name = "Gold"
    value = 25
    img = IMG_GOLD_DROP
    # img = FONT_EMOJI_MD.render("🟨", True, WHITE).convert_alpha()


class DiamondDrop(Drop):
    name = "Diamond"
    value = 40
    img = IMG_DIAMOND_DROP
    # img = FONT_EMOJI_MD.render("💎", True, WHITE).convert_alpha()


class RewardUrnDrop(Drop):
    name = "Urn"
    value = 500
    img = IMG_URN_DROP
    # img = FONT_EMOJI_MD.render("🏺", True, WHITE).convert_alpha()


class RewardChaliceDrop(Drop):
    name = "Chalice"
    value = 1000
    img = IMG_CHALICE_DROP
    # img = FONT_EMOJI_MD.render("🏺", True, WHITE).convert_alpha()


class TreeDrop(Drop):
    name = "Log"
    value = 10
    img = IMG_LOG_DROP
    # img = FONT_EMOJI_MD.render("🌳", True, WHITE).convert_alpha()


class House1Drop(Drop):
    name = "House Lvl 1"
    value = 1000
    img = IMG_HOUSE_01 = FONT_EMOJI_MD.render("🏚️", True, WHITE)


class House2Drop(Drop):
    name = "House Lvl 2"
    value = 1000
    img = IMG_HOUSE_02 = FONT_EMOJI_MD.render("🏠️", True, WHITE)


class House3Drop(Drop):
    name = "House Lvl 3"
    value = 1000
    img = IMG_HOUSE_03 = FONT_EMOJI_MD.render("🏡", True, WHITE)


class House4Drop(Drop):
    name = "House Lvl 4"
    value = 1000
    img = IMG_HOUSE_04 = FONT_EMOJI_MD.render("🏛️", True, WHITE)


class Drops(Enum):
    NONE = NoneDrop()
    DIRT = DirtDrop()
    CLAY = ClayDrop()
    COAL = CoalDrop()
    STONE = StoneDrop()
    COPPER = CopperDrop()
    IRON = IronDrop()
    SILVER = SilverDrop()
    GOLD = GoldDrop()
    DIAMOND = DiamondDrop()
    REWARD_URN = RewardUrnDrop()
    REWARD_CHALICE = RewardChaliceDrop()
    TREE_DROP = TreeDrop()
    HOUSE_1 = House1Drop()
    HOUSE_2 = House2Drop()
    HOUSE_3 = House3Drop()
    HOUSE_4 = House4Drop()
