"""https://stackoverflow.com/questions/62336555/how-to-add-color-gradient-to-rectangle-in-pygame"""

import pygame


def rect_gradient_v(window, left_color, right_color, target_rect):
    """Draw a horizontal-gradient filled rectangle covering <target_rect>"""

    color_rect = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
    pygame.draw.line(color_rect, left_color, (0, 0), (0, 1))  # left color line
    pygame.draw.line(color_rect, right_color, (1, 0), (1, 1))  # right color line
    color_rect = pygame.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))  # stretch!
    window.blit(color_rect, target_rect)


def rect_gradient_h(window, top_color, bottom_color, target_rect):
    """Draw a horizontal-gradient filled rectangle covering <target_rect>"""

    color_rect = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
    pygame.draw.line(color_rect, top_color, (0, 0), (1, 0))  # left color line
    pygame.draw.line(color_rect, bottom_color, (0, 1), (1, 1))  # right color line
    color_rect = pygame.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))  # stretch!
    window.blit(color_rect, target_rect)