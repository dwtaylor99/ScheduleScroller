from datetime import datetime

import pygame

from constants import VALENTINES_DAY, ST_PATRICKS_DAY

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(192, 192, 192)
DK_GRAY = pygame.Color(32, 32, 32)
GRAY = pygame.Color(128, 128, 128)
YELLOW = pygame.Color(192, 192, 0)

GREEN = pygame.Color(0, 128, 0)
LT_GREEN = pygame.Color(70, 150, 80)

BLUE = pygame.Color(0, 0, 120)
LT_BLUE = pygame.Color(0, 0, 200)
MED_BLUE = pygame.Color(0, 50, 180)
PALE_BLUE = pygame.Color(0, 80, 220)

RED = pygame.Color(120, 0, 0)
MED_RED = pygame.Color(196, 90, 118)
LT_RED = pygame.Color(156, 70, 82)


JOEL_RED = pygame.Color(201, 58, 34)  # "C93A22"
MIKE_BLUE = pygame.Color(0, 115, 164)  # "0073A4"
JONAH_YELLOW = pygame.Color(211, 161, 1)  # "D3A101"
EMILY_PURPLE = pygame.Color(100, 96, 173)  # "6460AD"
GROUP_GREEN = pygame.Color(33, 130, 0)  # "218200"

# Color schemes [dark, medium, light]:
# dark and light are used for the gradient, medium used for scroller background
SCHEME_DEFAULT = [BLUE, MED_BLUE, LT_BLUE]
SCHEME_PINK = [(120, 15, 15), (170, 80, 80), (196, 20, 20)]
SCHEME_GREEN = [(22, 80, 30), (30, 115, 35), (60, 140, 60)]

# Set the color scheme
COLOR_SCHEME = SCHEME_DEFAULT
DATE_YYYY = datetime.strftime(datetime.now(), "%Y-%m-%d")
if DATE_YYYY == VALENTINES_DAY:
    COLOR_SCHEME = SCHEME_PINK
elif DATE_YYYY == ST_PATRICKS_DAY:
    COLOR_SCHEME = SCHEME_GREEN


def get_host_color(epnum):
    num = int(epnum)

    host_color = JOEL_RED
    if 512 < num <= 1013:
        host_color = MIKE_BLUE
    elif 1101 < num <= 1302 or num in [1304, 1307, 1309, 1311]:
        host_color = JONAH_YELLOW
    elif num in [1303, 1305, 1308, 1310]:
        host_color = EMILY_PURPLE
    elif num in [1306, 1312]:
        host_color = JOEL_RED
    elif num == 1313:
        host_color = GROUP_GREEN

    return host_color
