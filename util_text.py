import pygame

EMDASH = "—"
ENDASH = "–"


def prepare_summary(summary: str) -> str:
    return summary.replace("--", ENDASH)


def update_title(title, epnum):
    title_display = title
    if title.startswith("The Incredibly Strange Creatures"):
        title_display = "The Incredibly Strange Creatures…"
    if epnum != "":
        title_display += " (" + epnum + ")"
    return title_display


def drop_shadow(screen, font, text, color, x, y, drop=1):
    screen.blit(font.render(text, True, (0, 0, 0)), (x + drop, y + drop))
    screen.blit(font.render(text, True, color), (x, y))


def get_center(surf1: pygame.Surface, surf2: pygame.Surface):
    """Calculate the center of surf2 inside surf1"""
    return (surf1.get_width() - surf2.get_width()) // 2, (surf1.get_height() - surf2.get_height()) // 2


def levenshtein_distance(str1: str, str2: str):
    """
    Calculate how similar two strings are.
    https://rosettacode.org/wiki/Levenshtein_distance#Python
    """
    m = len(str1)
    n = len(str2)
    lensum = float(m + n)
    d = []
    for i in range(m + 1):
        d.append([i])
    del d[0][0]
    for j in range(n + 1):
        d[0].append(j)
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if str1[i - 1] == str2[j - 1]:
                d[i].insert(j, d[i - 1][j - 1])
            else:
                minimum = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 2)
                d[i].insert(j, minimum)
    ldist = d[-1][-1]
    ratio = (lensum - ldist) / lensum
    return {'distance': ldist, 'ratio': ratio}


def wrap_text(text) -> str:
    s = ""
    last_space = 0
    for i in range(0, len(text)):
        t = text[i]

        if i % 52 == 0:
            s = s[:last_space + 1] + "\n" + s[last_space + 2:]

        if t == " ":
            last_space = i

        s += t
    return s
