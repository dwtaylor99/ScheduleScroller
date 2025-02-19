import pygame

import gradient
from colors import WHITE, BLACK
from dig_game_drops import screen
from dig_game_objects import Facing, RUNNING, WALKING, Player, PLAYER_W, PLAYER_H
from dig_game_objects import TORCH_ANIM, TORCH_W_SCALED, TORCH_H_SCALED, TORCH_DIST
from dig_game_tiles import Tiles, TILE_W, TILE_H
from dig_game_utils import constrain
from dig_game_world import generate_world
from fonts import FONT_EMOJI_SM

pygame.init()

clock = pygame.time.Clock()
dt = 0
is_running = True

FPS = 60
FONT_EMOJI_MD = pygame.font.Font("../fonts/seguiemj.ttf", 32)

MOUSE_OK_COLOR = "#00CF00"
MOUSE_BAD_COLOR = "#CF0000"
HOLLOW_COLOR = (255, 0, 255, 0)

GRAVITY = 0.5
JUMP_VEL = -8.0
WALK_VEL = 3.0
DIG_TICKS = 1000  # Should be based on player's tool level

WORLD_W = 40
WORLD_H = 20
LEVEL_W = 20
LEVEL_H = 20
main_world = [[Tiles.AIR for ix in range(WORLD_W)] for iy in range(WORLD_H)]
# world = [[Tiles.AIR for ix in range(LEVEL_W)] for iy in range(LEVEL_H)]

SCROLL_TICKS_MAX = 100
SCROLL_MIN_X = 300
SCROLL_MAX_X = (LEVEL_W * TILE_W) - 300
view_x = 0
scroll_ticks = 0

jump_allowed = True
last_m_tile_x = last_m_tile_y = 0
torch_anim_step = torch_ticks = 0


def draw_world(world):
    global last_m_tile_x, last_m_tile_y, torch_anim_step, torch_ticks, view_x, scroll_ticks

    screen.fill(BLACK)
    # view_x = 0  # Never got this to work correctly. It should be an X offset to shift the world by 'view_x' to allow scrolling.

    """ Background """
    gradient.rect_gradient_h(screen, (100, 140, 210), (64, 64, 64), pygame.Rect(0, 0, LEVEL_W * TILE_W, 2 * TILE_H))
    gradient.rect_gradient_h(screen, (64, 64, 64), (0, 0, 0), pygame.Rect(0, TILE_H * 2, LEVEL_W * TILE_W, LEVEL_H * TILE_H - (TILE_H * 2)))

    """ Border """
    low_border_x = 0
    low_border_y = LEVEL_H * TILE_H
    low_border_w = LEVEL_W * TILE_W + (TILE_W // 2)
    low_border_h = TILE_H // 2
    pygame.draw.rect(screen, (64, 64, 64), (low_border_x, low_border_y, low_border_w, low_border_h))

    side_border_x = LEVEL_W * TILE_W
    side_border_y = 0
    side_border_w = TILE_W // 2
    side_border_h = LEVEL_H * TILE_H
    pygame.draw.rect(screen, (64, 64, 64), (side_border_x, side_border_y, side_border_w, side_border_h))

    # Border stripes
    for iy in range(0, TILE_H // 2, 3):
        pygame.draw.rect(screen, BLACK, (0, low_border_y + iy + 2, low_border_w, 1))
    for ix in range(0, TILE_W // 2, 3):
        pygame.draw.rect(screen, BLACK, (side_border_x + ix + 2, 0, 1, side_border_h))

    """ Tile the player occupies """
    tile_x = int(player.x + 8) // TILE_W
    tile_y = int(player.y + 2 + PLAYER_H) // TILE_H
    tile_x = constrain(tile_x, 0, LEVEL_W - 1)
    tile_y = constrain(tile_y, 0, LEVEL_H - 1)

    # Draw the world tiles
    for y in range(LEVEL_H):
        yy = y * TILE_H
        for x in range(view_x, view_x + LEVEL_W):
            xx = (x - view_x) * TILE_W
            tile = world[y][x].value
            if tile.img is not None:
                screen.blit(tile.img, (xx, yy))

    if player.x < SCROLL_MIN_X and view_x > 0:
        player.x = SCROLL_MIN_X
        scroll_ticks += dt
        if scroll_ticks >= SCROLL_TICKS_MAX:
            scroll_ticks = 0
            view_x = constrain(view_x - 1, 0, WORLD_W - LEVEL_W)
            print("<- view_x", view_x)

    if player.x > SCROLL_MAX_X and view_x < WORLD_W - LEVEL_W:
        player.x = SCROLL_MAX_X
        scroll_ticks += dt
        if scroll_ticks >= SCROLL_TICKS_MAX:
            scroll_ticks = 0
            view_x = constrain(view_x + 1, 0, WORLD_W - LEVEL_W)
            print("-> view_x", view_x)

    """ Circle around player """
    surf_w = surf_h = 3000
    surf_w2 = surf_h2 = surf_w // 2

    # The main circle around the player
    temp_surf = pygame.Surface((surf_w, surf_h))
    temp_surf.fill(BLACK)
    temp_surf.set_colorkey((255, 0, 255))
    pygame.draw.circle(temp_surf, HOLLOW_COLOR, (surf_w2, surf_h2), 100)
    fog_x = player.x - surf_w2 + (PLAYER_W // 2)
    fog_y = player.y - surf_h2 + (PLAYER_H // 2)

    # Additional circles for each of the torches
    for torch in player.torches:
        screen.blit(TORCH_ANIM[torch_anim_step], (torch.x - (TORCH_W_SCALED // 2), torch.y - (TORCH_H_SCALED // 2)))
        pygame.draw.circle(temp_surf, HOLLOW_COLOR, (torch.x - fog_x, torch.y - fog_y), torch.w)

        # Torch animation
        torch_ticks += dt
        if torch_ticks >= 100:
            torch_anim_step = (torch_anim_step + 1) % len(TORCH_ANIM)
            torch_ticks = 0

    # screen.blit(temp_surf, (fog_x, fog_y))

    """ Mouse Movement """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if 0 <= mouse_x <= LEVEL_W * TILE_W and 0 <= mouse_y <= LEVEL_H * TILE_H:
        m_tile_x = constrain(mouse_x // TILE_W, 0, LEVEL_W - 1)
        m_tile_y = constrain(mouse_y // TILE_H, 0, LEVEL_H - 1)

        m_color = MOUSE_BAD_COLOR
        if 0 <= tile_x < LEVEL_W and 0 <= tile_y < LEVEL_H:
            if world[m_tile_y][m_tile_x - view_x] != Tiles.AIR and abs(tile_x - m_tile_x) < 2 and abs(tile_y - m_tile_y) < 2:
                m_color = MOUSE_OK_COLOR

        # Highlight mouse tile
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

        if but1 and m_color == MOUSE_OK_COLOR:
            player.ticks += dt

            # Block breaks
            if player.ticks >= DIG_TICKS:
                player.ticks = 0
                print("breaking x:", m_tile_x + view_x)
                player.add_inv(world[m_tile_y][m_tile_x + view_x])
                world[m_tile_y][m_tile_x + view_x] = Tiles.AIR
                # player.add_inv(world[m_tile_y][m_tile_x - view_x])
                # world[m_tile_y][m_tile_x - view_x] = Tiles.AIR

                for wx in range(WORLD_W):
                    a = str(world[1][wx])[6:8]
                    print("{}".format(a), end=" ")
                print()

            # Digging progress
            else:
                dug_h = TILE_H * (DIG_TICKS - player.ticks) / DIG_TICKS  # calculate the percentage dug
                temp_surf = pygame.Surface((TILE_W - 4, TILE_H - dug_h))
                temp_surf.set_alpha(128)
                temp_surf.fill((192, 0, 0))
                screen.blit(temp_surf, (m_tile_x * TILE_W + 2, m_tile_y * TILE_H))

        # Place a block
        if (but3 and m_color == MOUSE_BAD_COLOR and world[m_tile_y][m_tile_x - view_x] == Tiles.AIR
                and (m_tile_x != tile_x or m_tile_y != tile_y) and abs(tile_x - m_tile_x) < 2 and abs(tile_y - m_tile_y) < 2):
            if len(player.inv_dict.keys()) > 0:
                ks = list(player.inv_dict.keys())
                if len(ks) > 0:
                    while player.inv_selected >= len(ks):
                        player.inv_selected -= 1

                    if player.inv_selected < 0:
                        player.inv_selected = 0

                    tile = ks[player.inv_selected]
                    player.remove_inv(tile)
                    world[m_tile_y][m_tile_x - view_x] = tile

    """ Player Movement """

    # left_tile = world[tile_y][tile_x - view_x - 1] if tile_x - 1 >= 0 else Tiles.STONE
    # right_tile = world[tile_y][tile_x - view_x + 1] if tile_x + 1 < LEVEL_W else Tiles.STONE
    left_tile = world[tile_y][tile_x - view_x - 1] if tile_x - 1 >= 0 else Tiles.STONE
    right_tile = world[tile_y][tile_x - view_x + 1] if tile_x + 1 < LEVEL_W else Tiles.STONE

    min_x = (tile_x - 1) * TILE_W + TILE_W - (PLAYER_W // 2) if left_tile != Tiles.AIR else 0
    max_x = (tile_x + 1) * TILE_W - PLAYER_W - (PLAYER_W // 2) if right_tile != Tiles.AIR else (LEVEL_W - 1) * TILE_W + PLAYER_W
    # min_x = (tile_x - view_x - 1) * TILE_W + TILE_W - (PLAYER_W // 2) if left_tile != Tiles.AIR else 0
    # max_x = (tile_x - view_x + 1) * TILE_W - PLAYER_W - (PLAYER_W // 2) if right_tile != Tiles.AIR else (LEVEL_W - 1) * TILE_W + PLAYER_W

    player.x = constrain(player.x + player.vel_x, min_x, max_x)

    stats = FONT_EMOJI_SM.render("px: {}, py: {}, tile_x: {}, tile_y: {}, view_x: {}, left_tile: {}, right_tile: {}, min_x: {}, max_x: {}"
                                 .format(player.x, player.y, tile_x, tile_y, view_x, left_tile, right_tile, min_x, max_x), True, WHITE).convert_alpha()
    screen.blit(stats, (4, 900))

    if player.on_ground:
        while tile_y < WORLD_H and world[tile_y][tile_x + view_x] == Tiles.AIR:
            player.on_ground = False
            tile_y += 1

        target_y = constrain((tile_y - 1) * TILE_H, 0, LEVEL_H * TILE_H)

        # Is player falling?
        if not player.on_ground:
            player.vel_y += GRAVITY
            player.y += player.vel_y

        # Stop falling
        if player.y >= target_y:
            player.on_ground = True
            player.vel_y = 0.0
            player.y = target_y

    # Jumping
    if not player.on_ground:
        player.vel_y += GRAVITY
        player.y += player.vel_y

        # Check for a max jump height if there is a tile above the player
        min_y = -100
        if tile_y > 0 and world[tile_y - 1][tile_x - view_x] != Tiles.AIR:
            min_y = tile_y * TILE_H
        if player.y <= min_y:
            player.y = min_y

        # Find where player should land
        while tile_y < LEVEL_H and world[tile_y][tile_x - view_x] == Tiles.AIR:
            player.on_ground = False
            tile_y += 1

        target_y = constrain((tile_y - 1) * TILE_H, 0, LEVEL_H * TILE_H)

        # Stop jumping, player has landed
        if player.y >= target_y:
            player.on_ground = True
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
    # pygame.draw.rect(screen, "#00FF00", player.get_rect(), 1)

    """ Render Inventory """
    inv_x = LEVEL_W * TILE_W + (TILE_W // 2) + 4
    for inv_i, key in enumerate(player.inv_dict.keys()):
        screen.blit(key.value.drop.img, (inv_x - 2, inv_i * TILE_H + TILE_H + 1))
        screen.blit(FONT_EMOJI_SM.render(str(player.inv_dict[key]), True, WHITE).convert_alpha(), (inv_x + TILE_W + 4, inv_i * TILE_H + TILE_H + 18))
        if player.inv_selected == inv_i:
            screen.blit(FONT_EMOJI_SM.render(key.value.drop.name, True, WHITE).convert_alpha(), (inv_x, 20))
            pygame.draw.rect(screen, "#00FF00", (inv_x, inv_i * TILE_H + TILE_H, TILE_W, TILE_H), 2)


if __name__ == '__main__':
    main_world = generate_world(WORLD_W, WORLD_H)
    # world = generate_world(LEVEL_W, LEVEL_H)
    player = Player()

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    pygame.key.set_repeat(1, FPS)

    while is_running:
        draw_world(main_world)

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

                    if player.x < SCROLL_MIN_X and view_x > 0:
                        player.x = SCROLL_MIN_X
                        scroll_ticks += dt
                        if scroll_ticks >= SCROLL_TICKS_MAX:
                            scroll_ticks = 0
                            view_x = constrain(view_x - 1, 0, WORLD_W - LEVEL_W)
                    else:
                        if keys[pygame.K_LSHIFT]:
                            player.vel_x = -WALK_VEL // 2
                        else:
                            player.vel_x = -WALK_VEL

                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    player.facing = Facing.RIGHT

                    if player.x > SCROLL_MAX_X and view_x < WORLD_W - LEVEL_W:
                        player.x = SCROLL_MAX_X
                        scroll_ticks += dt
                        if scroll_ticks >= SCROLL_TICKS_MAX:
                            scroll_ticks = 0
                            view_x = constrain(view_x + 1, 0, WORLD_W - LEVEL_W)

                    if keys[pygame.K_LSHIFT]:
                        player.vel_x = WALK_VEL // 2
                    else:
                        player.vel_x = WALK_VEL

                elif keys[pygame.K_t]:
                    player.torches.append(pygame.Rect(player.x + PLAYER_W, player.y + PLAYER_H // 2, TORCH_DIST, TORCH_DIST))

                if keys[pygame.K_SPACE] and player.on_ground and jump_allowed:
                    jump_allowed = False
                    player.vel_y = JUMP_VEL
                    player.on_ground = False

            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT]:
                    player.vel_x = 0.0
                if event.key == pygame.K_SPACE:
                    jump_allowed = True

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
* Larger, scrolling world
* Lamps/Torch to expand sight line

+ Combine on_ground and jumping flags 
+ Stop space bar from repeat jumping
+ Caves
+ Rooms
+ Convert inventory array to dict
+ Limit sight line
+ Lamps to keep areas lit
"""
