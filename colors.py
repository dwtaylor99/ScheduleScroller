import pygame

BLACK = pygame.Color(0, 0, 0)
BLUE = pygame.Color(0, 0, 120)
LTBLUE = pygame.Color(0, 0, 200)
MEDBLUE = pygame.Color(0, 50, 180)
PALEBLUE = pygame.Color(0, 80, 220)
YELLOW = pygame.Color(192, 192, 0)
WHITE = pygame.Color(192, 192, 192)
DK_GRAY = pygame.Color(32, 32, 32)
GRAY = pygame.Color(128, 128, 128)

JOEL_RED = pygame.Color(201, 58, 34)  # "C93A22"
MIKE_BLUE = pygame.Color(0, 115, 164)  # "0073A4"
JONAH_YELLOW = pygame.Color(211, 161, 1)  # "D3A101"
EMILY_PURPLE = pygame.Color(100, 96, 173)  # "6460AD"
GROUP_GREEN = pygame.Color(33, 130, 0)  # "218200"


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