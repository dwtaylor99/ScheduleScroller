import pygame

from colors import WHITE, BLACK
from dig_game_drops import Drops
from fonts import FONT_EMOJI_MD

UI_BG_COLOR = (37, 57, 113)

TXT_UPGRADE_HOUSE = FONT_EMOJI_MD.render("Upgrade House:", True, WHITE).convert_alpha()
TXT_UPGRADE = FONT_EMOJI_MD.render("Upgrade", True, WHITE).convert_alpha()
TXT_HOUSE_UP1 = FONT_EMOJI_MD.render("🏚️ ➡️ 🏠️", True, WHITE).convert_alpha()
TXT_HOUSE_UP2 = FONT_EMOJI_MD.render("🏠️ ➡️ 🏡", True, WHITE).convert_alpha()
TXT_HOUSE_UP3 = FONT_EMOJI_MD.render("🏡 ➡️ 🏛️", True, WHITE).convert_alpha()
TXT_TIMES = FONT_EMOJI_MD.render("✖️", True, WHITE)

house_ui_open = False

line_height = 30


def button(house_ui, x, y, w, h, text):
    pygame.draw.rect(house_ui, (160, 160, 160), (x, y, w, h))
    pygame.draw.rect(house_ui, BLACK, (x, y, w, h), 2)
    pygame.draw.line(house_ui, (200, 200, 200), (x, y), (x + w - 3, y), 2)
    pygame.draw.line(house_ui, (200, 200, 200), (x, y), (x, y + h - 3), 2)

    text = FONT_EMOJI_MD.render(text, True, BLACK).convert_alpha()
    house_ui.blit(text, (x + (w - text.get_width()) // 2, y + (h - text.get_height()) // 2))


def build_ui(ui_w, ui_h, player):
    house_ui = pygame.Surface((ui_w, ui_h))
    house_ui.fill(UI_BG_COLOR)

    button(house_ui, 20, 20, 100, 30, "Upgrade")
    if player.house_index < 2:
        # house_ui.blit(TXT_UPGRADE, (20, 20))
        if player.house_index == 0:
            house_ui.blit(TXT_HOUSE_UP1, (200, 18))
            house_ui.blit(Drops.STONE.value.img, (30, 20 + line_height + 4))
            house_ui.blit(TXT_TIMES, (70, 20 + line_height + 12))

    return house_ui


"""
TODO:
* Add House UI:
    * Allow house upgrade with significant resources required
    * Allow tool recharge somehow: house can give 15% for free, coal is used to refill fully
    * Ability to construct single-use batteries (copper + iron?) for longer use of tool
    * Exchange inventory for crafted items
    * Craft flashlight to expand sight line
* Way to increase tool distance?
"""