import random
from itertools import cycle

import pygame

import gradient
from dig_game_colors import WHITE, BLACK, YELLOW, RED, CYAN
from dig_game_colors import HOLLOW_COLOR, MOUSE_BAD_COLOR, MOUSE_OK_COLOR, CHARGE_GOOD_COLOR, CHARGE_BAD_COLOR, \
    CHARGE_WARN_COLOR, UI_BG_COLOR
from dig_game_drops import screen
from dig_game_objects import Facing, Player, PLAYER_W, GIRL_RUN_ANIM, GIRL_IDLE_ANIM, \
    GIRL_JUMP_ANIM, GIRL_JUMP_ANIM_DELAY, GIRL_IDLE_ANIM_DELAY, GIRL_RUN_ANIM_DELAY, TORCH_ANIM_DELAY, GIRL_ATTACK_ANIM, \
    PLAYER_W2, PLAYER_H2, OGRE_IDLE_ANIM, IMG_OGRE_SHEET, OGRE_WALK_ANIM, OGRE_ATTACK_ANIM, OGRE_HURT_ANIM, \
    OGRE_DEATH_ANIM, EnemyAction, Ogre
from dig_game_objects import TORCH_ANIM, TORCH_W_SCALED, TORCH_H_SCALED, TORCH_DIST
from dig_game_tiles import Tiles, TILE_W, TILE_H, IMG_GRASS, IMG_VOLTAGE, IMG_BUSH_01, IMG_BUSH_02, \
    IMG_BUSH_03, IMG_BUSH_04
from dig_game_ui import build_ui
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

GRAVITY = 0.4
JUMP_VEL = -6.0
WALK_VEL = 5.0

WORLD_W = 50
WORLD_H = 50
LEVEL_W = 20
LEVEL_H = 20
main_world = [[Tiles.AIR for _ in range(WORLD_W)] for _ in range(WORLD_H)]

BEAM_COLORS = cycle([RED, YELLOW, CYAN])
beam_color = next(BEAM_COLORS)

jump_allowed = True
last_m_tile_x = last_m_tile_y = 0
torch_anim_step = torch_ticks = 0
tree_ticks = 0

# Convenience variables
screen_w = screen.get_width()
screen_h = screen.get_height()
screen_w2 = screen_w // 2
screen_h2 = screen_h // 2

house_ui_open = False
house_ui_w = int(screen_w * 0.6)
house_ui_h = int(screen_h * 0.6)
house_ui_x = (screen_w - house_ui_w) // 2
house_ui_y = (screen_h - house_ui_h) // 2

house_ui_surf = pygame.Surface((house_ui_w, house_ui_h))
ui_surf = pygame.Surface((screen.get_width(), TILE_H * 2))

enemies = []


def draw_world(world, bgs):
    global last_m_tile_x, last_m_tile_y
    global house_ui_surf, house_ui_open
    global torch_anim_step, torch_ticks, tree_ticks, beam_color

    screen.fill((8, 8, 8))

    screen_player_y = screen_h // 2

    offset_x = -player.x + screen_w2 + PLAYER_W2
    offset_y = -player.y + screen_h2

    """ Tile the player occupies """
    tile_x = constrain(int(player.x) // TILE_W, 0, WORLD_W - 1)
    tile_y = constrain(int(player.y) // TILE_H, 0, WORLD_H - 1)

    """ Background """
    # Sky
    pygame.draw.rect(screen, (60, 110, 175), (0, 600 - player.y - screen_h2, screen_w, screen_h2 + 150))
    # Transition to cave
    gradient.rect_gradient_h(screen, (60, 110, 175), (16, 16, 16), pygame.Rect(0, 600 - player.y + 150, screen_w, TILE_H))
    # Cave
    pygame.draw.rect(screen, (16, 16, 16), (0, 600 - player.y + 150 + TILE_H, screen_w, WORLD_H * TILE_H))

    # How many tiles can we render on screen
    num_w = (screen_w // TILE_W) // 2
    num_h = (screen_h // TILE_H) // 2
    render_tiles_x1 = constrain(tile_x - num_w - 5, 0, WORLD_W)
    render_tiles_x2 = constrain(tile_x + num_w + 3, 0, WORLD_W)
    render_tiles_y1 = constrain(tile_y - num_h - 1, 0, WORLD_H)
    render_tiles_y2 = constrain(tile_y + num_h + 1, 0, WORLD_H)

    # Should we grow a new tree?
    tree_ticks += dt
    if tree_ticks > 60000 and random.randrange(100) < 5:
        tree_ticks = 0
        # Select a random off-screen x-pos
        sanity_max = 20
        sanity = 0
        tree_x = random.randrange(WORLD_W)
        while render_tiles_x1 < tree_x < render_tiles_x2 or world[4][tree_x] != Tiles.AIR and sanity < sanity_max:
            tree_x = random.randrange(WORLD_W)
            sanity += 1
        if sanity == sanity_max:
            print("Could not grow a tree")
        else:
            print("Grew a new tree at x={}".format(tree_x))
            world[4][tree_x] = random.choice([Tiles.TREE_01, Tiles.TREE_02, Tiles.TREE_03, Tiles.TREE_04])

    ps_offset_x = player.x - screen_w2 - PLAYER_W2  # Player/Screen offset-x
    ps_offset_y = player.y - screen_h2

    # Render background tiles first
    for y in range(render_tiles_y1, render_tiles_y2):
        yy = y * TILE_H
        for x in range(render_tiles_x1, render_tiles_x2):
            xx = x * TILE_W
            if bgs[y][x] is not None:
                off_y = 0
                if bgs[y][x] in [IMG_BUSH_01, IMG_BUSH_02, IMG_BUSH_03, IMG_BUSH_04]:
                    off_y = -bgs[y][x].get_height() + TILE_H
                screen.blit(bgs[y][x], (xx - ps_offset_x, yy + off_y - ps_offset_y))

    for y in range(render_tiles_y1, render_tiles_y2):
        yy = y * TILE_H
        for x in range(render_tiles_x1, render_tiles_x2):
            xx = x * TILE_W
            tile = world[y][x].value
            if tile.img is not None:
                screen.blit(tile.img, (xx + tile.img_offset_x - ps_offset_x, yy + tile.img_offset_y - ps_offset_y))
                if y == 5:
                    screen.blit(IMG_GRASS, (xx - ps_offset_x, yy - ps_offset_y - TILE_H + 2))

    """ Circle around player """
    # The main circle around the player, once player is on tile_y >= 6 (cave darkness)
    temp_surf = pygame.Surface((screen_w, WORLD_H * TILE_H - (7 * TILE_H)))
    temp_surf.fill((8, 8, 8))
    temp_surf.set_colorkey((255, 0, 255))
    if tile_y >= 6:
        pygame.draw.circle(temp_surf, HOLLOW_COLOR, (screen_w2 + PLAYER_W2, (tile_y - 7) * TILE_H), 100)

    for torch in player.torches:
        screen.blit(TORCH_ANIM[torch_anim_step], (torch.x - (TORCH_W_SCALED // 2) - PLAYER_W2 + offset_x, torch.y - (TORCH_H_SCALED // 2) + offset_y))
        pygame.draw.circle(temp_surf, HOLLOW_COLOR, (torch.x - (TORCH_W_SCALED // 2) - PLAYER_W2 + offset_x, torch.y - (TORCH_H_SCALED // 2) - 300), torch.w)

        # Torch animation
        torch_ticks += dt
        if torch_ticks >= TORCH_ANIM_DELAY:
            torch_anim_step = (torch_anim_step + 1) % len(TORCH_ANIM)
            torch_ticks = 0

    if not is_debug_stats:
        screen.blit(temp_surf, (0, (TILE_H * 7) + offset_y))

    """ Mouse Movement """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    but1, but2, but3 = pygame.mouse.get_pressed()

    # Convert the mouse position to tile coordinates
    m_tile_x = int(constrain((mouse_x - offset_x) // TILE_W, -1, WORLD_W))
    m_tile_y = int(constrain((mouse_y - offset_y) // TILE_H, -1, WORLD_H))

    # Is the targeted block close enough to the player to dig it?
    m_color = MOUSE_BAD_COLOR
    if abs(tile_x - m_tile_x) < player.tool_dist and abs(tile_y - m_tile_y) < player.tool_dist:
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

    if (but1 and m_color == MOUSE_OK_COLOR and -1 < m_tile_x < WORLD_W and -1 < m_tile_y < WORLD_H
            and world[m_tile_y][m_tile_x].value.dig_level > 0):

        allow_dig = player.tool_charge > 0

        # Check if the targeted block is an unreachable diagonal
        up_tile = world[tile_y - 1][tile_x] if tile_y - 1 > -1 else Tiles.STONE
        down_tile = world[tile_y + 1][tile_x] if tile_y + 1 < WORLD_H else Tiles.STONE
        left_tile = world[tile_y][tile_x - 1] if tile_x - 1 > -1 else Tiles.STONE
        right_tile = world[tile_y][tile_x + 1] if tile_x + 1 < WORLD_W else Tiles.STONE

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
                player.beam_ticks += dt
                if player.beam_ticks > 30:
                    player.beam_ticks = 0
                    beam_color = next(BEAM_COLORS)
                pygame.draw.line(screen, beam_color, (player.x + offset_x + PLAYER_W2, player.y + offset_y + PLAYER_H2), (mouse_x, mouse_y), 2)

                # Cover the block with a translucent effect to indicate progress
                dug_h = TILE_H * (block_ticks - player.ticks) / block_ticks  # calculate the percentage dug
                temp_surf = pygame.Surface((TILE_W - 4, TILE_H - dug_h))
                temp_surf.set_alpha(128)
                temp_surf.fill((192, 0, 0))
                screen.blit(temp_surf, (m_tile_x * TILE_W + 2 + offset_x, m_tile_y * TILE_H + offset_y))

                # Reduce the tool charge by the time spent digging
                player.tool_charge -= dug_h / ((player.tool_level + 1) * 1000)

    # Place a block
    if (but3 and world[m_tile_y][m_tile_x] == Tiles.AIR
            and (0 < abs(tile_x - m_tile_x) < player.tool_dist or 0 < abs(tile_y - m_tile_y) < player.tool_dist)):

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
                        t_tile_x = (torch.x - PLAYER_W) // TILE_W
                        t_tile_y = (torch.y - PLAYER_H2) // TILE_H
                        if m_tile_x != t_tile_x or m_tile_y != t_tile_y:
                            new_torch_list.append(torch)
                    player.torches = new_torch_list

    """ House UI """
    if house_ui_open:
        screen.blit(house_ui_surf, (house_ui_x, house_ui_y))
    elif (but3 and world[m_tile_y][m_tile_x] in [Tiles.HOUSE_1, Tiles.HOUSE_2, Tiles.HOUSE_3, Tiles.HOUSE_4]
          and not house_ui_open):
        house_ui_open = True
        house_ui_surf = build_ui(house_ui_w, house_ui_h, player)
        screen.blit(house_ui_surf, (house_ui_x, house_ui_y))

    """ Player Movement """
    # Limit left/right movement
    left_tile = world[tile_y][tile_x - 1] if tile_x - 1 >= 0 else Tiles.STONE
    right_tile = world[tile_y][tile_x + 1] if tile_x + 1 < WORLD_W else Tiles.STONE

    # min_x = (tile_x - 1) * TILE_W + TILE_W - 3 if left_tile.value.is_solid else 0
    min_x = (tile_x - 1) * TILE_W + TILE_W if left_tile.value.is_solid else 0
    max_x = (tile_x + 1) * TILE_W - PLAYER_W if right_tile.value.is_solid else (WORLD_W - 1) * TILE_W + PLAYER_W

    # Calculate the player's new X and Y coords
    player.x = constrain(player.x + player.vel_x, min_x, max_x)
    player.y = constrain(player.y + player.vel_y, -100, WORLD_H * TILE_H)

    if player.on_ground:
        target_y = tile_y
        while target_y < WORLD_H and not world[target_y][tile_x].value.is_solid:
            player.on_ground = False
            target_y += 1
        target_y = constrain((target_y - 1) * TILE_H, 0, WORLD_H * TILE_H)

        # while tile_y < WORLD_H and not world[tile_y][tile_x].value.is_solid:
        #     player.on_ground = False
        #     tile_y += 1
        # target_y = constrain((tile_y - 1) * TILE_H, 0, WORLD_H * TILE_H)

        # Is player falling?
        if not player.on_ground:
            player.vel_y += GRAVITY
            player.y += player.vel_y

        # Stop falling
        if player.y >= target_y:
            player.on_ground = True
            player.vel_y = 0.0
            player.y = target_y

    # Prepare to draw animations
    player.anim_ticks += dt
    player_img_offset_x = 10
    player_img_offset_y = -2

    # Jumping
    if not player.on_ground:
        player.vel_y += GRAVITY

        # Check for a max jump height if there is a tile above the player
        min_y = -100
        if tile_y > 0 and world[tile_y - 1][tile_x].value.is_solid:
            min_y = tile_y * TILE_H
        if player.y <= min_y:
            player.y = min_y

        # Find where player should land
        target_y = tile_y
        while target_y < WORLD_H and not world[target_y][tile_x].value.is_solid:
            player.on_ground = False
            target_y += 1
        target_y = constrain((target_y - 1) * TILE_H, 0, WORLD_H * TILE_H)

        # while tile_y < WORLD_H and not world[tile_y][tile_x].value.is_solid:
        #     player.on_ground = False
        #     tile_y += 1
        # target_y = constrain((tile_y - 1) * TILE_H, 0, WORLD_H * TILE_H)

        # Stop jumping, player has landed
        if player.y >= target_y:
            player.on_ground = True
            player.vel_y = 0.0
            player.y = target_y

        # Draw jumping animation
        player.anim_ticks += dt
        player.anim_step = constrain(player.anim_step, 0, len(GIRL_JUMP_ANIM) - 1)
        sprite = GIRL_JUMP_ANIM[player.anim_step]
        if player.facing == Facing.LEFT:
            sprite = pygame.transform.flip(GIRL_JUMP_ANIM[player.anim_step], True, False)
        screen.blit(sprite, (screen_w2 - player_img_offset_x, screen_player_y - player_img_offset_y))

        if player.anim_ticks >= GIRL_JUMP_ANIM_DELAY:
            player.anim_ticks = 0
            player.anim_step = (player.anim_step + 1) % len(GIRL_JUMP_ANIM)

    # Not jumping, walking
    else:
        if not house_ui_open:
            if but1:
                # Digging
                sprite = GIRL_ATTACK_ANIM[len(GIRL_ATTACK_ANIM) - 1]
                if player.facing == Facing.LEFT:
                    sprite = pygame.transform.flip(sprite, True, False)
                screen.blit(sprite, (screen_w2 - player_img_offset_x, screen_player_y - player_img_offset_y))

            else:
                if int(player.vel_x) == 0:
                    player.anim_step = constrain(player.anim_step, 0, len(GIRL_IDLE_ANIM) - 1)
                    sprite = GIRL_IDLE_ANIM[player.anim_step]
                    if player.facing == Facing.LEFT:
                        sprite = pygame.transform.flip(sprite, True, False)
                    screen.blit(sprite, (screen_w2 - player_img_offset_x, screen_player_y - player_img_offset_y))

                    if player.anim_ticks >= GIRL_IDLE_ANIM_DELAY:
                        player.anim_ticks = 0
                        player.anim_step = (player.anim_step + 1) % len(GIRL_IDLE_ANIM)
                else:
                    player.anim_step = constrain(player.anim_step, 0, len(GIRL_RUN_ANIM) - 1)
                    sprite = GIRL_RUN_ANIM[player.anim_step]
                    if player.facing == Facing.LEFT:
                        sprite = pygame.transform.flip(sprite, True, False)
                    screen.blit(sprite, (screen_w2 - player_img_offset_x, screen_player_y - player_img_offset_y))

                    delay = GIRL_RUN_ANIM_DELAY
                    if player.vel_x < WALK_VEL:
                        delay = GIRL_RUN_ANIM_DELAY * 2

                    if player.anim_ticks >= delay:
                        player.anim_ticks = 0
                        player.anim_step = (player.anim_step + 1) % len(GIRL_RUN_ANIM)

    player.x = round(player.x, 3)
    player.y = round(player.y, 3)

    """ Enemies """

    for enemy in enemies:
        enemy.ticks += dt
        anim_list = []
        anim_delay = 200

        if enemy.action == EnemyAction.IDLE:
            anim_list = enemy.idle_anim
            anim_delay = 150
        elif enemy.action == EnemyAction.WALK:
            anim_list = enemy.walk_anim
            anim_delay = 200

        if enemy.ticks >= anim_delay:
            enemy.ticks = 0
            enemy.anim_step = (enemy.anim_step + 1) % len(anim_list)

        frame = anim_list[enemy.anim_step]
        if enemy.facing == Facing.RIGHT:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (enemy.x + offset_x, enemy.y + offset_y))

    """ Render UI """
    # Inventory
    FONT_EMOJI_SM.set_bold(True)
    ui_surf.fill(UI_BG_COLOR)
    ui_surf_w = ui_surf.get_width()
    ui_surf_h = ui_surf.get_height()
    ui_y = screen_h - TILE_H * 2

    for inv_i, key in enumerate(player.inv_dict.keys()):
        inv_x = TILE_W * inv_i + 5
        # Item image
        ui_surf.blit(key.value.drop.value.img, (inv_x, 32))
        # Item name
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
    pygame.draw.rect(ui_surf, charge_color, (ui_surf_w - 110, 4, 100, ui_surf_h - 8), 0, 10)
    txt_charge = FONT_EMOJI_MD.render("{}%".format(int(player.tool_charge)), True, BLACK).convert_alpha()
    txt_charge_x = ui_surf_w - 55 - (txt_charge.get_width() // 2)
    ui_surf.blit(txt_charge, (txt_charge_x + 1, 10))
    ui_surf.blit(FONT_EMOJI_MD.render("{}%".format(int(player.tool_charge)), True, WHITE).convert_alpha(), (txt_charge_x, 9))
    ui_surf.blit(IMG_VOLTAGE, (ui_surf.get_width() - 80, 40))

    FONT_EMOJI_SM.set_bold(False)
    screen.blit(ui_surf, (0, ui_y))

    """ Debug stats (toggle with F3) """
    if is_debug_stats:
        player_rect = player.get_rect()
        player_rect.x += offset_x
        player_rect.y += offset_y
        pygame.draw.rect(screen, "#00FF00", player_rect, 1)  # Player hitbox

        stats = FONT_EMOJI_SM.render("px, py: {}, {} | tile_x, y: {}, {}".format(player.x, player.y, tile_x, tile_y), True, WHITE).convert_alpha()
        stat2 = FONT_EMOJI_SM.render("m_tile_x, y: {}, {} @ {}".format(m_tile_x, m_tile_y, world[m_tile_y][m_tile_x]), True, WHITE).convert_alpha()
        stat3 = FONT_EMOJI_SM.render("left: {}, right: {}, min_x: {}, max_x: {}".format(left_tile, right_tile, min_x, max_x), True, WHITE)
        screen.blit(stats, (400, screen_h - 80))
        screen.blit(stat2, (400, screen_h - 55))
        screen.blit(stat3, (400, screen_h - 25))


if __name__ == '__main__':
    main_world, main_bg = generate_world(WORLD_W, WORLD_H)
    player = Player()

    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
    pygame.key.set_repeat(20, FPS)

    enemies.append(Ogre(200, 300))

    while is_running:
        draw_world(main_world, main_bg)

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

                if keys[pygame.K_SPACE] and player.on_ground and jump_allowed:
                    jump_allowed = False
                    player.vel_y = JUMP_VEL
                    player.anim_ticks = 0
                    player.anim_step = 0
                    player.on_ground = False

            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_d, pygame.K_LEFT, pygame.K_RIGHT]:
                    player.vel_x = 0.0
                    player.anim_ticks = 0
                    player.anim_step = 0

                elif event.key == pygame.K_ESCAPE:
                    # Close the House UI if it's open
                    if house_ui_open:
                        house_ui_open = False

                elif event.key == pygame.K_t:
                    player.torches.append(pygame.Rect(player.x + PLAYER_W, player.y + PLAYER_H2, TORCH_DIST, TORCH_DIST))

                elif event.key == pygame.K_y:
                    player.tool_charge = 100

                elif event.key == pygame.K_u:
                    player.tool_dist += 1

                elif event.key == pygame.K_F3 or event.key == pygame.K_F4:
                    is_debug_stats = not is_debug_stats

                if event.key == pygame.K_SPACE and not jump_allowed:
                    jump_allowed = True
                    player.vel_y = 0
                    player.anim_ticks = 0
                    player.anim_step = 0

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:
                    player.inv_selected -= 1
                elif event.y < 0:
                    player.inv_selected += 1
                player.inv_selected = constrain(player.inv_selected, 0, len(player.inv_dict.keys()) - 1)

        dt = clock.tick(FPS)

    pygame.quit()

"""
TODO:
* Enemies
* Fix placing blocks when jumping
* Ore vein frequency needs to be based on level size
* Add House UI
* Add Attack/Run animation

MAYBES:
* Way to increase jump height?
* Should blocks remember the percent dug they are? This will increase memory requirement. Maybe just remember last 20 or so.
* Wrap world?
* Fix detection of line-of-sight when digging large distances

COMPLETED:
+ Place ores in veins instead of randomly
+ Randomly grow trees
+ Cave darkness is VERY slow on large maps. Try making a smaller Surface and only render immediately around player
+ Spamming jump makes player "fly"
+ Torches are not deleted when a block is place on them
+ Jump height based on time the space bar is held
+ Game allows digging at y > max depth
+ Game gets crazy slow at y=27
+ Fix game allows digging at x < 0
+ Use a different animation when digging (right now it's using IDLE_ANIM, try ATTACK)
+ Allow LARGER worlds by limiting the tiles rendered
+ Limit digging once tool charge reaches 0
+ Fix player can move about 3-5 pixels inside a block while holding left/right
+ Player animations
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
