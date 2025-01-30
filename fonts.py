import pygame

from colors import YELLOW

FONT_MD = pygame.font.Font("fonts/Inter.ttf", 16)
FONT_LG = pygame.font.Font("fonts/Inter.ttf", 30)
FONT_XL = pygame.font.Font("fonts/Inter.ttf", 48)

# Font used in Overdrawn at the Memory Bank
FONT_FINGAL_MD = pygame.font.Font("fonts/HandelGo.ttf", 16)
FONT_FINGAL_LG = pygame.font.Font("fonts/HandelGo.ttf", 30)
FONT_FINGAL_XL = pygame.font.Font("fonts/HandelGo.ttf", 48)

# Font used in modern MST3K stuff
FONT_MST3K_MD = pygame.font.Font("fonts/SimianText_Orangutan.otf", 20)
FONT_MST3K_LG = pygame.font.Font("fonts/SimianText_Orangutan.otf", 36)
FONT_MST3K_XL = pygame.font.Font("fonts/SimianText_Orangutan.otf", 52)

# Font used to render emoji
FONT_EMOJI_LG = pygame.font.Font("fonts/seguiemj.ttf", 44)

STR_STINGER = "Name the MST3K movie this stinger is from:"
TXT_STINGER = FONT_MST3K_LG.render(STR_STINGER, True, YELLOW)

STR_CHARACTER = "Name the character:"
TXT_CHARACTER = FONT_MST3K_LG.render(STR_CHARACTER, True, YELLOW)

STR_EMOJI = "Name the MST3K movie described by these emoji:"
TXT_EMOJI = FONT_MST3K_LG.render(STR_EMOJI, True, YELLOW)