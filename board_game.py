import pygame.display


class BoardSpace:
    x: int = 0
    y: int = 0
    w: int = 64
    h: int = 64
    bg = (192, 192, 192)


pygame.init()
screen = pygame.display.set_mode((1920 // 2, 1080 // 2))
board: [BoardSpace] = []


def build_board():
    for i in range(12):
        bs = BoardSpace()
        bs.x = i * (bs.w + 10) + 40
        bs.y = 10
        board.append(bs)

    bs = BoardSpace()
    bs.x = 11 * (bs.w + 10) + 40
    bs.y = bs.h + 20
    board.append(bs)

    for i in range(12):
        bs = BoardSpace()
        bs.x = (11 - i) * (bs.w + 10) + 40
        bs.y = bs.w * 2 + 30
        board.append(bs)

    bs = BoardSpace()
    bs.x = 40
    bs.y = bs.h * 3 + 40
    board.append(bs)

    for i in range(12):
        bs = BoardSpace()
        bs.x = i * (bs.w + 10) + 40
        bs.y = bs.h * 4 + 50
        board.append(bs)

    bs = BoardSpace()
    bs.x = 11 * (bs.w + 10) + 40
    bs.y = bs.h * 5 + 60
    board.append(bs)

    for i in range(12):
        bs = BoardSpace()
        bs.x = (11 - i) * (bs.w + 10) + 40
        bs.y = bs.w * 6 + 70
        board.append(bs)


if __name__ == '__main__':
    build_board()

    running = True
    while running:
        for b in board:
            pygame.draw.rect(screen, b.bg, (b.x, b.y, b.w, b.h))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
