from datetime import datetime

import pygame

import funfactory
import schedule
import summaries
from gradient import rect_gradient_h
from schedule import PAC_TZ
from ufo import *
from util_text import *

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
main_img = pygame.Surface((WIDTH, HEIGHT))

fun_obj = None
fun_objs = []


def draw_image():
    global main_img

    bg = pygame.Rect(0, 0, WIDTH_HALF, HEIGHT_HALF)
    rect_gradient_h(screen, BLACK, DK_GRAY, bg)

    if main_img is not None:
        iw = main_img.get_width()
        ih = main_img.get_height()

        new_w = (WIDTH_HALF / iw)
        new_h = (HEIGHT_HALF / ih)

        if new_w < new_h:
            img_scaled = pygame.transform.smoothscale_by(main_img, new_w)
        else:
            img_scaled = pygame.transform.smoothscale_by(main_img, new_h)

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
    global hdr_y, main_img, sched

    print("Loading...")
    start_time = datetime.now()
    summaries.refresh()
    schedule.refresh()
    sched = schedule.get_schedule(schedule.US_PAC, NUM_SCHEDULE)
    stop_time = datetime.now()
    print("done. " + str(stop_time - start_time))

    main_img = pygame.image.load('images/' + sched[0]['image']).convert()
    draw_schedule_items(HEIGHT_HALF + SCHED_H)
    hdr_y = HEIGHT_HALF + (len(sched) + 1) * SCHED_H


def fun():
    if len(fun_objs) > 0:
        for o in fun_objs:
            o.animate()


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
        if int(timer_tick) % 60 == 0 and random_fun == 1:
            title = sched[0]['title']
            epnum = sched[0]['epnum']
            print("Starting fun for: {} {}".format(title, epnum))
            fun_objs = funfactory.get(screen, title, epnum)

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
