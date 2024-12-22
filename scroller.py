from datetime import datetime

import schedule
import summaries
from deathray import DeathRay
from elsanto import ElSanto
from gamera import Gamera
from gradient import rect_gradient_h
from sandstorm import SandStorm
from schedule import PAC_TZ
from starfighter import Starfighter
from ufo import *
from util_text import *
from vampire_woman import VampireWoman

pygame.init()

# Constants
WIDTH = 1920
HEIGHT = 1080

WIDTH_HALF = int(WIDTH / 2)
HEIGHT_HALF = int(HEIGHT / 2)

# Dimensions of the schedule bars
SCHED_H = 60
SCHED_COL1_X = 30
SCHED_COL2_X = 320
SCHED_COL3_X = 600
DOW_W = 80

# Create two fonts
FONT_FACE = "arial"
FONT_SIZE = 32
FONT = pygame.font.SysFont(FONT_FACE, FONT_SIZE)

FONT_SIZE_SMALL = 26
FONT_SM = pygame.font.SysFont(FONT_FACE, FONT_SIZE_SMALL)

FONT_SIZE_LARGE = 40
FONT_LG = pygame.font.SysFont(FONT_FACE, FONT_SIZE_LARGE)

FONT_PAD = 10  # vertical font spacing

# Colors
BLACK = pygame.Color(0, 0, 0)
BLUE = pygame.Color(0, 0, 120)
LTBLUE = pygame.Color(0, 0, 200)
PALEBLUE = pygame.Color(0, 80, 220)
YELLOW = pygame.Color(192, 192, 0)
WHITE = pygame.Color(192, 192, 192)
DK_GRAY = pygame.Color(32, 32, 32)

NUM_SCHEDULE = 20  # Number of schedule items to load

CLOCK_FORMAT = "%I:%M:%S %p"

# Globals
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
sched = []
hdr_y = 0
ticker = 0
timer_tick = 0  # start it at 1 so we don't trigger 'fun' immediately
is_reloading = False
is_fun = False

is_ufo = False
ufo = None

is_starfighter = False
starfighters = []

is_vampire_woman = False
elsanto = None
vampire_woman = None

is_sandstorm = False
sandstorms = []

is_gamera = False
gamera = None

is_deathray = False
deathray = None
HOLE_IMG = pygame.transform.smoothscale_by(pygame.image.load('images/fun/hole_sm.png').convert_alpha(), 1.0)


def fun():
    global is_fun, is_ufo, is_starfighter, is_vampire_woman, is_sandstorm, is_gamera, is_deathray

    if is_deathray:
        offset = 52

        # Step 0: Raise the Death Ray
        if deathray.anim_step == 0:
            screen.blit(deathray.img, (deathray.x, deathray.y))
            if deathray.y >= HEIGHT_HALF - deathray.img.get_height():
                deathray.y += deathray.velocity
            else:
                deathray.anim_step += 1  # move the next step of animation

        # Step 1: Fire the Death Ray
        if deathray.anim_step == 1:
            screen.blit(deathray.img, (deathray.x, deathray.y))
            if ticker % 3 == 0:
                for i in range(9):
                    pygame.draw.aaline(screen, deathray.RAY_COLOR,
                                       (deathray.x + deathray.img.get_width() - 6, deathray.y + i + offset),
                                       (deathray.x + deathray.img.get_width() + 650, deathray.y + i + (offset - 28)))
            if deathray.ticks > 200:
                deathray.anim_step += 1

        # Step 2: Explosion and hole
        if deathray.anim_step == 2:
            screen.blit(deathray.img, (deathray.x, deathray.y))
            screen.blit(HOLE_IMG, (1133, 367))
            if deathray.ticks > 360:
                deathray.anim_step += 1

        # Step 3: Lower the Death Ray
        if deathray.anim_step == 3:
            screen.blit(deathray.img, (deathray.x, deathray.y))
            screen.blit(HOLE_IMG, (1133, 367))
            if deathray.y <= HEIGHT_HALF:
                deathray.y += -deathray.velocity
            else:
                deathray.anim_step += 1  # move the next step of animation

        # Step 4: Fade out the hole
        if deathray.anim_step == 4:
            HOLE_IMG.set_alpha(HOLE_IMG.get_alpha() - 2)
            screen.blit(HOLE_IMG, (1133, 367))
            if HOLE_IMG.get_alpha() == 0:
                is_deathray = False
                is_fun = False
        deathray.ticks += 1

    if is_gamera:
        screen.blit(gamera.img, (gamera.x, gamera.y))
        gamera.x += gamera.velocity
        if gamera.x > WIDTH:
            is_gamera = False
            is_fun = False

    if is_sandstorm:
        all_offscreen = True
        for s in sandstorms:
            screen.blit(s.img, (s.x, s.y))
            s.x += s.velocity
            if s.x < WIDTH:
                all_offscreen = False
        if all_offscreen:
            is_sandstorm = False
            is_fun = False
            sandstorms.clear()

    if is_starfighter:
        all_offscreen = True
        for s in starfighters:
            screen.blit(s.img, (s.x, s.y))
            s.x += s.velocity
            if s.x > -s.img.get_width():
                all_offscreen = False
        if all_offscreen:
            is_starfighter = False
            is_fun = False
            starfighters.clear()

    if is_ufo:
        screen.blit(ufo.img, (ufo.x, ufo.y))
        ufo.x += ufo.velocity
        if ufo.x > WIDTH + ufo.img.get_width():
            is_ufo = False
            is_fun = False

    if is_vampire_woman:
        screen.blit(vampire_woman.img, (vampire_woman.x, vampire_woman.y))
        screen.blit(elsanto.img, (elsanto.x, elsanto.y))
        vampire_woman.y += vampire_woman.velocity
        elsanto.y += elsanto.velocity
        elsanto.x = vampire_woman.x + 25
        if vampire_woman.y + vampire_woman.img.get_height() < HEIGHT_HALF:
            vampire_woman.velocity = -vampire_woman.velocity
            elsanto.velocity = -elsanto.velocity
        if vampire_woman.y > HEIGHT_HALF and vampire_woman.velocity > 0:
            is_vampire_woman = False
            is_fun = False


def draw_image():
    bg = pygame.Rect(0, 0, WIDTH_HALF, HEIGHT_HALF)
    rect_gradient_h(screen, BLACK, DK_GRAY, bg)

    img = pygame.image.load('images/' + sched[0]['image']).convert()
    iw = img.get_width()
    ih = img.get_height()

    new_w = (WIDTH_HALF / iw)
    new_h = (HEIGHT_HALF / ih)

    if new_w < new_h:
        img_scaled = pygame.transform.smoothscale_by(img, new_w)
    else:
        img_scaled = pygame.transform.smoothscale_by(img, new_h)

    iws = (WIDTH_HALF - img_scaled.get_width()) / 2
    screen.blit(img_scaled, (iws, 0))


def draw_summary():
    """Split the long 'about' string into several pieces and render them."""

    bg = pygame.Rect(WIDTH_HALF, 0, WIDTH_HALF, HEIGHT_HALF)
    rect_gradient_h(screen, BLACK, DK_GRAY, bg)

    summary = prepare_summary(sched[0]['about'])
    summary += " (" + sched[0]['year'] + ")"
    s = wrap_text(summary).strip()
    parts = s.split("\n")
    for i, p in enumerate(parts):
        screen.blit(FONT.render(p, True, BLACK), (WIDTH_HALF + 32, ((FONT_SIZE + 10) * i) + 16))
        screen.blit(FONT.render(p, True, WHITE), (WIDTH_HALF + 30, ((FONT_SIZE + 10) * i) + 14))


def draw_schedule_header():
    """This is the schedule header that doesn't scroll"""

    y = int(HEIGHT / 2)
    bg_border = pygame.Rect(0, y, WIDTH, SCHED_H)
    pygame.draw.rect(screen, WHITE, bg_border)

    bg = pygame.Rect(2, y + 2, WIDTH - 3, SCHED_H - 3)
    rect_gradient_h(screen, LTBLUE, BLUE, bg)

    screen.blit(FONT.render("Playing:", True, BLACK), (SCHED_COL3_X + 2, y + 2 + FONT_PAD))
    screen.blit(FONT.render("Playing:", True, YELLOW), (SCHED_COL3_X, y + FONT_PAD))

    title = update_title(sched[0]['title'], sched[0]['epnum'])
    screen.blit(FONT.render(title, True, BLACK), (SCHED_COL3_X + 126, y + 2 + FONT_PAD))
    screen.blit(FONT.render(title, True, WHITE), (SCHED_COL3_X + 128, y + FONT_PAD))


def draw_scrolling_header():
    """The scrolling header is part of the scrolling list of titles"""

    global hdr_y
    hdr_y -= 1
    if hdr_y < HEIGHT_HALF:
        # Move this item to the end of the list
        hdr_y += int((len(sched) + 1) * SCHED_H)

    bg_border = pygame.Rect(0, hdr_y, WIDTH, SCHED_H)
    pygame.draw.rect(screen, WHITE, bg_border)

    bg = pygame.Rect(2, hdr_y + 2, WIDTH - 3, SCHED_H - 3)
    rect_gradient_h(screen, LTBLUE, BLUE, bg)

    screen.blit(FONT.render("PST", True, BLACK), (SCHED_COL1_X + 2, hdr_y + 2 + FONT_PAD))
    screen.blit(FONT.render("EST", True, BLACK), (SCHED_COL2_X + 2, hdr_y + 2 + FONT_PAD))
    screen.blit(FONT.render("Title", True, BLACK), (SCHED_COL3_X + 2, hdr_y + 2 + FONT_PAD))

    screen.blit(FONT.render("PST", True, YELLOW), (SCHED_COL1_X, hdr_y + FONT_PAD))
    screen.blit(FONT.render("EST", True, YELLOW), (SCHED_COL2_X, hdr_y + FONT_PAD))
    screen.blit(FONT.render("Title", True, YELLOW), (SCHED_COL3_X, hdr_y + FONT_PAD))


def draw_schedule_item(obj, y):
    if y < HEIGHT_HALF:
        # Move this item to the end of the list
        y += int((len(sched) + 1) * SCHED_H)

    bg_border = pygame.Rect(0, y, WIDTH, SCHED_H)
    pygame.draw.rect(screen, WHITE, bg_border)

    bg = pygame.Rect(2, y + 2, WIDTH - 3, SCHED_H - 3)
    rect_gradient_h(screen, PALEBLUE, LTBLUE, bg)

    title_display = update_title(obj['title'], obj['epnum'])

    # Separate the DOW and Time into individual columns
    pos1 = obj['time'].find(" ")
    dow1 = obj['time'][:pos1]
    time1 = obj['time'][pos1 + 1:]

    pos2 = obj['time_est'].find(" ")
    dow2 = obj['time_est'][:pos2]
    time2 = obj['time_est'][pos2 + 1:]

    if len(time1) == 7:
        time1 = "  " + time1

    if len(time2) == 7:
        time2 = "  " + time2

    screen.blit(FONT.render(dow1, True, BLACK), (SCHED_COL1_X + 2, y + 2 + FONT_PAD))
    screen.blit(FONT.render(dow2, True, BLACK), (SCHED_COL2_X + 2, y + 2 + FONT_PAD))
    screen.blit(FONT.render(time1, True, BLACK), (SCHED_COL1_X + DOW_W + 2, y + 2 + FONT_PAD))
    screen.blit(FONT.render(time2, True, BLACK), (SCHED_COL2_X + DOW_W + 2, y + 2 + FONT_PAD))
    screen.blit(FONT.render(title_display, True, BLACK), (SCHED_COL3_X + 2, y + 2 + FONT_PAD))

    screen.blit(FONT.render(dow1, True, WHITE), (SCHED_COL1_X, y + FONT_PAD))
    screen.blit(FONT.render(dow2, True, WHITE), (SCHED_COL2_X, y + FONT_PAD))
    screen.blit(FONT.render(time1, True, WHITE), (SCHED_COL1_X + DOW_W, y + FONT_PAD))
    screen.blit(FONT.render(time2, True, WHITE), (SCHED_COL2_X + DOW_W, y + FONT_PAD))
    screen.blit(FONT.render(title_display, True, WHITE), (SCHED_COL3_X, y + FONT_PAD))

    obj['y'] = y


def draw_schedule_items(y):
    for s in sched:
        draw_schedule_item(s, y)
        y += SCHED_H


def move_schedule():
    for s in sched:
        draw_schedule_item(s, s['y'] - 1)

    # Add a scrolling header to indicate the list is restarting
    draw_scrolling_header()


def draw_clock():
    global sched, hdr_y, is_reloading

    pac = datetime.now().astimezone(PAC_TZ)
    pac_time = datetime.strftime(pac, CLOCK_FORMAT).lstrip("0")
    screen.blit(FONT.render(pac_time, True, BLACK), (SCHED_COL1_X + 2, HEIGHT_HALF + 2 + FONT_PAD))
    screen.blit(FONT.render(pac_time, True, YELLOW), (SCHED_COL1_X, HEIGHT_HALF + FONT_PAD))

    curr_time = datetime.strftime(datetime.now(), CLOCK_FORMAT).lstrip("0")
    screen.blit(FONT.render(curr_time, True, BLACK), (SCHED_COL2_X + 2, HEIGHT_HALF + 2 + FONT_PAD))
    screen.blit(FONT.render(curr_time, True, YELLOW), (SCHED_COL2_X, HEIGHT_HALF + FONT_PAD))

    # Is it time to reload the schedule?
    time_parts = sched[1]['time_est'].split(" ")
    update_time = time_parts[1] + ":00 " + time_parts[2]
    if curr_time == update_time and not is_reloading:
        is_reloading = True
        start_t = datetime.now()
        print("Loading...")
        schedule.refresh()
        sched = schedule.get_schedule(schedule.US_PAC, NUM_SCHEDULE)
        draw_schedule_items(HEIGHT_HALF + SCHED_H)
        hdr_y = HEIGHT_HALF + (len(sched) + 1) * SCHED_H
        stop_t = datetime.now()
        print("done. " + str(stop_t - start_t))
        is_reloading = False


def draw_vertical_separators():
    sep1 = pygame.Rect(SCHED_COL2_X - 30, HEIGHT_HALF, 2, HEIGHT_HALF)
    pygame.draw.rect(screen, WHITE, sep1)

    sep1 = pygame.Rect(SCHED_COL3_X - 30, HEIGHT_HALF, 2, HEIGHT_HALF)
    pygame.draw.rect(screen, WHITE, sep1)


def setup():
    global sched, hdr_y

    print("Loading...")
    start_time = datetime.now()
    summaries.refresh()
    schedule.refresh()
    sched = schedule.get_schedule(schedule.US_PAC, NUM_SCHEDULE)
    stop_time = datetime.now()
    print("done. " + str(stop_time - start_time))

    draw_schedule_items(HEIGHT_HALF + SCHED_H)
    hdr_y = HEIGHT_HALF + (len(sched) + 1) * SCHED_H


if __name__ == '__main__':
    setup()

    while running:
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        draw_image()
        draw_summary()
        fun()
        move_schedule()
        draw_schedule_header()
        draw_vertical_separators()
        draw_clock()

        # Time for fun?
        # random_fun = random.randrange(1, 5)  # 20% chance of fun every minute
        random_fun = 1
        if int(timer_tick) % 60 == 0 and not is_fun and random_fun == 1:
            is_fun = True
            title = sched[0]['title']
            epnum = sched[0]['epnum']
            print("Starting fun for: {} {}".format(title, epnum))

            if epnum == "620":
                is_deathray = True
                deathray = DeathRay()

            if epnum in ["302", "304", "308", "312", "316", "1307"] and not is_gamera:
                is_gamera = True
                gamera = Gamera()

            if epnum == "410" and not is_sandstorm:
                is_sandstorm = True
                for _ in range(random.randrange(5, 10)):
                    sandstorms.append(SandStorm())

            if epnum == "612" and not is_starfighter:
                is_starfighter = True
                for _ in range(random.randrange(3, 5)):
                    starfighters.append(Starfighter())

            if epnum == "624" and not is_vampire_woman:
                is_vampire_woman = True
                elsanto = ElSanto()
                vampire_woman = VampireWoman()

            if epnum == "" and not is_ufo:
                ufo = Ufo()
                is_ufo = True

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60 - dt is delta time in seconds since last frame.
        ticker += 1
        if ticker > 60000:
            ticker = 0

        dt = clock.tick(60) / 1000
        timer_tick += dt
        # Reset the timer_tick every hour so we don't overflow the variable.
        if timer_tick >= 3600:
            timer_tick = 0

    pygame.quit()
