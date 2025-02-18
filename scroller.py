import os.path
import random
import urllib.error

import pygame.display

import schedule
import summaries
from anims.candy_heart_snow import CandyHeartSnow
from anims.clover_snow import CloverSnow
from anims.lights_off import LightsOff
from anims.snow import SnowFlake
from colors import *
from constants import VALENTINES_DAY
from gradient import rect_gradient_h
from schedule import PAC_TZ, EST_TZ
from util_text import *

pygame.init()

# Constants
DEBUG = False

WIDTH = 1920
HEIGHT = 1080

WIDTH_HALF = WIDTH // 2
HEIGHT_HALF = HEIGHT // 2

# Dimensions of the schedule bars
SCHED_H = 60
SCHED_COL1_X = 30
SCHED_COL2_X = 320
SCHED_COL3_X = 610
DOW_W = 80
HOUR_W = 20
MIN_W = 36
MERID_W = 50

FONT_FACE_SIM = "fonts/SimianText_Orangutan.otf"
FONT_SIZE = 36
FONT = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE)

FONT_SIZE_EXTRA_SMALL = 18
FONT_XS = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE_EXTRA_SMALL)

FONT_SIZE_SMALL = 26
FONT_SM = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE_SMALL)

FONT_SIZE_LARGE = 40
FONT_LG = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE_LARGE)

TXT_LOADING = FONT_LG.render("Loading...", True, WHITE)

STR_TWITCH = "twitch.tv/mst3k"
STR_GIZMO = "gizmoplex.com"

# vertical font spacing
FONT_PAD = 10

NUM_SCHEDULE = 20  # Number of schedule items to load

CLOCK_FORMAT = "%I:%M:%S %p %Z"

# Globals
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("ScheduleScroller")
# clock = pygame.time.Clock()
running = True
dt = 0
sched = []
hdr_y = 0
timer_tick = 0  # start it at 1 so we don't trigger 'fun' immediately
is_reloading = False
is_loading_fun = False
main_img = pygame.Surface((WIDTH, HEIGHT))
main_summary = ""
main_year = ""
fun_objs = []
time_until = ""  # Used to display time until next movie

animation = None
anim_x1 = 0
anim_x2 = 0

# Used for fading between "Playing" and "Up Next"
header_color = pygame.Color(192, 192, 0, 0)
title_color = pygame.Color(192, 192, 192, 0)

# NUM_SNOWFLAKES = 100
NUM_SNOWFLAKES = 50
snow_flakes = []


def drop_shadow(screen, font, text, color: pygame.Color, x, y):
    shadow = font.render(text, True, BLACK)
    shadow.set_alpha(color.a)
    screen.blit(shadow, (x + 2, y + 2))

    hilite = font.render(text, True, color)
    hilite.set_alpha(color.a)
    screen.blit(hilite, (x, y))


def draw_episode_number(screen):
    """Overwrite the weird episode numbers on the main_img if this is a MST3K episode"""
    epnum = sched[0]['epnum']

    # Is this a Joel or Mike ep?
    if epnum != "":
        # Who is the host?
        host_color = get_host_color(epnum)

        num = int(epnum)
        host_file = ""
        if num <= 512:
            host_file = "images/hosts/joel_header.png"
        elif 512 < num <= 1013:
            host_file = "images/hosts/mike_header.png"
        if host_file != "":
            host_img = pygame.image.load(host_file).convert_alpha()
            screen.blit(host_img, (0, 359))

        # Extend the rectangle to cover the bottom curve
        pygame.draw.rect(screen, host_color, (0, 470, 85, 45), 0, 0, 0, 0, 0, 20)

        # Draw the experiment number
        FONT.set_bold(True)
        text = FONT.render(epnum, True, (252, 252, 252), host_color)
        xpos = (85 - text.get_size()[0]) // 2
        screen.blit(text, (xpos, 470))
        FONT.set_bold(False)

    # elif sched[0]['title'].lower().startswith("rifftrax"):
    #     host_img = pygame.transform.smoothscale_by(pygame.image.load('images/hosts/RiffTrax.png'), 0.1).convert_alpha()
    #     screen.blit(host_img, (0, 359))
    # elif sched[0]['title'].lower().startswith("ct"):
    #     host_img = pygame.transform.smoothscale_by(pygame.image.load('images/hosts/Cinematic_Titanic.png'), 0.4).convert_alpha()
    #     screen.blit(host_img, (0, 359))
    # elif sched[0]['title'].lower().startswith("fc"):
    #     host_img = pygame.transform.smoothscale_by(pygame.image.load('images/hosts/film_crew.png'), 1.0).convert_alpha()
    #     screen.blit(host_img, (0, 359))


def draw_image(screen):
    global main_img

    bg = pygame.Rect(0, 0, WIDTH_HALF, HEIGHT_HALF)
    rect_gradient_h(screen, DK_GRAY, BLACK, bg)

    if main_img is not None:
        new_w = WIDTH_HALF / main_img.get_width()
        new_h = HEIGHT_HALF / main_img.get_height()
        img_scaled = pygame.transform.smoothscale_by(main_img, min(new_w, new_h))
        screen.blit(img_scaled, ((WIDTH_HALF - img_scaled.get_width()) // 2, 0))

        draw_episode_number(screen)


def draw_year(screen):
    global main_year

    if main_year != "":
        drop_shadow(screen, FONT_SM, "(" + main_year + ")", GRAY, WIDTH_HALF - 72, HEIGHT_HALF - 30)


def draw_summary(screen):
    """Split the long 'about' string into several pieces and render them."""

    bg = pygame.Rect(WIDTH_HALF, 0, WIDTH_HALF, HEIGHT_HALF)
    rect_gradient_h(screen, DK_GRAY, BLACK, bg)

    parts = main_summary.split("\n")
    for i, p in enumerate(parts):
        drop_shadow(screen, FONT, p, WHITE, WIDTH_HALF + 30, ((FONT_SIZE + 10) * i) + 14)


def draw_schedule_header(screen):
    """This is the schedule header that doesn't scroll"""

    y = HEIGHT_HALF
    pygame.draw.rect(screen, WHITE, pygame.Rect(0, y, WIDTH, SCHED_H))

    bg = pygame.Rect(2, y + 2, WIDTH - 3, SCHED_H - 4)
    rect_gradient_h(screen, COLOR_SCHEME[2], COLOR_SCHEME[0], bg)

    alpha_step = 2
    tick = int(timer_tick) % 60
    if tick < 2:
        # FADE IN: Playing
        if header_color.a + alpha_step <= 255:
            header_color.a += alpha_step
        if title_color.a + alpha_step <= 255:
            title_color.a += alpha_step
        display_index = 0
    elif tick < 28:
        # DISPLAY: Playing
        header_color.a = 255
        title_color.a = 255
        display_index = 0
    elif tick < 30:
        # FADE OUT: Playing
        if header_color.a - alpha_step >= 0:
            header_color.a -= alpha_step
        if title_color.a - alpha_step >= 0:
            title_color.a -= alpha_step
        display_index = 0
    elif tick < 32:
        # FADE IN: Next
        if header_color.a + alpha_step <= 255:
            header_color.a += alpha_step
        if title_color.a + alpha_step <= 255:
            title_color.a += alpha_step
        display_index = 1
    elif tick < 58:
        # DISPLAY: Next
        header_color.a = 255
        title_color.a = 255
        display_index = 1
    else:
        # FADE OUT: Next
        if header_color.a - alpha_step >= 0:
            header_color.a -= alpha_step
        if title_color.a - alpha_step >= 0:
            title_color.a -= alpha_step
        display_index = 1

    leading_word = "Playing:" if display_index == 0 else "Up Next:"
    drop_shadow(screen, FONT, leading_word, header_color, SCHED_COL3_X, y + FONT_PAD)
    drop_shadow(screen, FONT, update_title(sched[display_index]['title'], sched[display_index]['epnum']),
                title_color, SCHED_COL3_X + 136, y + FONT_PAD)

    # How much time until next episode?
    if leading_word == "Up Next:":
        txt = FONT.render(time_until, True, header_color)
        drop_shadow(screen, FONT, time_until, header_color, screen.get_width() - txt.get_width() - 30, y + FONT_PAD)


def draw_scrolling_header(screen):
    """The scrolling header is part of the scrolling list of titles"""

    global hdr_y
    hdr_y -= 1
    if hdr_y < HEIGHT_HALF:
        # Move this item to the end of the list
        hdr_y += int((len(sched) + 1) * SCHED_H)

    pygame.draw.rect(screen, WHITE, pygame.Rect(0, hdr_y, WIDTH, SCHED_H))
    rect_gradient_h(screen, COLOR_SCHEME[2], COLOR_SCHEME[0], pygame.Rect(2, hdr_y + 2, WIDTH - 3, SCHED_H - 3))

    date_now = datetime.now()
    ptz = date_now.astimezone(PAC_TZ)
    etz = date_now.astimezone(EST_TZ)
    drop_shadow(screen, FONT, datetime.strftime(ptz, "%Z"), YELLOW, SCHED_COL1_X, hdr_y + FONT_PAD)
    drop_shadow(screen, FONT, datetime.strftime(etz, "%Z"), YELLOW, SCHED_COL2_X, hdr_y + FONT_PAD)
    drop_shadow(screen, FONT, "Title", YELLOW, SCHED_COL3_X, hdr_y + FONT_PAD)


def split_time(time: str):
    """Separate the DOW and Time into individual columns"""
    parts = time.split(" ")
    dow = parts[0]
    merid = parts[2]

    parts2 = parts[1].split(":")
    hour = parts2[0]
    mins = parts2[1]

    return dow, hour, mins, merid


def draw_schedule_item(screen, obj, y):
    if y < HEIGHT_HALF:
        # Move this item to the end of the list
        y += int((len(sched) + 1) * SCHED_H)

    pygame.draw.rect(screen, WHITE, pygame.Rect(0, y, WIDTH, SCHED_H))
    pygame.draw.rect(screen, COLOR_SCHEME[1], pygame.Rect(2, y + 2, WIDTH - 3, SCHED_H - 3))

    title_display = update_title(obj['title'], obj['epnum'])

    dow1, hour1, min1, merid1 = split_time(obj['time'])
    dow2, hour2, min2, merid2 = split_time(obj['time_est'])

    h1 = FONT.render(hour1, True, WHITE)
    h2 = FONT.render(hour2, True, WHITE)

    drop_shadow(screen, FONT, dow1, WHITE, SCHED_COL1_X, y + FONT_PAD)
    drop_shadow(screen, FONT, hour1 + ":", WHITE, SCHED_COL1_X + DOW_W + HOUR_W + 26 - h1.get_width(), y + FONT_PAD)
    drop_shadow(screen, FONT, min1, WHITE, SCHED_COL1_X + DOW_W + HOUR_W + MIN_W, y + FONT_PAD)
    drop_shadow(screen, FONT, merid1, WHITE, SCHED_COL1_X + DOW_W + HOUR_W + MIN_W + MERID_W, y + FONT_PAD)

    drop_shadow(screen, FONT, dow2, WHITE, SCHED_COL2_X, y + FONT_PAD)
    drop_shadow(screen, FONT, hour2 + ":", WHITE, SCHED_COL2_X + DOW_W + HOUR_W + 26 - h2.get_width(), y + FONT_PAD)
    drop_shadow(screen, FONT, min2, WHITE, SCHED_COL2_X + DOW_W + HOUR_W + MIN_W, y + FONT_PAD)
    drop_shadow(screen, FONT, merid2, WHITE, SCHED_COL2_X + DOW_W + HOUR_W + MIN_W + MERID_W, y + FONT_PAD)

    drop_shadow(screen, FONT, title_display, WHITE, SCHED_COL3_X, y + FONT_PAD)

    obj['y'] = y


def draw_schedule_items(screen, y):
    for s in sched:
        draw_schedule_item(screen, s, y)
        y += SCHED_H


def move_schedule(screen):
    for s in sched:
        draw_schedule_item(screen, s, s['y'] - 1)
    draw_scrolling_header(screen)


def draw_clock(screen):
    global sched, hdr_y, is_reloading

    right_now = datetime.now()

    pac = right_now.astimezone(PAC_TZ)
    pac_time = datetime.strftime(pac, CLOCK_FORMAT).lstrip("0")
    pac_pos = pac_time.find(" ")
    drop_shadow(screen, FONT, pac_time[:pac_pos], YELLOW, SCHED_COL1_X, HEIGHT_HALF + FONT_PAD)
    drop_shadow(screen, FONT_SM, pac_time[pac_pos + 1:], YELLOW, SCHED_COL1_X + 165, HEIGHT_HALF + FONT_PAD)

    curr = right_now.astimezone(EST_TZ)
    curr_time = datetime.strftime(curr, CLOCK_FORMAT).lstrip("0")
    curr_pos = curr_time.find(" ")
    drop_shadow(screen, FONT, curr_time[:curr_pos], YELLOW, SCHED_COL2_X, HEIGHT_HALF + FONT_PAD)
    drop_shadow(screen, FONT_SM, curr_time[curr_pos + 1:], YELLOW, SCHED_COL2_X + 165, HEIGHT_HALF + FONT_PAD)

    # Is it time to reload the schedule?
    time_parts = sched[1]['time_est'].split(" ")
    update_times = [time_parts[1] + ":00 " + time_parts[2]]
    curr_time = curr_time.rstrip(" EST").rstrip(" EDT")  # Remove the timezone
    if curr_time in update_times and not is_reloading:
        print("calling setup")
        setup(screen)


def draw_vertical_separators(screen):
    pygame.draw.rect(screen, WHITE, pygame.Rect(SCHED_COL2_X - 30, HEIGHT_HALF, 2, HEIGHT_HALF))
    pygame.draw.rect(screen, WHITE, pygame.Rect(SCHED_COL3_X - 30, HEIGHT_HALF, 2, HEIGHT_HALF))


def draw_loading(screen):
    screen.fill(BLACK)
    rn = random.randint(1, 2)
    if rn == 1:
        img = pygame.image.load('images/fun/seven_years_later.png').convert_alpha()
        screen.blit(img, ((WIDTH - img.get_width()) // 2, (HEIGHT - img.get_height()) // 2))
        screen.blit(TXT_LOADING, (100, HEIGHT - 100))
        pygame.display.flip()
    elif rn == 2:
        img = pygame.image.load('images/fun/turn_lights_down.png').convert_alpha()
        screen.blit(img, (0, 0))
        pygame.display.flip()


def setup(screen):
    global hdr_y, is_reloading, main_img, main_summary, main_year, sched

    draw_loading(screen)

    is_reloading = True
    start_time = datetime.now()

    try:
        summaries.update()
    except urllib.error.URLError:
        print("Error downloading summaries file. Using the existing file.")

    try:
        schedule.update()
    except urllib.error.URLError:
        print("Error downloading schedule file. Using the existing file.")

    sched = schedule.get_schedule(schedule.US_PAC, NUM_SCHEDULE)
    now = datetime.now()
    next_start = datetime.strptime(sched[1]['datetime_est'], "%a, %b %d %I:%M%p %Y")
    # If necessary, keep popping the schedule until we catch up to the current time
    while next_start < now:
        next_start = datetime.strptime(sched[1]['datetime_est'], "%a, %b %d %I:%M%p %Y")
        sched.pop(0)

    stop_time = datetime.now()
    print("Loading finished in " + str(stop_time - start_time))

    img_path = sched[0]['image']
    if img_path != "":
        img_path = 'images/movies/' + img_path
        if os.path.exists(img_path):
            main_img = pygame.image.load(img_path).convert()
        else:
            main_img = pygame.image.load('images/movies/mst3k.png').convert()
    else:
        main_img = pygame.image.load('images/movies/mst3k.png').convert()

    main_summary = wrap_text(prepare_summary(sched[0]['about'])).strip()
    main_year = sched[0]['year']

    draw_schedule_items(screen, HEIGHT_HALF + SCHED_H)
    hdr_y = HEIGHT_HALF + (len(sched) + 1) * SCHED_H
    is_reloading = False


def snow(screen):
    global snow_flakes

    for flake in snow_flakes:
        flake.animate()
        if flake.anim_step == 0:
            if DATE_YYYY == VALENTINES_DAY or sched[0]['epnum'] == '501':
                snow_flakes.append(CandyHeartSnow(screen))
            elif DATE_YYYY == ST_PATRICKS_DAY:
                snow_flakes.append(CloverSnow(screen))
            else:
                snow_flakes.append(SnowFlake(screen))

    # Keep any snowflakes that are still falling
    temp_objs = []
    for flake in snow_flakes:
        if flake.anim_step > 0:
            temp_objs.append(flake)

    snow_flakes = temp_objs


def draw_urls(screen):
    drop_shadow(screen, FONT_XS, STR_TWITCH, WHITE, WIDTH - 130, HEIGHT_HALF - 50)
    drop_shadow(screen, FONT_XS, STR_GIZMO, WHITE, WIDTH - 130, HEIGHT_HALF - 30)


def main_loop(screen):
    """This is called from TriviaVox now."""
    """
    global running, dt, timer_tick, is_loading_fun, fun_objs

    # while running:
    if running:
        screen.fill(BLACK)

        draw_image(screen)
        draw_year(screen)
        # draw_summary()
        # draw_gizmoplex()
        fun()

        # Snowy movies: 321=Santa vs Martians, 422=Day Earth Froze, 521=Santa Claus,
        # 813=Jack Frost, 1104=Avalanche, 1113=Xmas That Almost Wasn't
        if sched[0]['epnum'] in ['321', '422', '521', '813', '1104', '1113']:
            if len(snow_flakes) == 0:
                for _ in range(NUM_SNOWFLAKES):
                    snow_flakes.append(SnowFlake(screen))
            snow(screen)
        else:
            snow_flakes.clear()

        move_schedule(screen)
        draw_schedule_header(screen)
        draw_vertical_separators(screen)
        draw_clock(screen)

        # Time for fun?
        # random_fun = random.randrange(1, 5)  # 20% chance of fun every minute
        random_fun = 1
        if int(timer_tick) % 60 == 0 and random_fun == 1 and not is_loading_fun:
            is_loading_fun = True
            fun_objs = funfactory.get(screen, sched[0]['title'], sched[0]['epnum'])

        if int(timer_tick) % 64 == 0:
            is_loading_fun = False

        if len(fun_objs) > 0 and not is_loading_fun:
            temp_objs = []
            for obj in fun_objs:
                if obj.anim_step > 0:
                    temp_objs.append(obj)
            fun_objs = temp_objs

        # pygame.QUIT event means the user clicked X to close your window
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         running = False

        # flip() the display to put your work on screen
        # pygame.display.flip()

        # limits FPS to 60 - dt is delta time in seconds since last frame.
        # dt = clock.tick(60) / 1000

        # timer_tick += dt
        # if timer_tick >= 7200:  # Reset every two hours
        #     timer_tick = 0
    """
    pass


if __name__ == '__main__':
    scr = pygame.display.set_mode((WIDTH, HEIGHT))
    clk = pygame.time.Clock()

    # is_running = True
    # lo = LightsOff(scr)
    #
    # while is_running:
    #     lo.animate()
    #     pygame.display.flip()
    #
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             is_running = False
    #
    # pygame.quit()

    # summaries.refresh()
    # setup(scr)
    # main_loop()
