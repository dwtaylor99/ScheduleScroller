from enum import Enum

import pygame

from colors import WHITE

pygame.init()
screen = pygame.display.set_mode((1920 // 2, 1080 // 2))
FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)


class Drop:
    name = ""
    value = 0
    img = None


class NoneDrop(Drop):
    name = "None"


class DirtDrop(Drop):
    name = "Dirt"
    value = 1
    img = FONT_EMOJI_MD.render("🟫", True, WHITE).convert_alpha()


class StoneDrop(Drop):
    name = "Stone"
    value = 1
    img = FONT_EMOJI_MD.render("⚪", True, WHITE).convert_alpha()


class ClayDrop(Drop):
    name = "Clay"
    value = 2
    img = FONT_EMOJI_MD.render("🟤", True, WHITE).convert_alpha()


class CoalDrop(Drop):
    name = "Coal"
    value = 3
    img = FONT_EMOJI_MD.render("⚫", True, WHITE).convert_alpha()


class CopperDrop(Drop):
    name = "Copper"
    value = 5
    img = FONT_EMOJI_MD.render("🔶", True, WHITE).convert_alpha()


class IronDrop(Drop):
    name = "Iron"
    value = 10
    img = FONT_EMOJI_MD.render("🔷", True, WHITE).convert_alpha()


class SilverDrop(Drop):
    name = "Silver"
    value = 15
    img = FONT_EMOJI_MD.render("⬜", True, WHITE).convert_alpha()


class GoldDrop(Drop):
    name = "Gold"
    value = 25
    img = FONT_EMOJI_MD.render("🟨", True, WHITE).convert_alpha()


class DiamondDrop(Drop):
    name = "Diamond"
    value = 40
    img = FONT_EMOJI_MD.render("💎", True, WHITE).convert_alpha()


class RewardUrnDrop(Drop):
    name = "Urn"
    value = 100
    img = FONT_EMOJI_MD.render("🏺", True, WHITE).convert_alpha()


class TreeDrop(Drop):
    name = "Log"
    value = 10
    img = FONT_EMOJI_MD.render("🌳", True, WHITE).convert_alpha()


class Drops(Enum):
    NONE = NoneDrop()
    CLAY = ClayDrop()
    STONE = StoneDrop()
    COPPER = CopperDrop()
    IRON = IronDrop()
    SILVER = SilverDrop()
    GOLD = GoldDrop()
    DIAMOND = DiamondDrop()
    REWARD_URN = RewardUrnDrop()
    TREE_DROP = TreeDrop()
