import pygame

pygame.init()

WIDTH = 1920 // 2
HEIGHT = 1080 // 2
FPS = 60

BLACK = (0, 0, 0)
WHITE = (192, 192, 192)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
is_running = True
dt = 0

EMJ_NINJA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/ninja_1f977.png'), 0.12).convert_alpha()

FONT = pygame.font.Font('fonts/seguiemj.ttf', 36)

TEST1 = "Name the MST3K movie: 🤖🆚🇲🇽⚰️🧟‍♂️"
TEST2 = "👨‍🏫🥷🥷👨‍🏫"

TEST2 = TEST2.replace("🥷", "   ")

TXT1 = FONT.render(TEST1, True, WHITE)
TXT2 = FONT.render(TEST2, True, WHITE)


def main_loop():
    global is_running, dt

    while is_running:
        screen.fill(BLACK)

        screen.blit(TXT1, (20, 20))
        screen.blit(TXT2, (20, 70))

        for event in pygame.event.get():
            if event == pygame.QUIT:
                is_running = False

        pygame.display.flip()
        dt = clock.tick(FPS)


if __name__ == '__main__':
    main_loop()
    pygame.quit()
