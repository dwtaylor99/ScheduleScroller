import pygame


UI_BG_COLOR = (37, 57, 113)

house_ui_open = False


def build_ui(ui_w, ui_h):
    house_ui = pygame.Surface((ui_w, ui_h))
    house_ui.fill(UI_BG_COLOR)

    return house_ui
