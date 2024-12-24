import os.path
import random
from datetime import datetime

import pygame
from pygame import Surface

import funfactory
import schedule
import summaries
from ball import Ball
from gradient import rect_gradient_h
from schedule import PAC_TZ, EST_TZ
from snow import SnowFlake
from util_text import *

pygame.init()

# Constants
DEBUG = False

WIDTH = 1920
HEIGHT = 1080

WIDTH_HALF = int(WIDTH / 2)
HEIGHT_HALF = int(HEIGHT / 2)

# Dimensions of the schedule bars
SCHED_H = 60
SCHED_COL1_X = 30
SCHED_COL2_X = 320
SCHED_COL3_X = 610
DOW_W = 80

# Create fonts
# FONT_FACE = "arial"
FONT_FACE_SIM = "fonts/SimianText_Orangutan.otf"
FONT_SIZE = 36
FONT = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE)

FONT_SIZE_EXTRA_SMALL = 18
FONT_XS = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE_EXTRA_SMALL)

FONT_SIZE_SMALL = 26
FONT_SM = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE_SMALL)

FONT_SIZE_LARGE = 40
FONT_LG = pygame.font.Font(FONT_FACE_SIM, FONT_SIZE_LARGE)

FONT_PAD = 10  # vertical font spacing

# Colors
BLACK = pygame.Color(0, 0, 0)
BLUE = pygame.Color(0, 0, 120)
LTBLUE = pygame.Color(0, 0, 200)
PALEBLUE = pygame.Color(0, 80, 220)
YELLOW = pygame.Color(192, 192, 0)
WHITE = pygame.Color(192, 192, 192)
DK_GRAY = pygame.Color(32, 32, 32)
GRAY = pygame.Color(128, 128, 128)

NUM_SCHEDULE = 20  # Number of schedule items to load

CLOCK_FORMAT = "%I:%M:%S %p %Z"

# Globals
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
dt = 0
sched = []
hdr_y = 0
timer_tick = 0  # start it at 1 so we don't trigger 'fun' immediately
is_reloading = False
is_loading_fun = False
main_img = pygame.Surface((WIDTH, HEIGHT))
main_summary = ""
fun_objs = []

NUM_SNOWFLAKES = 200
snow_flakes = []
for _ in range(NUM_SNOWFLAKES):
    snow_flakes.append(SnowFlake(screen))

# game variables
wall_thickness = 10
gravity = 0.5
bounce_stop = 0.3
# track positions of mouse to get movement vector
mouse_trajectory = []


def drop_shadow(font, text, color, x, y):
    screen.blit(font.render(text, True, BLACK), (x + 2, y + 2))
    screen.blit(font.render(text, True, color), (x, y))


def draw_image():
    global main_img

    bg = pygame.Rect(0, 0, WIDTH_HALF, HEIGHT_HALF)
    rect_gradient_h(screen, BLACK, DK_GRAY, bg)

    if main_img is not None:
        new_w = WIDTH_HALF / main_img.get_width()
        new_h = HEIGHT_HALF / main_img.get_height()
        img_scaled = pygame.transform.smoothscale_by(main_img, min(new_w, new_h))
        screen.blit(img_scaled, ((WIDTH_HALF - img_scaled.get_width()) / 2, 0))


def draw_summary():
    """Split the long 'about' string into several pieces and render them."""

    bg = pygame.Rect(WIDTH_HALF, 0, WIDTH_HALF, HEIGHT_HALF)
    rect_gradient_h(screen, BLACK, DK_GRAY, bg)

    parts = main_summary.split("\n")
    for i, p in enumerate(parts):
        drop_shadow(FONT, p, WHITE, WIDTH_HALF + 30, ((FONT_SIZE + 10) * i) + 14)


def draw_schedule_header():
    """This is the schedule header that doesn't scroll"""

    y = HEIGHT_HALF
    pygame.draw.rect(screen, WHITE, pygame.Rect(0, y, WIDTH, SCHED_H))

    bg = pygame.Rect(2, y + 2, WIDTH - 3, SCHED_H - 4)
    rect_gradient_h(screen, LTBLUE, BLUE, bg)

    drop_shadow(FONT, "Playing:", YELLOW, SCHED_COL3_X, y + FONT_PAD)
    drop_shadow(FONT, update_title(sched[0]['title'], sched[0]['epnum']), WHITE, SCHED_COL3_X + 128, y + FONT_PAD)


def draw_scrolling_header():
    """The scrolling header is part of the scrolling list of titles"""

    global hdr_y
    hdr_y -= 1
    if hdr_y < HEIGHT_HALF:
        # Move this item to the end of the list
        hdr_y += int((len(sched) + 1) * SCHED_H)

    pygame.draw.rect(screen, WHITE, pygame.Rect(0, hdr_y, WIDTH, SCHED_H))
    rect_gradient_h(screen, LTBLUE, BLUE, pygame.Rect(2, hdr_y + 2, WIDTH - 3, SCHED_H - 3))

    date_now = datetime.now()
    ptz = date_now.astimezone(PAC_TZ)
    etz = date_now.astimezone(EST_TZ)
    drop_shadow(FONT, datetime.strftime(ptz, "%Z"), YELLOW, SCHED_COL1_X, hdr_y + FONT_PAD)
    drop_shadow(FONT, datetime.strftime(etz, "%Z"), YELLOW, SCHED_COL2_X, hdr_y + FONT_PAD)
    drop_shadow(FONT, "Title", YELLOW, SCHED_COL3_X, hdr_y + FONT_PAD)


def split_time(time: str):
    """Separate the DOW and Time into individual columns"""
    pos = time.find(" ")
    dow = time[:pos]
    t = time[pos + 1:]

    if len(t) == 7:
        t = "  " + t

    return dow, t


def draw_schedule_item(obj, y):
    if y < HEIGHT_HALF:
        # Move this item to the end of the list
        y += int((len(sched) + 1) * SCHED_H)

    pygame.draw.rect(screen, WHITE, pygame.Rect(0, y, WIDTH, SCHED_H))
    rect_gradient_h(screen, PALEBLUE, LTBLUE, pygame.Rect(2, y + 2, WIDTH - 3, SCHED_H - 3))

    title_display = update_title(obj['title'], obj['epnum'])

    dow1, time1 = split_time(obj['time'])
    dow2, time2 = split_time(obj['time_est'])

    drop_shadow(FONT, dow1, WHITE, SCHED_COL1_X, y + FONT_PAD)
    drop_shadow(FONT, time1, WHITE, SCHED_COL1_X + DOW_W, y + FONT_PAD)

    drop_shadow(FONT, dow2, WHITE, SCHED_COL2_X, y + FONT_PAD)
    drop_shadow(FONT, time2, WHITE, SCHED_COL2_X + DOW_W, y + FONT_PAD)

    drop_shadow(FONT, title_display, WHITE, SCHED_COL3_X, y + FONT_PAD)

    obj['y'] = y


def draw_schedule_items(y):
    for s in sched:
        draw_schedule_item(s, y)
        y += SCHED_H


def move_schedule():
    for s in sched:
        draw_schedule_item(s, s['y'] - 1)
    draw_scrolling_header()


def draw_clock():
    global sched, hdr_y, is_reloading

    right_now = datetime.now()

    pac = right_now.astimezone(PAC_TZ)
    pac_time = datetime.strftime(pac, CLOCK_FORMAT).lstrip("0")
    pac_pos = pac_time.find(" ")
    drop_shadow(FONT, pac_time[:pac_pos], YELLOW, SCHED_COL1_X, HEIGHT_HALF + FONT_PAD)
    drop_shadow(FONT_SM, pac_time[pac_pos + 1:], YELLOW, SCHED_COL1_X + 160, HEIGHT_HALF + FONT_PAD)

    curr = right_now.astimezone(EST_TZ)
    curr_time = datetime.strftime(curr, CLOCK_FORMAT).lstrip("0")
    curr_pos = curr_time.find(" ")
    drop_shadow(FONT, curr_time[:curr_pos], YELLOW, SCHED_COL2_X, HEIGHT_HALF + FONT_PAD)
    drop_shadow(FONT_SM, curr_time[curr_pos + 1:], YELLOW, SCHED_COL2_X + 160, HEIGHT_HALF + FONT_PAD)

    # Is it time to reload the schedule?
    time_parts = sched[1]['time_est'].split(" ")
    update_time = time_parts[1] + ":00 " + time_parts[2]
    curr_time = curr_time.rstrip(" EST").rstrip(" EDT")  # Remove the timezone
    # print(curr_time + " | " + update_time + " | is_reloading: " + str(is_reloading))
    if curr_time == update_time and not is_reloading:
        setup()


def draw_vertical_separators():
    pygame.draw.rect(screen, WHITE, pygame.Rect(SCHED_COL2_X - 30, HEIGHT_HALF, 2, HEIGHT_HALF))
    pygame.draw.rect(screen, WHITE, pygame.Rect(SCHED_COL3_X - 30, HEIGHT_HALF, 2, HEIGHT_HALF))


def setup():
    global hdr_y, is_reloading, main_img, main_summary, sched

    is_reloading = True
    start_time = datetime.now()
    schedule.refresh()
    sched = schedule.get_schedule(schedule.US_PAC, NUM_SCHEDULE)
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
    if sched[0]['year'] != "":
        main_summary += " [" + sched[0]['year'] + "]"

    draw_schedule_items(HEIGHT_HALF + SCHED_H)
    hdr_y = HEIGHT_HALF + (len(sched) + 1) * SCHED_H
    is_reloading = False


def fun():
    if len(fun_objs) > 0:
        for o in fun_objs:
            o.animate()


def snow():
    global snow_flakes

    for flake in snow_flakes:
        flake.animate()
        if flake.anim_step == 0:
            snow_flakes.append(SnowFlake(screen))

    # Remove and snowflakes that are finished falling
    temp_objs = []
    for flake in snow_flakes:
        if flake.anim_step > 0:
            temp_objs.append(flake)

    snow_flakes = temp_objs


def draw_gizmoplex():
    drop_shadow(FONT_XS, "twitch.tv/mst3k", GRAY, WIDTH - 140, HEIGHT_HALF - 50)
    drop_shadow(FONT_XS, "gizmoplex.com", GRAY, WIDTH - 140, HEIGHT_HALF - 30)


def draw_walls():
    left = pygame.draw.line(screen, 'white', (0, 0), (0, HEIGHT), wall_thickness)
    right = pygame.draw.line(screen, 'white', (WIDTH, 0), (WIDTH, HEIGHT), wall_thickness)
    top = pygame.draw.line(screen, 'white', (0, 0), (WIDTH, 0), wall_thickness)
    bottom = pygame.draw.line(screen, 'white', (0, HEIGHT), (WIDTH, HEIGHT), wall_thickness)
    wall_list = [left, right, top, bottom]
    return wall_list


def calc_motion_vector():
    x_speed = 0
    y_speed = 0
    if len(mouse_trajectory) > 10:
        x_speed = (mouse_trajectory[-1][0] - mouse_trajectory[0][0]) / len(mouse_trajectory)
        y_speed = (mouse_trajectory[-1][1] - mouse_trajectory[0][1]) / len(mouse_trajectory)
    return x_speed, y_speed


ball1 = Ball(screen, 50, 50, 30, 'blue', 100, .75, 0, 0, 1, 0.02)
ball2 = Ball(screen, 500, 50, 50, 'green', 300, .9, 0, 0, 2, 0.03)
ball3 = Ball(screen, 200, 50, 40, 'purple', 200, .8, 0, 0, 3, 0.04)
ball4 = Ball(screen, 700, 50, 60, 'red', 500, .7, 0, 0, 4, .1)
balls = [ball1, ball2, ball3, ball4]

rot = 0
rot_speed = 2

image_orig = pygame.Surface((100 , 100))
# for making transparent background while rotating an image
image_orig.set_colorkey(BLACK)
# fill the rectangle / surface with color
image_orig.fill(YELLOW)
# creating a copy of orignal image for smooth rotation
image = image_orig.copy()
image.set_colorkey(BLACK)
# define rect for placing the rectangle at the desired position
rect = image.get_rect()
rect.center = (WIDTH // 2, HEIGHT // 2)


if __name__ == '__main__':
    summaries.refresh()
    setup()

    while running:
        screen.fill(BLACK)

        draw_image()
        draw_summary()
        draw_gizmoplex()
        fun()
        snow()
        move_schedule()
        draw_schedule_header()
        draw_vertical_separators()
        draw_clock()

        # Time for fun?
        random_fun = random.randrange(1, 5)  # 20% chance of fun every minute
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

        """
        # making a copy of the old center of the rectangle
        old_center = rect.center
        # defining angle of the rotation
        rot = (rot + rot_speed) % 360
        # rotating the orignal image
        new_image = pygame.transform.rotate(image_orig, rot)
        rect = new_image.get_rect()
        # set the rotated rectangle to the old center
        rect.center = old_center
        # drawing the rotated rectangle to the screen
        screen.blit(new_image, rect)
        """

        # Handle balls
        # mouse_coords = pygame.mouse.get_pos()
        # mouse_trajectory.append(mouse_coords)
        # if len(mouse_trajectory) > 20:
        #     mouse_trajectory.pop(0)
        # x_push, y_push = calc_motion_vector()

        # walls = draw_walls()
        # for ball in balls:
        #     ball.draw()
        #     ball.update_pos(mouse_coords)
        #     ball.y_speed = ball.check_collisions(balls, x_push, y_push)

        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     if event.button == 1:
            #         if ball1.check_select(event.pos) or ball2.check_select(event.pos) \
            #                 or ball3.check_select(event.pos) or ball4.check_select(event.pos):
            #             active_select = True
            # if event.type == pygame.MOUSEBUTTONUP:
            #     if event.button == 1:
            #         active_select = False
            #         for i in range(len(balls)):
            #             balls[i].check_select((-1000, -1000))

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60 - dt is delta time in seconds since last frame.
        dt = clock.tick(60) / 1000

        timer_tick += dt
        if timer_tick >= 7200:  # Reset every two hours
            timer_tick = 0

    pygame.quit()
