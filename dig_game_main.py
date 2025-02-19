import pygame

import gradient
from colors import WHITE, BLACK, YELLOW, RED
from dig_game_drops import screen
from dig_game_objects import Facing, RUNNING, WALKING, Player, PLAYER_W, PLAYER_H
from dig_game_objects import TORCH_ANIM, TORCH_W_SCALED, TORCH_H_SCALED, TORCH_DIST
from dig_game_tiles import Tiles, TILE_W, TILE_H, Tree01, RewardUrn, IMG_GRASS, IMG_VOLTAGE, IMG_BUSH_01, IMG_BUSH_02, \
    IMG_BUSH_03, IMG_BUSH_04
from dig_game_utils import constrain
from dig_game_world import generate_world
from fonts import FONT_EMOJI_SM

pygame.init()

clock = pygame.time.Clock()
dt = 0
is_running = True
is_debug_stats = False

FPS = 60
FONT_EMOJI_MD = pygame.font.Font("fonts/seguiemj.ttf", 32)

MOUSE_OK_COLOR = "#00CF00"
MOUSE_BAD_COLOR = "#CF0000"
HOLLOW_COLOR = (255, 0, 255, 0)
CHARGE_GOOD_COLOR = (0, 150, 0)
CHARGE_WARN_COLOR = (100, 100, 0)
CHARGE_BAD_COLOR = (150, 0, 0)

GRAVITY = 0.4
JUMP_VEL = -5.0
WALK_VEL = 6.0

WORLD_W = 50
WORLD_H = 50
LEVEL_W = 20
LEVEL_H = 20
main_world = [[Tiles.AIR for _ in range(WORLD_W)] for _ in range(WORLD_H)]

DEBOUNCE = 200
key_ticks = DEBOUNCE
jump_allowed = True
last_m_tile_x = last_m_tile_y = 0
torch_anim_step = torch_ticks = 0

ui_surf = pygame.Surface((screen.get_width(), TILE_H * 2))


def draw_world(world, bgs):
    global last_m_tile_x, last_m_tile_y, torch_anim_step, torch_ticks

    screen.fill(BLACK)

    screen_w = screen.get_width()
    screen_h = screen.get_height()
    screen_w2 = screen_w // 2
    screen_h2 = screen_h // 2

    """ Tile the player occupies """
    tile_x = int(player.x + 8) // TILE_W
    tile_y = int(player.y + 2 + PLAYER_H) // TILE_H
    tile_x = constrain(tile_x, 0, WORLD_W - 1)
    tile_y = constrain(tile_y, 0, WORLD_H - 1)

    # Draw the world tiles
    sky_surf = pygame.Surface((WORLD_W * TILE_W, 500))
    world_surf = pygame.Surface((WORLD_W * TILE_W, WORLD_H * TILE_H))

    """ Background """
    # Sky
    gradient.rect_gradient_h(sky_surf, (210, 210, 210), (120, 160, 200), pygame.Rect(0, 0, sky_surf.get_width(), sky_surf.get_height()))
    # Cave dark background
    gradient.rect_gradient_h(world_surf, (120, 160, 200), (60, 110, 175), pygame.Rect(0, 0, world_surf.get_width(), 5 * TILE_H))
    gradient.rect_gradient_h(world_surf, (60, 110, 175), (32, 32, 32), pygame.Rect(0, 5 * TILE_H, world_surf.get_width(), 2 * TILE_H))
    gradient.rect_gradient_h(world_surf, (32, 32, 32), (0, 0, 0), pygame.Rect(0, 7 * TILE_H, world_surf.get_width(), WORLD_H * TILE_H - (7 * TILE_H)))

    for y in range(WORLD_H):
        yy = y * TILE_H
        for x in range(WORLD_W):
            xx = x * TILE_W
            tile = world[y][x].value
            if bgs[y][x] is not None:
                off_y = 0
                if bgs[y][x] in [IMG_BUSH_01, IMG_BUSH_02, IMG_BUSH_03, IMG_BUSH_04]:
                    off_y = -bgs[y][x].get_height() + TILE_H
                world_surf.blit(bgs[y][x], (xx, yy + off_y))
            if tile.img is not None:
                world_surf.blit(tile.img, (xx + tile.img_offset_x, yy + tile.img_offset_y))
                if y == 5:
                    world_surf.blit(IMG_GRASS, (xx, yy - TILE_H + 2))

    player.x = constrain(player.x + player.vel_x, 0, world_surf.get_width() - PLAYER_W)
    player.y = constrain(player.y + player.vel_y, -100, world_surf.get_height())

    offset_x = -player.x + screen_w2 + (PLAYER_W // 2)
    offset_y = -player.y + (screen_h2 // 2)

    # Draw the surfaces to the screen
    screen.blit(sky_surf, (offset_x, offset_y - sky_surf.get_height()))
    screen.blit(world_surf, (offset_x, offset_y))

    """ Circle around player """
    # Once player is on tile_y >= 7, darkness happens
    surf_w = WORLD_W * TILE_W
    surf_h = WORLD_H * TILE_H

    # The main circle around the player
    temp_surf = pygame.Surface((surf_w, surf_h))
    temp_surf.fill(BLACK)
    temp_surf.set_colorkey((255, 0, 255))
    if tile_y >= 6:
        pygame.draw.circle(temp_surf, HOLLOW_COLOR, (screen.get_width() // 2 + (PLAYER_W // 2), (tile_y - 7) * TILE_H), 100)

    # Additional circles for each of the torches
    for torch in player.torches:
        screen.blit(TORCH_ANIM[torch_anim_step], (torch.x - (TORCH_W_SCALED // 2) - (PLAYER_W // 2) + offset_x, torch.y - (TORCH_H_SCALED // 2) + offset_y))
        pygame.draw.circle(temp_surf, HOLLOW_COLOR, (torch.x + offset_x - PLAYER_W, torch.y - (screen.get_height() // 4 + PLAYER_H + 6)), torch.w)
        # pygame.draw.circle(temp_surf, HOLLOW_COLOR, (torch.x + offset_x - PLAYER_W, torch.y - (tile_y * TILE_H) - TILE_H - offset_y), torch.w)

        # Torch animation
        torch_ticks += dt
        if torch_ticks >= 100:
            torch_anim_step = (torch_anim_step + 1) % len(TORCH_ANIM)
            torch_ticks = 0

    if not is_debug_stats:
        screen.blit(temp_surf, (0, (TILE_H * 7) + offset_y))

    """ Mouse Movement """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    but1, but2, but3 = pygame.mouse.get_pressed()

    # Convert the mouse position to tile coordinates
    m_tile_x = int(constrain((mouse_x - offset_x) // TILE_W, 0, WORLD_W - 1))
    m_tile_y = int(constrain((mouse_y - offset_y) // TILE_H, 0, WORLD_H - 1))

    # Is the targeted block close enough to the player to dig it?
    m_color = MOUSE_BAD_COLOR
    if abs(tile_x - m_tile_x) < 2 and abs(tile_y - m_tile_y) < 2:
        m_color = MOUSE_OK_COLOR

    # Highlight mouse tile
    pygame.draw.rect(screen, m_color, (m_tile_x * TILE_W + offset_x, m_tile_y * TILE_H + offset_y, TILE_W, TILE_H), 2)

    # Reset ticks if mouse button 1 is released
    if not but1:
        player.ticks = 0

    # If mouse moved to a different tile, reset the digging progress
    if last_m_tile_x != m_tile_x or last_m_tile_y != m_tile_y:
        player.ticks = 0
    last_m_tile_x = m_tile_x
    last_m_tile_y = m_tile_y

    if but1 and m_color == MOUSE_OK_COLOR and world[m_tile_y][m_tile_x].value.dig_level > 0:
        # Check if the targeted block is an unreachable diagonal
        up_tile = world[tile_y - 1][tile_x]
        down_tile = world[tile_y + 1][tile_x]
        left_tile = world[tile_y][tile_x - 1]
        right_tile = world[tile_y][tile_x + 1]

        allow_dig = True
        if m_tile_x < tile_x and m_tile_y < tile_y and up_tile.value.is_solid and left_tile.value.is_solid:
            allow_dig = False  # up and left
        elif m_tile_x < tile_x and m_tile_y > tile_y and down_tile.value.is_solid and left_tile.value.is_solid:
            allow_dig = False  # down and left
        elif m_tile_x > tile_x and m_tile_y < tile_y and up_tile.value.is_solid and right_tile.value.is_solid:
            allow_dig = False  # up and right
        elif m_tile_x > tile_x and m_tile_y > tile_y and down_tile.value.is_solid and right_tile.value.is_solid:
            allow_dig = False  # down and right

        block_ticks = world[m_tile_y][m_tile_x].value.dig_ticks
        if allow_dig and block_ticks > 0:
            # Start digging the block
            player.ticks += dt

            # Block breaks
            if player.ticks >= block_ticks:
                player.ticks = 0
                player.add_inv(world[m_tile_y][m_tile_x])
                world[m_tile_y][m_tile_x] = Tiles.AIR

            # Digging progress
            else:
                # Line from player to mouse crosshair
                line_color = YELLOW if player.ticks % 60 < 30 else RED
                pygame.draw.line(screen, line_color, (player.x + offset_x + (PLAYER_W // 2), player.y + offset_y + (PLAYER_H // 2)), (mouse_x, mouse_y), 2)

                # Cover the block with a translucent effect to indicate progress
                dug_h = TILE_H * (block_ticks - player.ticks) / block_ticks  # calculate the percentage dug
                temp_surf = pygame.Surface((TILE_W - 4, TILE_H - dug_h))
                temp_surf.set_alpha(128)
                temp_surf.fill((192, 0, 0))
                screen.blit(temp_surf, (m_tile_x * TILE_W + 2 + offset_x, m_tile_y * TILE_H + offset_y))

                # Reduce the tool charge by the time spent digging
                player.tool_charge -= dug_h / ((player.tool_level + 2) * 100)

    # Place a block
    if (but3 and world[m_tile_y][m_tile_x] == Tiles.AIR
            and world[m_tile_y][m_tile_x] not in [Tiles.HOUSE_1, Tiles.HOUSE_2, Tiles.HOUSE_3, Tiles.HOUSE_4]
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
                world[m_tile_y][m_tile_x] = tile

                # If a torch is in the tile, delete it
                if len(player.torches) > 0:
                    new_torch_list = []
                    for torch in player.torches:
                        t_tile_x = torch.x // TILE_W
                        t_tile_y = torch.y // TILE_H
                        if m_tile_x != t_tile_x or m_tile_y != t_tile_y:
                            new_torch_list.append(torch)
                    player.torches = new_torch_list

    # Right-clicked the house, open house UI
    elif but3 and world[m_tile_y][m_tile_x] in [Tiles.HOUSE_1, Tiles.HOUSE_2, Tiles.HOUSE_3, Tiles.HOUSE_4]:
        print("House clicked!")

    """ Player Movement """
    # Limit left/right movement
    left_tile = world[tile_y][tile_x - 1] if tile_x - 1 >= 0 else Tiles.STONE
    right_tile = world[tile_y][tile_x + 1] if tile_x + 1 < WORLD_W else Tiles.STONE

    min_x = (tile_x - 1) * TILE_W + TILE_W - 3 if left_tile.value.is_solid else 0
    max_x = (tile_x + 1) * TILE_W - PLAYER_W if right_tile.value.is_solid else (WORLD_W - 1) * TILE_W + PLAYER_W

    player.x = constrain(player.x, min_x, max_x)

    if player.on_ground:
        while tile_y < WORLD_H and not world[tile_y][tile_x].value.is_solid:
            player.on_ground = False
            tile_y += 1

        target_y = constrain((tile_y - 1) * TILE_H, 0, WORLD_H * TILE_H)

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
        # if tile_y > 0 and world[tile_y - 1][tile_x] != Tiles.AIR:
        if tile_y > 0 and world[tile_y - 1][tile_x].value.is_solid:
            min_y = tile_y * TILE_H
        if player.y <= min_y:
            player.y = min_y

        # Find where player should land
        while tile_y < WORLD_H and not world[tile_y][tile_x].value.is_solid:
            player.on_ground = False
            tile_y += 1

        target_y = constrain((tile_y - 1) * TILE_H, 0, WORLD_H * TILE_H)

        # Stop jumping, player has landed
        if player.y >= target_y:
            player.on_ground = True
            player.vel_y = 0.0
            player.y = target_y

        if player.facing == Facing.LEFT:
            emoji = FONT_EMOJI_MD.render(RUNNING[player.emoji_index], True, WHITE).convert_alpha()
        else:
            emoji = pygame.transform.flip(FONT_EMOJI_MD.render(RUNNING[player.emoji_index], True, WHITE), True, False).convert_alpha()
        screen.blit(emoji, (screen.get_width() // 2, screen.get_height() // 4 + 5))

    # Not jumping, walking
    else:
        if player.facing == Facing.LEFT:
            emoji = FONT_EMOJI_MD.render(WALKING[player.emoji_index], True, WHITE).convert_alpha()
        else:
            emoji = pygame.transform.flip(FONT_EMOJI_MD.render(WALKING[player.emoji_index], True, WHITE), True, False).convert_alpha()
        screen.blit(emoji, (screen.get_width() // 2, screen.get_height() // 4 + 5))

    """ Border """
    # low_border_x = 0
    # low_border_y = LEVEL_H * TILE_H
    # low_border_w = screen.get_width()
    # low_border_h = TILE_H // 2
    # pygame.draw.rect(screen, (64, 64, 64), (low_border_x, low_border_y, low_border_w, low_border_h))

    """ Render UI """
    # Inventory
    FONT_EMOJI_SM.set_bold(True)
    ui_surf.fill((32, 32, 32))
    ui_surf_w = ui_surf.get_width()
    ui_surf_h = ui_surf.get_height()
    ui_y = screen_h - TILE_H * 2

    for inv_i, key in enumerate(player.inv_dict.keys()):
        inv_x = TILE_W * inv_i + 3
        ui_surf.blit(key.value.drop.value.img, (inv_x, 32))
        ui_surf.blit(FONT_EMOJI_SM.render(str(player.inv_dict[key]), True, BLACK).convert_alpha(), (inv_x + 3, 33))
        ui_surf.blit(FONT_EMOJI_SM.render(str(player.inv_dict[key]), True, WHITE).convert_alpha(), (inv_x + 2, 32))

        if player.inv_selected == inv_i:
            pygame.draw.rect(ui_surf, "#00FF00", (TILE_W * inv_i + 4, 30, TILE_W, TILE_H), 2)
            ui_surf.blit(FONT_EMOJI_SM.render(key.value.drop.value.name, True, WHITE).convert_alpha(), (4, 4))

    # Charge Level
    charge_color = CHARGE_GOOD_COLOR
    if player.tool_charge < 20:
        charge_color = CHARGE_BAD_COLOR
    elif player.tool_charge < 50:
        charge_color = CHARGE_WARN_COLOR
    pygame.draw.rect(ui_surf, charge_color, (ui_surf_w - 80, 4, 70, ui_surf_h - 8), 0, 10)
    ui_surf.blit(FONT_EMOJI_SM.render("{}%".format(int(player.tool_charge)), True, BLACK).convert_alpha(), (ui_surf_w - 64, 10))
    ui_surf.blit(FONT_EMOJI_SM.render("{}%".format(int(player.tool_charge)), True, WHITE).convert_alpha(), (ui_surf_w - 65, 9))
    ui_surf.blit(IMG_VOLTAGE, (ui_surf.get_width() - 65, 32))

    FONT_EMOJI_SM.set_bold(False)
    screen.blit(ui_surf, (0, ui_y))

    """ Debug stats (toggle with F3) """
    if is_debug_stats:
        player_rect = player.get_rect()
        player_rect.x += offset_x
        player_rect.y += offset_y
        pygame.draw.rect(screen, "#00FF00", player_rect, 1)  # Player hitbox

        stats = FONT_EMOJI_SM.render("px: {}, py: {} | tile_x: {}, tile_y: {}".format(player.x, player.y, tile_x, tile_y), True, WHITE).convert_alpha()
        stat2 = FONT_EMOJI_SM.render("m_tile_x: {}, m_tile_y: {}".format(m_tile_x, m_tile_y), True, WHITE).convert_alpha()
        stat3 = FONT_EMOJI_SM.render("left: {}, right: {}, min_x: {}, max_x: {}".format(left_tile, right_tile, min_x, max_x), True, WHITE)
        screen.blit(stats, (500, screen_h - 80))
        screen.blit(stat2, (500, screen_h - 55))
        screen.blit(stat3, (500, screen_h - 25))


if __name__ == '__main__':
    main_world, main_bg = generate_world(WORLD_W, WORLD_H)
    player = Player()

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    pygame.key.set_repeat(20, FPS)

    while is_running:
        draw_world(main_world, main_bg)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = True
            elif event.type == pygame.KEYDOWN:
                debounce = False
                key_ticks += dt
                if key_ticks >= DEBOUNCE:
                    debounce = True

                keys = pygame.key.get_pressed()

                # if keys[pygame.K_w] or keys[pygame.K_UP]:
                #     player.y -= player.speed
                # elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                #     player.y += player.speed

                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    player.facing = Facing.LEFT

                    if keys[pygame.K_LSHIFT]:
                        player.vel_x = -WALK_VEL // 2
                    else:
                        player.vel_x = -WALK_VEL

                elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    player.facing = Facing.RIGHT

                    if keys[pygame.K_LSHIFT]:
                        player.vel_x = WALK_VEL // 2
                    else:
                        player.vel_x = WALK_VEL

                # These keys require debounce
                if debounce:
                    if keys[pygame.K_t]:
                        key_ticks = 0
                        player.torches.append(pygame.Rect(player.x + PLAYER_W, player.y + PLAYER_H // 2, TORCH_DIST, TORCH_DIST))

                    elif keys[pygame.K_F3]:
                        key_ticks = 0
                        is_debug_stats = not is_debug_stats

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
* Allow house upgrade with signifant resources required
* Allow tool recharge somehow
* Ability to construct single-use batteries (copper + iron?)
* Should blocks remember the percent dug they are?
* Exchange inventory for crafted items
* Player animations
* Lamps/Torch to expand sight line
* Fix player can move about 3-5 pixels inside a block while holding left/right

COMPLETED:
+ Background bushes for aesthetics
+ Fix bush heights so they don't extend underground
+ Extract 'ui_surf' out of draw_world() method
+ Don't allow block placement on top of House
+ Add more trees
+ Add charge level to tool, reduce charge level based on time digging, show charge in UI, 
+ Key bounce issue
+ Delete torches if a block is placed on them
+ Fix UI rendering for any screen size
+ Add offset_x and offset_y to tile images (for trees and urns)
+ Grass
+ Add Trees and wood drops
+ Give tiles/rooms background images (bricks, etc)
+ Destroying diagonal blocks without line-of-sight
+ Different materials required different time to dig
+ Line from player to crosshair when digging
+ Larger, scrolling world
+ Combine on_ground and jumping flags 
+ Stop space bar from repeat jumping
+ Caves
+ Rooms
+ Convert inventory array to dict
+ Limit sight line
+ Lamps to keep areas lit
"""
