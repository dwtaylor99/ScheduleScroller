import pygame

from colors import BLACK


def build_ui(ui_w, ui_h):
    house_ui = pygame.Surface((ui_w, ui_h))
    house_ui.fill((64, 64, 64))

    return house_ui
