import random

import pygame

from colors import WHITE, BLACK
from fonts import FONT_MST3K_XL, TXT_SCRAMBLE

LETTER_W = 52
LETTER_H = 48
SPACING = 10
SCRAMBLED_WORDS = ["APOLLONIA", "ARDY", "ATOR", "BARUGON", "BATWOMAN", "BEEPER", "CAMBOT", "CORNJOB", "CLEOLANTA",
                   "DIABOLIK", "MORDRID", "EXETER", "FINGAL", "FORRESTER", "FRANK", "GAMERA", "GODZILLA",
                   "GOOSIO", "GUIRON", "GYPSY", "HAMLET", "HERCULES", "JIGER", "JONAH", "KINGA", "KOLOS", "MEGAWEAPON",
                   "MUNCHIE", "NUVEENA", "OBSERVER", "ORTEGA", "PEARL", "PITCH", "PIPPER", "SANTO", "SANTA", "SUMURU",
                   "STUMPY", "SYNTHIA", "SERVO", "TOBLERONE", "TORGO", "VADINHO", "VALARIA", "VORELLI", "ROWSDOWER",
                   "ZIGRA"]


def scramble(word: str) -> str:
    word = list(word)
    random.shuffle(word)
    return "".join(word)


def draw(alt_screen, scrambled):
    alt_screen.blit(TXT_SCRAMBLE, ((alt_screen.get_width() - TXT_SCRAMBLE.get_width()) // 2, 100))

    full_width = len(scrambled) * (LETTER_W + SPACING)
    x = ((alt_screen.get_width() - full_width) // 2)
    for i, ch in enumerate(scrambled):
        letter = FONT_MST3K_XL.render(ch, True, BLACK)
        cent_x = (LETTER_W - letter.get_width()) // 2
        pygame.draw.rect(alt_screen, WHITE, (x, 250, LETTER_W, LETTER_H), 0, 4)
        alt_screen.blit(letter, (x + cent_x, 250))
        x += LETTER_W + SPACING

    return alt_screen


if __name__ == '__main__':
    print(scramble(SCRAMBLED_WORDS[0]))
