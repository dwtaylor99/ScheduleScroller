import math
import random
import sys
import time

from twitchio import Message
from twitchio.ext import commands, routines

import botsecrets
from ball_objects import Ball, Player, Bumper, PowerUp
from constants import *
from levels import Level, LevelTest1, LevelTest2, LevelTest3
from persist import create_file_if_missing, get_points, save_add_points
from utils import drop_shadow

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
is_running = True
dt = 0

camera_move_y = HEIGHT // 2  # The y-coordinate that causes the camera to move down
camera_y = 0  # How far the camera has moved

level = Level
is_gameover = False
next_game_time = 0

# excluded_players = ["movievox", "leftfourdave"]  # Use all lowercase
excluded_players = ["movievox"]  # Use all lowercase
cpus = ["CPU1", "CPU2", "CPU3", "CPU4", "CPU5"]

balls: [Ball] = []
bumpers: [Bumper] = []
powerups: [PowerUp] = []
players: [Player] = []

CHANNEL_ID = 105623158
CHANNEL_NAME = "mst3k"


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=botsecrets.OAUTH_TOKEN, initial_channels=['mst3k'], prefix="!")
        self.stream = None
        self.channel = super().get_channel(CHANNEL_NAME)

    async def event_ready(self):
        global is_gameover, is_running, next_game_time, balls

        print("Ready.")
        await self.find_channel_handle()

        is_running = True
        is_gameover = True
        next_game_time = time.time() + SECONDS_BETWEEN_GAMES
        balls.clear()
        bumpers.clear()
        powerups.clear()
        players.clear()

        self.auto_update_game.start()

    async def find_channel_handle(self):
        # Save a handle to the Channel
        self.channel = super().get_channel(CHANNEL_NAME)
        streams = await self.fetch_streams(user_ids=[CHANNEL_ID])
        if streams:
            self.stream = streams.pop()
        else:
            print("No channel found!")
            pygame.quit()
            sys.exit()

    async def bot_print(self, txt):
        print(txt)
        if not DEBUG:
            await self.channel.send(txt)

    async def event_message(self, message: Message) -> None:
        if message.echo:
            return

        add_player(message.author.display_name, message.author.color)
        await self.handle_commands(message)

    async def event_command_error(self, ctx: commands.Context, error):
        pass

    @routines.routine(seconds=UPDATE_RATE)
    async def auto_update_game(self):
        update_game()

    @commands.command(name="play", aliases=['Play', 'PLAY'])
    async def cmd_play(self, ctx: commands.Context):
        add_player(ctx.author.display_name, ctx.author.color)


def add_player(username, hex_color):
    global players

    if username.lower() in excluded_players:
        return

    found = False
    for player in players:
        if player.username == username:
            found = True
            break

    if not found:
        players.append(Player(username, hex_to_rgb(hex_color), 0))


def calculate_ui_width():
    # calculate the width of the name to find the longest name
    w = 0
    for ball in balls + players:
        txt = FONT_MD.render("99. " + ball.username, True, ball.color)
        if txt.get_width() > w:
            w = txt.get_width()  # add padding to the UI width

    if w < 80:
        w = 80

    w += 30
    return w


def hex_to_rgb(hex_color):
    """Converts a hex color code to RGB values."""
    if hex_color == "":
        return (random.randrange(0, 255),
                random.randrange(0, 255),
                random.randrange(0, 255))

    # Remove the '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert the hex values to integers
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return r, g, b


def find_lowest() -> Ball:
    lowest_ball = None

    lowest_y = 0
    for ball in balls:
        if not ball.hit and ball.y > lowest_y:
            lowest_y = ball.y
            lowest_ball = ball

    return lowest_ball


def collision_wall(ball: Ball):
    if ball.x > WIDTH - ball.radius:
        ball.vel_x *= ball.e
        ball.x = WIDTH - ball.radius

    if ball.x < ball.radius:
        ball.vel_x *= ball.e
        ball.x = ball.radius

    if ball.y > level.height:
        ball.hit = True  # signals the ball is out of play

        # figure out which place the ball is in
        place = 0
        for b in balls:
            if b.hit:
                place += 1
        ball.place = place


def collision_bumpers(b1: Ball):
    for i in range(len(bumpers)):
        b2: Ball = bumpers[i]

        if b1.x != b2.x and b1.y != b2.y:
            if b1.x + b1.radius + b2.radius > b2.x and b1.x < b2.x + b1.radius + b2.radius and b1.y + b1.radius + b2.radius > b2.y and b1.y < b2.y + b1.radius + b2.radius:
                distx = b1.x - b2.x
                disty = b1.y - b2.y
                d = math.sqrt(distx * distx + disty * disty)

                if d < b1.radius + b2.radius:
                    nx = (b2.x - b1.x) / d
                    ny = (b2.y - b1.y) / d
                    p = 2 * (b1.vel_x * nx + b1.vel_y * ny - b2.vel_x * nx - b2.vel_y * ny) / (b1.mass + b2.mass)

                    # calculating the point of collision
                    colpoint_x = ((b1.x * b2.radius) + (b2.x * b1.radius)) / (b1.radius + b2.radius)
                    colpoint_y = ((b1.y * b2.radius) + (b2.y * b1.radius)) / (b1.radius + b2.radius)

                    # stopping overlap
                    b1.x = colpoint_x + b1.radius * (b1.x - b2.x) / d
                    b1.y = colpoint_y + b1.radius * (b1.y - b2.y) / d

                    # updating velocity to reflect collision
                    b1.vel_x -= p * b1.mass * nx * BUMPER_BOUNCE
                    b1.vel_y -= p * b1.mass * ny * BUMPER_BOUNCE

                    b1.vel_x = -MAX_VELOCITY if b1.vel_x < -MAX_VELOCITY else b1.vel_x
                    b1.vel_x = MAX_VELOCITY if b1.vel_x > MAX_VELOCITY else b1.vel_x
                    b1.vel_y = -MAX_VELOCITY if b1.vel_y < -MAX_VELOCITY else b1.vel_y
                    b1.vel_y = MAX_VELOCITY if b1.vel_y > MAX_VELOCITY else b1.vel_y


def collision_ball(b1: Ball):
    for i in range(len(balls)):
        b2: Ball = balls[i]
        if b1.x != b2.x and b1.y != b2.y:
            if b1.x + b1.radius + b2.radius > b2.x and b1.x < b2.x + b1.radius + b2.radius and b1.y + b1.radius + b2.radius > b2.y and b1.y < b2.y + b1.radius + b2.radius:
                distx = b1.x - b2.x
                disty = b1.y - b2.y
                d = math.sqrt(distx * distx + disty * disty)

                if d < b1.radius + b2.radius:
                    nx = (b2.x - b1.x) / d
                    ny = (b2.y - b1.y) / d
                    p = 2 * (b1.vel_x * nx + b1.vel_y * ny - b2.vel_x * nx - b2.vel_y * ny) / (b1.mass + b2.mass)

                    colpoint_x = ((b1.x * b2.radius) + (b2.x * b1.radius)) / (b1.radius + b2.radius)
                    colpoint_y = ((b1.y * b2.radius) + (b2.y * b1.radius)) / (b1.radius + b2.radius)

                    # stopping overlap
                    b1.x = colpoint_x + b1.radius * (b1.x - b2.x) / d
                    b1.y = colpoint_y + b1.radius * (b1.y - b2.y) / d
                    b2.x = colpoint_x + b2.radius * (b2.x - b1.x) / d
                    b2.y = colpoint_y + b2.radius * (b2.y - b1.y) / d

                    # updating velocity to reflect collision
                    b1.vel_x -= p * b1.mass * nx
                    b1.vel_y -= p * b1.mass * ny
                    b2.vel_x += p * b2.mass * nx
                    b2.vel_y += p * b2.mass * ny


def draw_arrow(ball):
    pygame.draw.line(screen, ball.color, (ball.x, 5), (ball.x, 25), 3)  # center
    pygame.draw.line(screen, ball.color, (ball.x, 5), (ball.x - 5, 12), 3)  # left
    pygame.draw.line(screen, ball.color, (ball.x, 5), (ball.x + 5, 12), 3)  # right
    t = FONT_MD.render(ball.username, True, ball.color)
    drop_shadow(screen, FONT_MD, ball.username, ball.color, ball.x - t.get_width() // 2, 28)


def draw_finish_line():
    if level.height > 0:
        for i in range(0, WIDTH, 20):
            # top row checkerboard
            pygame.draw.rect(screen, WHITE, (i, level.height - camera_y, 10, 10))
            pygame.draw.rect(screen, BLACK, (i + 10, level.height - camera_y, 10, 10))
            # bottom row checkerboard
            pygame.draw.rect(screen, BLACK, (i, level.height - camera_y + 10, 10, 10))
            pygame.draw.rect(screen, WHITE, (i + 10, level.height - camera_y + 10, 10, 10))

        pygame.draw.line(screen, WHITE, (0, level.height - camera_y - 2), (WIDTH, level.height - camera_y - 2), 2)
        pygame.draw.line(screen, WHITE, (0, level.height - camera_y + 20), (WIDTH, level.height - camera_y + 20), 2)


def draw_ui():
    global balls
    ox = oy = 20

    # calculate the width of the name to find the longest name
    ui_w = calculate_ui_width()

    # UI translucent background
    total_rows = len(balls) + len(players) + 3
    bg = pygame.Surface((ui_w, total_rows * oy), pygame.SRCALPHA)
    bg.fill(BG_UI)
    screen.blit(bg, (10, 10))
    # UI border
    pygame.draw.rect(screen, DK_GRAY, (10, 10, ui_w, total_rows * oy), 2)

    # Split balls into two lists: balls that finished the race and balls that haven't
    finished = []
    incomplete = []
    for b in balls:
        if b.hit:
            finished.append(b)
        else:
            incomplete.append(b)

    # Sort the lists and recombine them
    # balls.sort(key=lambda b: b.y, reverse=True)
    finished.sort(key=lambda b1: b1.place)
    incomplete.sort(key=lambda b2: b2.y, reverse=True)
    balls = finished + incomplete

    # Display the ball names
    for i, ball in enumerate(balls):
        drop_shadow(screen, FONT_MD, str(i + 1) + ".", WHITE, ox, oy)
        drop_shadow(screen, FONT_MD, ball.username, ball.color, ox + 24, oy)
        oy += 20

    # Display the next round players
    oy += 20
    drop_shadow(screen, FONT_MD, "Next round:", WHITE, ox, oy)

    oy += 20
    for i, player in enumerate(players):
        drop_shadow(screen, FONT_MD, str(i + 1) + ".", WHITE, ox, oy)
        drop_shadow(screen, FONT_MD, player.username, player.color, ox + 24, oy)
        oy += 20

    # Display Level name
    if level.name != "":
        drop_shadow(screen, FONT_MD, "Level: " + level.name, WHITE, 10, HEIGHT - 30)


def draw_gameover():
    # UI translucent background
    bg = pygame.Surface((WIDTH - 400, HEIGHT - 300), pygame.SRCALPHA)
    bg.fill((64, 64, 64, 220))
    screen.blit(bg, (200, 150))

    if len(balls) > 0:
        # Draw first place winner
        winner = balls[0]
        t = FONT_LG.render("Winner!", True, WHITE)
        drop_shadow(screen, FONT_LG, "Winner!", WHITE, (WIDTH - t.get_width()) // 2,
                    (HEIGHT - t.get_height()) // 2 - 170, 2)

        t = FONT_XL.render(winner.username, True, winner.color)
        drop_shadow(screen, FONT_XL, winner.username, winner.color, (WIDTH - t.get_width()) // 2,
                    (HEIGHT - t.get_height()) // 2 - 110, 2)

        if len(balls) > 1:
            # Draw second place winner
            winner = balls[1]
            t = FONT_LG.render(winner.username, True, winner.color)
            drop_shadow(screen, FONT_LG, winner.username, winner.color, (WIDTH - t.get_width()) // 2,
                        (HEIGHT - t.get_height()) // 2 - 60, 2)

        if len(balls) > 2:
            # Draw third place winner
            winner = balls[2]
            t = FONT_LG.render(winner.username, True, winner.color)
            drop_shadow(screen, FONT_LG, winner.username, winner.color, (WIDTH - t.get_width()) // 2,
                        (HEIGHT - t.get_height()) // 2 - 20, 2)

    t = FONT_LG.render("New game in", True, WHITE)
    drop_shadow(screen, FONT_LG, "New game in", WHITE, (WIDTH - t.get_width()) // 2,
                (HEIGHT - t.get_height()) // 2 + 100, 2)

    time_left = str(int(next_game_time - time.time()))
    t = FONT_LG.render(time_left, True, WHITE)
    drop_shadow(screen, FONT_XL, time_left, WHITE, ((WIDTH - t.get_width()) // 2) - (t.get_width() // 4),
                (HEIGHT - t.get_height()) // 2 + 140, 2)


def draw_screen():
    global camera_y, camera_move_y, is_gameover, next_game_time

    screen.fill(BG_COLOR)

    draw_finish_line()

    for bumper in bumpers:
        bumper.move()
        bumper.draw(screen, camera_y)

    for pwrup in powerups:
        pwrup.draw(screen, camera_y)
        for ball in balls:
            if pwrup.collide(ball):
                ball.vel_x *= pwrup.boost_x
                ball.vel_y *= pwrup.boost_y
                powerups.remove(pwrup)
                break

    balls_in_play = 0
    for ball in balls:
        if not ball.hit:
            balls_in_play += 1

            ball.update()
            ball.draw(screen, camera_y)

            # If the ball is above the top of the screen, draw a pointer to it
            if ball.y - camera_y < -10:
                draw_arrow(ball)

            # Handle ball collisions
            collision_bumpers(ball)
            collision_ball(ball)
            collision_wall(ball)

    # Game is over when there is only 1 ball left in play
    if len(balls) > 3:
        is_gameover = balls_in_play <= len(balls) - 3

    # Move camera?
    lowest_ball = find_lowest()
    if lowest_ball is not None:  # and lowest_ball.y > camera_move_y:
        new_cam_y = lowest_ball.y - camera_move_y
        camera_y = new_cam_y

    # Limit camera movement
    if camera_y > camera_move_y - 100:
        camera_y = camera_move_y - 100

    draw_ui()

    if is_gameover and next_game_time == 0:
        if len(balls) > 2:
            winner1 = balls[0].username
            if winner1 not in cpus:
                print(winner1 + " wins 20 points")
                save_add_points(winner1, 20)

            winner2 = balls[1].username
            if winner2 not in cpus:
                print(winner2 + " wins 10 points")
                save_add_points(winner2, 10)

            winner3 = balls[2].username
            if winner3 not in cpus:
                print(winner3 + " wins 5 points")
                save_add_points(winner3, 5)

        next_game_time = time.time() + SECONDS_BETWEEN_GAMES  # When to start a new game


def setup():
    global camera_y, level, next_game_time, bumpers, powerups, screen, clock

    # Is it OK to do this? I want to be sure to reinit everything so memory leaks happen
    # screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # clock = pygame.time.Clock()

    camera_y = 0
    next_game_time = 0

    balls.clear()
    bumpers.clear()
    powerups.clear()

    for p in players:
        ball = Ball(random.randrange(100, WIDTH - 100), random.randrange(-50, 50), 10, p.color)
        ball.username = p.username
        balls.append(ball)

    # All players were converted to balls, so clear the player list to allow new players for the next game.
    players.clear()

    if len(balls) < MIN_NUM_BALLS:
        for i in range(MIN_NUM_BALLS - len(balls)):
            cpu_r = random.randrange(0, 255)
            cpu_g = random.randrange(0, 255)
            cpu_b = random.randrange(0, 255)
            ball = Ball(random.randrange(100, WIDTH - 100), random.randrange(-50, 50), 10,
                        (cpu_r, cpu_g, cpu_b))
            ball.username = "CPU" + str(i + 1)
            balls.append(ball)

    # Get level data
    level = random.choice([LevelTest1(), LevelTest2(), LevelTest3()])
    # level = LevelTest3()
    bumpers = level.bumpers
    powerups = level.powerups


def update_game():
    global is_gameover, is_running, dt

    if is_running:
        draw_screen()

        if is_gameover:
            draw_gameover()

            # Is it time to start a new game?
            if time.time() > next_game_time:
                setup()
                is_gameover = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        pygame.display.flip()
        dt = clock.tick()


if __name__ == '__main__':
    create_file_if_missing()

    bot = TwitchBot()
    bot.run()

    pygame.quit()

"""
TODO:
Save/Load players
"""
