import random

import pygame

import gradient
from colors import WHITE, BLACK
from dig_game_drops import screen
from dig_game_player import Facing, RUNNING, WALKING, Player, PLAYER_W, PLAYER_H
from dig_game_tiles import Tiles, TILE_W, TILE_H
from fonts import FONT_EMOJI_SM

pygame.init()

clock = pygame.time.Clock()
dt = 0
is_running = True

FPS = 60
FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)

HOLLOW_COLOR = (255, 0, 255, 0)

LEVEL_W = LEVEL_H = 20
world = [[Tiles.AIR for ix in range(LEVEL_W)] for iy in range(LEVEL_H)]

GRAVITY = 0.5
JUMP_VEL = -8.0
WALK_VEL = 3.0
DIG_TICKS = 1000  # Should be based on player's tool level

last_m_tile_x = 0
last_m_tile_y = 0

# Torches
TORCH_DIST = 100  # Default distance to light up (radius of circle)
TORCH_SHEET = pygame.image.load("images/game/torch_sheet.png")
TORCH_SCALE = 0.05
torch_x = 64
torch_y = 115
torch_w = 260
torch_h = 520
torch_w_scaled = torch_w * TORCH_SCALE
torch_h_scaled = torch_h * TORCH_SCALE

TORCH_SHEET.set_clip((torch_x, torch_y, torch_w, torch_h))
TORCH_01 = pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha()
TORCH_SHEET.set_clip((torch_x + torch_w, torch_y, torch_w, torch_h))
TORCH_02 = pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha()
TORCH_SHEET.set_clip((torch_x + torch_w * 2, torch_y, torch_w, torch_h))
TORCH_03 = pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha()
TORCH_SHEET.set_clip((torch_x + torch_w * 3, torch_y, torch_w, torch_h))
TORCH_04 = pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha()
TORCH_SHEET.set_clip((torch_x + torch_w * 4, torch_y, torch_w, torch_h))
TORCH_05 = pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha()
TORCH_SHEET.set_clip((torch_x + torch_w * 5, torch_y, torch_w, torch_h))
TORCH_06 = pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha()
TORCH_SHEET.set_clip((torch_x + torch_w * 6, torch_y, torch_w, torch_h))
TORCH_07 = pygame.transform.smoothscale_by(TORCH_SHEET.subsurface(TORCH_SHEET.get_clip()), TORCH_SCALE).convert_alpha()

TORCH_ANIM = [TORCH_01, TORCH_02, TORCH_03, TORCH_04, TORCH_05, TORCH_06, TORCH_07]
torch_anim_step = 0
torch_ticks = 0


def generate_world():
    for y in range(LEVEL_H):
        for x in range(LEVEL_W):
            rn = random.randint(1, 100) + y

            if 1 <= y <= 3:
                if 1 <= rn <= 40:
                    world[y][x] = Tiles.DIRT
                elif 41 <= rn <= 70:
                    world[y][x] = Tiles.STONE
                elif 71 <= rn <= 90:
                    world[y][x] = Tiles.CLAY
                elif 91 <= rn <= 200:
                    world[y][x] = Tiles.COPPER

            if 4 <= y <= 7:
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

    # for yyy in range(19):
    #     world[yyy][10] = Tiles.AIR

    rn = 2  # random.randint(1, 2)
    for room_i in range(rn):
        room_x = random.randrange(LEVEL_W - 4) + 2
        room_y = random.randrange(LEVEL_H // 2) + (LEVEL_H // 2) - 3

        room_size = random.randint(2, 4)
        for jj in range(room_size):
            for ii in range(room_size):
                yyy = constrain(room_y + jj, 0, LEVEL_H - 1)
                xxx = constrain(room_x + ii, 0, LEVEL_W - 1)
                world[yyy][xxx] = Tiles.AIR
            if jj == room_size - 1:
                world[room_y + jj][room_x] = Tiles.REWARD_URN

    return world


def constrain(val, min_val, max_val):
    out = val
    if val < min_val:
        out = min_val
    elif val > max_val:
        out = max_val
    return out


def draw_world():
    global last_m_tile_x, last_m_tile_y, torch_anim_step, torch_ticks

    screen.fill(BLACK)

    # Gradient background
    gradient.rect_gradient_h(screen, (100, 140, 210), (64, 64, 64), pygame.Rect(0, 0, LEVEL_W * TILE_W, 2 * TILE_H))
    gradient.rect_gradient_h(screen, (64, 64, 64), (0, 0, 0), pygame.Rect(0, TILE_H * 2, LEVEL_W * TILE_W, LEVEL_H * TILE_H - (TILE_H * 2)))

    # Border
    pygame.draw.rect(screen, (64, 64, 64), (0, LEVEL_H * TILE_H, LEVEL_W * TILE_W + (TILE_W // 2), TILE_H // 2))
    pygame.draw.rect(screen, (64, 64, 64), (LEVEL_W * TILE_W, 0, (TILE_W // 2), LEVEL_H * TILE_H))

    # Draw the world tiles
    for y in range(LEVEL_H):
        yy = y * TILE_H
        for x in range(LEVEL_W):
            xx = x * TILE_W
            tile = world[y][x].value
            if tile.img is not None:
                screen.blit(tile.img, (xx, yy))

    """ Circle around player """
    surf_w = surf_h = 3000
    surf_w2 = surf_h2 = surf_w // 2

    temp_surf = pygame.Surface((surf_w, surf_h))
    temp_surf.fill(BLACK)
    temp_surf.set_colorkey((255, 0, 255))
    pygame.draw.circle(temp_surf, HOLLOW_COLOR, (surf_w2, surf_h2), 100)

    fog_x = player.x - surf_w2 + (PLAYER_W // 2)
    fog_y = player.y - surf_h2 + (PLAYER_H // 2)

    for torch in player.torches:
        screen.blit(TORCH_ANIM[torch_anim_step], (torch.x - (torch_w_scaled // 2), torch.y - (torch_h_scaled // 2)))
        pygame.draw.circle(temp_surf, HOLLOW_COLOR, (torch.x - fog_x, torch.y - fog_y), torch.w)
        torch_ticks += dt
        if torch_ticks >= 100:
            torch_ticks = 0
            torch_anim_step = (torch_anim_step + 1) % len(TORCH_ANIM)

    screen.blit(temp_surf, (fog_x, fog_y))

    # Tile the player occupies
    tile_x = int(player.x + 8) // TILE_W
    tile_y = int(player.y + 2 + PLAYER_H) // TILE_H
    tile_x = constrain(tile_x, 0, LEVEL_W - 1)
    tile_y = constrain(tile_y, 0, LEVEL_H - 1)

    """ Mouse Movement """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if 0 <= mouse_x <= LEVEL_W * TILE_W and 0 <= mouse_y <= LEVEL_H * TILE_H:
        m_tile_x = mouse_x // TILE_W
        m_tile_y = mouse_y // TILE_H
        m_tile_x = constrain(m_tile_x, 0, LEVEL_W - 1)
        m_tile_y = constrain(m_tile_y, 0, LEVEL_H - 1)

        m_color = "#C70000"
        if 0 <= tile_x < LEVEL_W and 0 <= tile_y < LEVEL_H:
            if world[m_tile_y][m_tile_x] != Tiles.AIR and abs(tile_x - m_tile_x) < 2 and abs(tile_y - m_tile_y) < 2:
                m_color = "#00C700"

        # Hightlight mouse tile
        pygame.draw.rect(screen, m_color, (m_tile_x * TILE_W, m_tile_y * TILE_H, TILE_W, TILE_H), 2)

        """ Mouse Buttons """
        but1, but2, but3 = pygame.mouse.get_pressed()
        if not but1:
            player.ticks = 0

        # If mouse moved to a different tile, reset the digging progress
        if last_m_tile_x != m_tile_x or last_m_tile_y != m_tile_y:
            player.ticks = 0
        last_m_tile_x = m_tile_x
        last_m_tile_y = m_tile_y

        if but1 and m_color == "#00C700":
            player.ticks += dt

            # Block breaks
            if player.ticks >= DIG_TICKS:
                player.ticks = 0
                player.inventory.append(world[m_tile_y][m_tile_x])
                world[m_tile_y][m_tile_x] = Tiles.AIR

            # Digging progress
            else:
                dug_h = TILE_H * (DIG_TICKS - player.ticks) / DIG_TICKS
                temp_surf = pygame.Surface((TILE_W - 4, TILE_H - dug_h))
                temp_surf.set_alpha(128)
                temp_surf.fill((192, 0, 0))
                screen.blit(temp_surf, (m_tile_x * TILE_W + 2, m_tile_y * TILE_H))

        # Place a block
        if but3 and m_color == "#C70000" and world[m_tile_y][m_tile_x] == Tiles.AIR and (m_tile_x != tile_x or m_tile_y != tile_y):
            if len(player.inventory) > 0:
                ks = list(player.inv_dict.keys())
                if len(ks) > 0:
                    while player.inv_selected >= len(ks):
                        player.inv_selected -= 1
                    if player.inv_selected < 0:
                        player.inv_selected = 0
                    tile = ks[player.inv_selected]
                    i = player.inventory.index(tile)
                    player.inventory.pop(i)
                    world[m_tile_y][m_tile_x] = tile

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
        while tile_y < LEVEL_H and world[tile_y][tile_x] == Tiles.AIR:
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
        while tile_y < LEVEL_H and world[tile_y][tile_x] == Tiles.AIR:
            player.on_ground = False
            tile_y += 1
            # tile_y = constrain(tile_y, 0, LEVEL_H - 1)

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
            emoji = FONT_EMOJI_MD.render(RUNNING[player.emoji_index], True, WHITE).convert_alpha()
        else:
            emoji = pygame.transform.flip(FONT_EMOJI_MD.render(RUNNING[player.emoji_index], True, WHITE), True, False).convert_alpha()
        screen.blit(emoji, (player.x, player.y + 4))

    # Not jumping, walking
    else:
        if player.facing == Facing.LEFT:
            emoji = FONT_EMOJI_MD.render(WALKING[player.emoji_index], True, WHITE).convert_alpha()
        else:
            emoji = pygame.transform.flip(FONT_EMOJI_MD.render(WALKING[player.emoji_index], True, WHITE), True, False).convert_alpha()
        screen.blit(emoji, (player.x, player.y + 4))

    # Player hitbox
    pygame.draw.rect(screen, "#00FF00", player.get_rect(), 1)

    """ Render Inventory """
    inv_dict = {}
    for inv_i, inv in enumerate(player.inventory):
        if inv in inv_dict.keys():
            inv_dict[inv] = inv_dict[inv] + 1
        else:
            inv_dict[inv] = 1
    player.inv_dict = inv_dict

    inv_x = LEVEL_W * TILE_W + (TILE_W // 2) + 4
    for inv_i, key in enumerate(inv_dict.keys()):
        screen.blit(key.value.drop.img, (inv_x - 2, inv_i * TILE_H + TILE_H + 1))
        screen.blit(FONT_EMOJI_SM.render(str(inv_dict[key]), True, WHITE).convert_alpha(), (inv_x + TILE_W + 4, inv_i * TILE_H + TILE_H + 18))
        if player.inv_selected == inv_i:
            screen.blit(FONT_EMOJI_SM.render(key.value.drop.name, True, WHITE).convert_alpha(), (inv_x, 20))
            pygame.draw.rect(screen, "#00FF00", (inv_x, inv_i * TILE_H + TILE_H, TILE_W, TILE_H), 2)


if __name__ == '__main__':
    world = generate_world()

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

    player = Player()
    player.x = random.randrange((LEVEL_W - 1) * TILE_W + (TILE_W * 2))

    pygame.key.set_repeat(1, FPS)
    while is_running:
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
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        player.vel_x = -(WALK_VEL // 2)
                    else:
                        player.vel_x = -WALK_VEL
                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    player.facing = Facing.RIGHT
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        player.vel_x = (WALK_VEL // 2)
                    else:
                        player.vel_x = WALK_VEL

                if player.on_ground and keys[pygame.K_SPACE]:
                    player.vel_y = JUMP_VEL
                    player.on_ground = False
                    player.jumping = True

                if keys[pygame.K_t]:
                    player.torches.append(pygame.Rect(player.x + PLAYER_W, player.y + PLAYER_H // 2, TORCH_DIST, TORCH_DIST))

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

"""
TODO:
* Convert inventory array to dict
* Caves and rooms
* Larger, scrolling world
* Limit sight line
* Lamps to keep areas lit
* Lamps/Torch to expand sight line
"""
