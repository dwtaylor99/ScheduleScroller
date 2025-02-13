import pygame

pygame.init()

DEBUG = True

WIDTH = 1200
HEIGHT = 800

FPS = 60
FPS_FRACTION = 1 / (FPS / 2)
UPDATE_RATE = 1 / 720

BG_COLOR = (1, 0, 68)  # PALE_BLUE
BG_UI = (80, 80, 80, 128)

BUMPER_COLOR = (20, 128, 30)
BUMPER_OUTLINE = (10, 118, 10)

BALL_RADIUS = 5
PEG_RADIUS = 8

PEG_BOUNCE = 2.0
BUMPER_BOUNCE = 4.0
MAX_VELOCITY = 60.0

GRAVITY = 1.0  # 1.00
DENSITY = 1.22  # 1.22
DRAG = 0.47  # 0.47

AG = 9.81
AG_MULT_GRAV = AG * GRAVITY
DRAG_CALC = -0.5 * DRAG * DENSITY

POWERUP_SPEED = 1  # Type of PowerUp
SECONDS_BETWEEN_GAMES = 10
MIN_NUM_BALLS = 5

IMG_SCALE = 0.0625

