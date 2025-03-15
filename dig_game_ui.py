import pygame

from colors import WHITE, BLACK
from dig_game_colors import HOLLOW_COLOR
from dig_game_drops import Drops
from dig_game_tiles import Tiles
from fonts import FONT_EMOJI_MD, FONT_EMOJI_MD2

UI_BG_COLOR = (37, 57, 113)

TXT_UPGRADE_HOUSE = FONT_EMOJI_MD.render("Upgrade House:", True, WHITE).convert_alpha()
TXT_UPGRADE = FONT_EMOJI_MD.render("Upgrade", True, WHITE).convert_alpha()
TXT_HOUSE_UP1 = FONT_EMOJI_MD2.render("🏚️ ➡️ 🏠️", True, WHITE).convert_alpha()
TXT_HOUSE_UP2 = FONT_EMOJI_MD2.render("🏠️ ➡️ 🏡", True, WHITE).convert_alpha()
TXT_HOUSE_UP3 = FONT_EMOJI_MD2.render("🏡 ➡️ 🏛️", True, WHITE).convert_alpha()
TXT_TIMES = FONT_EMOJI_MD.render("✖️", True, WHITE)

house_upgrade_1 = {
    Tiles.TREE_01: 10,
    Tiles.STONE: 30,
    Tiles.CLAY: 20,
    Tiles.COPPER: 15
}

line_height = 48


def button(house_ui, x, y, w, h, text):
    pygame.draw.rect(house_ui, (160, 160, 160), (x, y, w, h))
    pygame.draw.rect(house_ui, BLACK, (x, y, w, h), 2)
    pygame.draw.line(house_ui, (200, 200, 200), (x, y), (x + w - 3, y), 2)
    pygame.draw.line(house_ui, (200, 200, 200), (x, y), (x, y + h - 3), 2)

    text = FONT_EMOJI_MD.render(text, True, BLACK).convert_alpha()
    house_ui.blit(text, (x + (w - text.get_width()) // 2, y + (h - text.get_height()) // 2))


def build_ui(ui_w, ui_h, player):
    # Background
    house_ui = pygame.Surface((ui_w, ui_h))
    house_ui.fill(HOLLOW_COLOR)
    house_ui.set_colorkey(HOLLOW_COLOR)
    pygame.draw.rect(house_ui, UI_BG_COLOR, (0, 0, ui_w, ui_h), 0, 10)

    # House Upgrade
    if player.house_index < 2:
        if player.house_index == 0:
            house_ui.blit(TXT_HOUSE_UP1, (20, 18))

            for i, key in enumerate(house_upgrade_1.keys()):
                res_amt = house_upgrade_1[key]
                drop = key.value.drop

                house_ui.blit(drop.value.img, (30, i * line_height + 80))
                house_ui.blit(TXT_TIMES, (70, i * line_height + 90))
                res_color = (200, 40, 40)
                if key in player.inv_dict.keys() and player.inv_dict[key] >= res_amt:
                    res_color = (40, 200, 40)
                house_ui.blit(FONT_EMOJI_MD2.render(str(res_amt), True, res_color).convert_alpha(), (100,  i * line_height + 86))

        button(house_ui, 20, (line_height * 5) + 44, 100, 30, "Upgrade")

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