import pygame

from colors import YELLOW

pygame.init()

FONT_SM = pygame.font.Font("fonts/Inter.ttf", 13)
FONT_MD = pygame.font.Font("fonts/Inter.ttf", 16)
FONT_LG = pygame.font.Font("fonts/Inter.ttf", 30)
FONT_XL = pygame.font.Font("fonts/Inter.ttf", 48)
FONT_XXL = pygame.font.Font("fonts/Inter.ttf", 72)

# Font used in Overdrawn at the Memory Bank
FONT_FINGAL_MD = pygame.font.Font("fonts/HandelGo.ttf", 16)
FONT_FINGAL_LG = pygame.font.Font("fonts/HandelGo.ttf", 30)
FONT_FINGAL_XL = pygame.font.Font("fonts/HandelGo.ttf", 48)

# Font used in modern MST3K stuff
FONT_MST3K_MD = pygame.font.Font("fonts/SimianText_Orangutan.otf", 20)
FONT_MST3K_LG = pygame.font.Font("fonts/SimianText_Orangutan.otf", 36)
FONT_MST3K_XL = pygame.font.Font("fonts/SimianText_Orangutan.otf", 52)

# Font used to render emoji
FONT_EMOJI_SM = pygame.font.Font("fonts/seguiemj.ttf", 18)
FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 22)
FONT_EMOJI_MD2 = pygame.font.Font("fonts/seguiemj.ttf", 36)
FONT_EMOJI_LG = pygame.font.Font("fonts/seguiemj.ttf", 44)
FONT_EMOJI_XL = pygame.font.Font("fonts/seguiemj.ttf", 96)

STR_STINGER = "Name the MST3K movie this stinger is from:"
TXT_STINGER = FONT_MST3K_LG.render(STR_STINGER, True, YELLOW)

STR_CHARACTER = "Name the character:"
TXT_CHARACTER = FONT_MST3K_LG.render(STR_CHARACTER, True, YELLOW)

STR_EMOJI = "Name the MST3K movie described by these emoji:"
TXT_EMOJI = FONT_MST3K_LG.render(STR_EMOJI, True, YELLOW)

STR_SCRAMBLE = "Unscramble the character name:"
TXT_SCRAMBLE = FONT_MST3K_LG.render(STR_SCRAMBLE, True, YELLOW)
