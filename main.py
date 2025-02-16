import random
from enum import Enum

import pygame

from colors import WHITE, BLACK

pygame.init()
screen = pygame.display.set_mode((1920//2, 900))
clock = pygame.time.Clock()
dt = 0
is_running = True

FPS = 60

STONE = "S"
CLAY = "Y"
COPPER = "C"
IRON = "I"
SILVER = "V"
GOLD = "G"
DIAMOND = "D"

FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)


class Drop:
    name = ""
    value = 0
    img = None


class NoneDrop(Drop):
    name = "None"


class StoneDrop(Drop):
    name = "Stone"
    value = 1
    img = FONT_EMOJI_MD.render("⚫", True, WHITE)


class ClayDrop(Drop):
    name = "Clay"
    value = 2
    img = FONT_EMOJI_MD.render("🟤", True, WHITE)


class CopperDrop(Drop):
    name = "Copper"
    value = 5
    img = FONT_EMOJI_MD.render("🔶", True, WHITE)


class IronDrop(Drop):
    name = "Iron"
    value = 10
    img = FONT_EMOJI_MD.render("🔷", True, WHITE)


class SilverDrop(Drop):
    name = "Silver"
    value = 15
    img = FONT_EMOJI_MD.render("⬜", True, WHITE)


class GoldDrop(Drop):
    name = "Gold"
    value = 25
    img = FONT_EMOJI_MD.render("🟨", True, WHITE)


class DiamondDrop(Drop):
    name = "Diamond"
    value = 40
    img = FONT_EMOJI_MD.render("💎", True, WHITE)


class Drops(Enum):
    NONE = NoneDrop()
    CLAY = ClayDrop()
    STONE = StoneDrop()
    COPPER = CopperDrop()
    IRON = IronDrop()
    SILVER = SilverDrop()
    GOLD = GoldDrop()
    DIAMOND = DiamondDrop()


TILE_W = TILE_H = 40
TILE_SCALE = 0.29
IMG_DIRT = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/brown_dirt.png"), TILE_SCALE).convert()
IMG_STONE = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/gray_wall.png"), TILE_SCALE).convert()
IMG_CLAY = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/red_wall.png"), TILE_SCALE).convert()
IMG_COPPER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/yellow_wall.png"), TILE_SCALE).convert()
IMG_IRON = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/blue_wall.png"), TILE_SCALE).convert()
IMG_SILVER = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/cobble.png"), TILE_SCALE).convert()
IMG_GOLD = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/yellow_cobble.png"), TILE_SCALE).convert()
IMG_DIAMOND = pygame.transform.smoothscale_by(pygame.image.load("images/game/walls/mixed.png"), TILE_SCALE).convert()


class Tile:
    img = None
    drop = Drops.NONE
    dig_level = 0


class Air(Tile):
    img = None


class Dirt(Tile):
    img = IMG_DIRT


class Stone(Tile):
    img = IMG_STONE


class Clay(Tile):
    img = IMG_CLAY


class Copper(Tile):
    img = IMG_COPPER
    dig_level = 1


class Iron(Tile):
    img = IMG_IRON
    dig_level = 2


class Silver(Tile):
    img = IMG_IRON
    dig_level = 2


class Gold(Tile):
    img = IMG_GOLD
    dig_level = 2


class Diamond(Tile):
    img = IMG_DIAMOND
    dig_level = 2


class Tiles(Enum):
    AIR = Air()
    DIRT = Dirt()
    STONE = Stone()
    CLAY = Clay()
    COPPER = Copper()
    IRON = Iron()
    SILVER = Silver()
    GOLD = Gold()
    DIAMOND = Diamond()


class Facing(Enum):
    LEFT = -1
    RIGHT = 1


LEVEL_W = LEVEL_H = 20
world = [[Tiles.AIR for ix in range(LEVEL_W)] for iy in range(LEVEL_H)]

GRAVITY = 0.25
JUMP_VEL = -6.0
WALK_VEL = 4.0

PLAYER_W = 14
PLAYER_H = 32

DIG_TICKS = 1000

STANDING = ["🧍‍♂️", "🧍🏻‍♂️", "🧍🏼‍♂️", "🧍🏽‍♂️", "🧍🏾‍♂️", "🧍🏿‍♂️", "🧍‍♀️", "🧍🏻‍♀️", "🧍🏼‍♀️", "🧍🏽‍♀️", "🧍🏾‍♀️", "🧍🏿‍♀️"]
WALKING = ["🚶‍♂️", "🚶🏻‍♂️", "🚶🏼‍♂️", "🚶🏽‍♂️", "🚶🏾‍♂️", "🚶🏿‍♂️", "🚶‍♀️", "🚶🏻‍♀️", "🚶🏼‍♀️", "🚶🏽‍♀️", "🚶🏾‍♀️", "🚶🏿‍♀️"]
RUNNING = ["🏃‍♂️", "🏃🏻‍♂️", "🏃🏼‍♂️", "🏃🏽‍♂️", "🏃🏾‍♂️", "🏃🏿‍♂️", "🏃‍♀️", "🏃🏻‍♀️", "🏃🏼‍♀️", "🏃🏽‍♀️", "🏃🏾‍♀️", "🏃🏿‍♀️"]
BIKING = ["🚴‍♂️", "🚴🏻‍♂️", "🚴🏼‍♂️", "🚴🏽‍♂️", "🚴🏾‍♂️", "🚴🏿‍♂️", "🚴‍♀️", "🚴🏻‍♀️", "🚴🏼‍♀️", "🚴🏽‍♀️", "🚴🏾‍♀️", "🚴🏿‍♀️"]
HOUSES = ["🏚️", "🏠", "🏡", "🏛️"]


class Player:
    # position and movement
    x = 0.0
    y = 0.0
    emoji_index = random.randrange(len(WALKING))
    facing = Facing.RIGHT
    vel_x = 0.0
    vel_y = 0.0
    on_ground = True
    jumping = False
    ticks = 0

    # stats
    house_index = 0
    inventory: [Tile] = []
    inv_dict = {}
    inv_selected = 0

    def get_rect(self):
        return pygame.Rect(self.x + 8, self.y + 2, PLAYER_W, PLAYER_H)


def generate_world():
    for y in range(LEVEL_H):
        for x in range(LEVEL_W):
            rn = random.randint(1, 100) + y

            if 1 <= y <= 7:
                if 1 <= rn <= 70:
                    world[y][x] = Tiles.STONE
                elif 71 <= rn <= 90:
                    world[y][x] = Tiles.CLAY
                elif 91 <= rn <= 200:
                    world[y][x] = Tiles.COPPER

            if 8 <= y <= 15:
                if 1 <= rn <= 50:
                    world[y][x] = Tiles.STONE
                elif 51 <= rn <= 70:
                    world[y][x] = Tiles.COPPER
                elif 71 <= rn <= 90:
                    world[y][x] = Tiles.IRON
                elif 91 <= rn <= 200:
                    world[y][x] = Tiles.SILVER

            if 16 <= y <= 20:
                if 1 <= rn <= 50:
                    world[y][x] = Tiles.STONE
                elif 51 <= rn <= 70:
                    world[y][x] = Tiles.IRON
                elif 71 <= rn <= 90:
                    world[y][x] = Tiles.GOLD
                elif 91 <= rn <= 200:
                    world[y][x] = Tiles.DIAMOND

    world[1][10] = Tiles.AIR

    return world


def print_world(wrld):
    for y in range(LEVEL_H):
        for x in range(LEVEL_W):
            print(str(wrld[y][x]) + " ", end="")
        print()


def draw_world():
    for y in range(LEVEL_H):
        yy = y * TILE_H
        for x in range(LEVEL_W):
            xx = x * TILE_W
            # if abs(xx - player.x) < TILE_W * 2 and abs(yy - player.y) < TILE_H * 2:
            if True:
                tile = world[y][x]
                if tile.value.img is not None:
                    screen.blit(tile.value.img, (xx, yy))

    # Tile the player occupies
    tile_x = int(player.x + 8) // TILE_W
    tile_y = int(player.y + 2 + PLAYER_H) // TILE_H
    if tile_x < 0:
        tile_x = 0
    if tile_x >= LEVEL_W:
        tile_x = LEVEL_W - 1
    if tile_y < 0:
        tile_y = 0
    if tile_y >= LEVEL_H:
        tile_y = LEVEL_H - 1

    """ Mouse Movement """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if 0 <= mouse_x <= LEVEL_W * TILE_W and 0 <= mouse_y <= LEVEL_H * TILE_H:
        m_tile_x = mouse_x // TILE_W
        m_tile_y = mouse_y // TILE_H

        m_color = "#C70000"
        if 0 <= tile_x < LEVEL_W and 0 <= tile_y < LEVEL_H:
            if world[m_tile_y][m_tile_x] != Tiles.AIR and abs(tile_x - m_tile_x) < 2 and abs(tile_y - m_tile_y) < 2:
                m_color = "#00C700"

        # Hightlight mouse tile
        pygame.draw.rect(screen, m_color, (m_tile_x * TILE_W, m_tile_y * TILE_H, TILE_W, TILE_H), 2)

        """ Mouse Buttons """
        but1, but2, but3 = pygame.mouse.get_pressed()
        if but1 and m_color == "#00C700":
            player.ticks += dt
            if player.ticks >= DIG_TICKS:
                player.ticks = 0
                player.inventory.append(world[m_tile_y][m_tile_x])
                world[m_tile_y][m_tile_x] = Tiles.AIR

            else:
                dug_h = TILE_H * (DIG_TICKS - player.ticks) / DIG_TICKS
                pygame.draw.rect(screen, "#222222", (m_tile_x * TILE_W + 2, m_tile_y * TILE_H, TILE_W - 4, TILE_H - dug_h))

        if but3 and m_color == "#C70000" and world[m_tile_y][m_tile_x] == Tiles.AIR and (m_tile_x != tile_x or m_tile_y != tile_y):
            if len(player.inventory) > 0:
                ks = list(player.inv_dict.keys())
                if len(ks) > 0:
                    while player.inv_selected > len(ks):
                        player.inv_selected -= 1
                    if player.inv_selected < 0:
                        player.inv_selected = 0
                    tile = ks[player.inv_selected]
                    i = player.inventory.index(tile)
                    player.inventory.pop(i)
                    world[m_tile_y][m_tile_x] = tile

        if not but1:
            player.ticks = 0

    """ Player Movement """

    # Can player move left/right?
    min_x = 0
    max_x = (LEVEL_W - 1) * TILE_W + PLAYER_W

    if tile_x - 1 > 0 and tile_x + 1 < LEVEL_W:
        left_tile = world[tile_y][tile_x - 1]
        right_tile = world[tile_y][tile_x + 1]

        if left_tile != Tiles.AIR:
            min_x = (tile_x - 1) * TILE_W + TILE_W - (PLAYER_W // 2)
        if right_tile != Tiles.AIR:
            max_x = (tile_x + 1) * TILE_W - PLAYER_W - (PLAYER_W // 2)

    player.x += player.vel_x
    if player.x < min_x:
        player.x = min_x
    elif player.x > max_x:
        player.x = max_x

    if not player.jumping:
        while world[tile_y][tile_x] == Tiles.AIR:
            player.on_ground = False
            tile_y += 1

        target_y = (tile_y - 1) * TILE_H
        if target_y < 0:
            target_y = 0
        if target_y > LEVEL_H * TILE_H:
            target_y = LEVEL_H * TILE_H

        # Is player falling?
        if not player.on_ground:
            player.vel_y += GRAVITY
            player.y += player.vel_y

        # Stop falling
        if player.y >= target_y:
            player.on_ground = True
            player.jumping = False
            player.vel_y = 0.0
            player.y = target_y

    # Jumping
    if player.jumping:
        player.vel_y += GRAVITY
        player.y += player.vel_y

        # Check for a max jump height if there is a tile above the player
        min_y = -100
        if tile_y > 0 and world[tile_y - 1][tile_x] != Tiles.AIR:
            min_y = tile_y * TILE_H
        if player.y <= min_y:
            player.y = min_y

        # Find where player should land
        while world[tile_y][tile_x] == Tiles.AIR:
            player.on_ground = False
            tile_y += 1

        target_y = (tile_y - 1) * TILE_H
        if target_y < 0:
            target_y = 0
        if target_y > LEVEL_H * TILE_H:
            target_y = LEVEL_H * TILE_H

        # Stop jumping, player has landed
        if player.y >= target_y:
            player.on_ground = True
            player.jumping = False
            player.vel_y = 0.0
            player.y = target_y

        if player.facing == Facing.LEFT:
            emoji = FONT_EMOJI_MD.render(RUNNING[player.emoji_index], True, WHITE)
        else:
            emoji = pygame.transform.flip(FONT_EMOJI_MD.render(RUNNING[player.emoji_index], True, WHITE), True, False)
        screen.blit(emoji, (player.x, player.y))

    # Not jumping, walking
    else:
        if player.facing == Facing.LEFT:
            emoji = FONT_EMOJI_MD.render(WALKING[player.emoji_index], True, WHITE)
        else:
            emoji = pygame.transform.flip(FONT_EMOJI_MD.render(WALKING[player.emoji_index], True, WHITE), True, False)
        screen.blit(emoji, (player.x, player.y))

    # Player hitbox
    # pygame.draw.rect(screen, "#00FF00", (player.x + 8, player.y + 2, PLAYER_W, PLAYER_H), 1)

    """ Render Inventory """
    inv_dict = {}
    inv_x = LEVEL_W * TILE_W + TILE_W
    for inv_i, inv in enumerate(player.inventory):
        if inv in inv_dict.keys():
            count = inv_dict[inv]
            inv_dict[inv] = count + 1
        else:
            inv_dict[inv] = 1
    player.inv_dict = inv_dict

    for inv_i, key in enumerate(inv_dict.keys()):
        screen.blit(key.value.img, (inv_x, inv_i * TILE_H + TILE_H))
        screen.blit(FONT_EMOJI_MD.render(str(inv_dict[key]), True, WHITE), (inv_x + TILE_W, inv_i * TILE_H + TILE_H))
        if player.inv_selected == inv_i:
            pygame.draw.rect(screen, "#00FF00", (inv_x, inv_i * TILE_H + TILE_H, TILE_W, TILE_H), 2)


if __name__ == '__main__':
    world = generate_world()

    # Set mouse cursor
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

    player = Player()
    player.x = random.randrange((LEVEL_W - 1) * TILE_W + (TILE_W * 2))

    pygame.key.set_repeat(1, FPS)
    while is_running:
        screen.fill(BLACK)
        draw_world()

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = True
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                # if keys[pygame.K_w] or keys[pygame.K_UP]:
                #     player.y -= player.speed
                # elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                #     player.y += player.speed

                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    player.facing = Facing.LEFT
                    player.vel_x = -WALK_VEL
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    player.facing = Facing.RIGHT
                    player.vel_x = WALK_VEL

                if player.on_ground and keys[pygame.K_SPACE]:
                    player.vel_y = JUMP_VEL
                    player.on_ground = False
                    player.jumping = True

            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT]:
                    player.vel_x = 0.0

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    player.inv_selected -= 1
                    if player.inv_selected < 0:
                        player.inv_selected = 0
                elif event.y < 0:
                    player.inv_selected += 1
                    if player.inv_selected > len(player.inv_dict.keys()) - 1:
                        player.inv_selected = len(player.inv_dict.keys()) - 1

        dt = clock.tick(FPS)

    pygame.quit()
