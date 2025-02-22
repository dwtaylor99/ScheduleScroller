
# New idea: draw a line from player to mouse position. If all tiles crossed are AIR tiles, allow digging.
start_x = int(player.x + offset_x)
start_y = int(player.y + PLAYER_H2 + offset_y)
# start_x = int(player.x + PLAYER_W2 + offset_x)
# start_y = int(player.y + PLAYER_H2 + offset_y)
adj_x = 1 if start_x < mouse_x else -1
adj_y = 1 if start_y < mouse_y else -1
ray_x1 = tile_x * TILE_W + int(offset_x)
ray_y1 = tile_y * TILE_H + int(offset_y)
ray_x2 = ray_x1 + int(abs(start_x - mouse_x) * adj_x)
ray_y2 = ray_y1 - PLAYER_H2 + int(abs(start_y - mouse_y) * adj_y)
pygame.draw.line(screen, (0, 200, 200), (start_x, start_y), (mouse_x, mouse_y))
for qy in range(ray_y1, ray_y2, TILE_H * adj_y):
    for qx in range(ray_x1, ray_x2, TILE_W * adj_x):
        ray_rect = pygame.Rect(qx, qy, TILE_W, TILE_H)
        if ray_rect.clipline((start_x, start_y), (mouse_x, mouse_y)):
            pygame.draw.rect(screen, (200, 200, 0), ray_rect, 1)
        # else:
        #     pygame.draw.rect(screen, (0, 0, 200), ray_rect, 1)

if (but1 and m_color == MOUSE_OK_COLOR and -1 < m_tile_x < WORLD_W and -1 < m_tile_y < WORLD_H
        and world[m_tile_y][m_tile_x].value.dig_level > 0):

    allow_dig = player.tool_charge > 0
    """
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
    """
    # New idea: draw a line from player to mouse position. If all tiles crossed are AIR tiles, allow digging.
    # start_x = int(player.x + PLAYER_W2 + offset_x)
    # start_y = int(player.y + PLAYER_H2 + offset_y)
    # adj_x = 1 if start_x < mouse_x else -1
    # adj_y = 1 if start_y < mouse_y else -1
    # ray_x1 = tile_x * TILE_W + int(offset_x)
    # ray_y1 = tile_y * TILE_H + int(offset_y)
    # ray_x2 = ray_x1 + int(abs(start_x - mouse_x) * adj_x)
    # ray_y2 = ray_y1 + int(abs(start_y - mouse_y) * adj_y)
    # pygame.draw.line(screen, (0, 200, 200), (start_x, start_y), (mouse_x, mouse_y))
    for qy in range(ray_y1, ray_y2, TILE_H * adj_y):
        for qx in range(ray_x1, ray_x2, TILE_W * adj_x):
            ray_rect = pygame.Rect(qx, qy, TILE_W, TILE_H)
            if ray_rect.clipline((start_x, start_y), (mouse_x, mouse_y)):
                # Convert the intersected Rects to tiles
                intersected_tile_x = (qx - int(offset_x)) // TILE_W
                intersected_tile_y = (qy - int(offset_y)) // TILE_H
                if world[intersected_tile_y][intersected_tile_x].value.is_solid:
                    allow_dig = False
                    break