import random

from dig_game_tiles import Tiles, IMG_BLUE_BRICKS, IMG_RED_BRICKS, IMG_GRAY_BRICKS, IMG_GREEN_VINES
from dig_game_utils import constrain


def generate_world(level_width, level_height):
    world = [[Tiles.AIR for _ in range(level_width)] for _ in range(level_height)]
    background = [[None for _ in range(level_width)] for _ in range(level_height)]

    overworld = 5
    level_1 = int(level_height * 0.25) + overworld
    level_2 = int(level_height * 0.25) + level_1 + overworld
    level_3 = int(level_height * 0.25) + level_2 + overworld
    level_4 = int(level_height * 0.25) + level_3 + overworld

    for y in range(level_height):
        for x in range(level_width):
            # rn = random.randrange(100) + y
            rn = random.randrange(100)

            # Top 5 levels are Air so player has some build height
            if y < overworld:
                world[y][x] = Tiles.AIR

            # Add trees
            if y == overworld - 1:
                if rn < 25:
                    world[y][x] = random.choice([Tiles.TREE_01, Tiles.TREE_02])

            if overworld <= y < level_1:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.DIRT
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.STONE
                elif 80 <= rn < 90:
                    world[y][x] = Tiles.CLAY
                elif 90 <= rn < 100:
                    world[y][x] = Tiles.COAL

            elif level_1 <= y < level_2:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.STONE
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.COPPER
                elif 80 <= rn < 90:
                    world[y][x] = Tiles.COAL
                elif 90 <= rn < 100:
                    world[y][x] = Tiles.IRON

            elif level_2 <= y < level_3:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.STONE
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.IRON
                elif 80 <= rn < 90:
                    world[y][x] = Tiles.SILVER
                elif 90 <= rn < 100:
                    world[y][x] = Tiles.GOLD

            elif level_3 <= y < level_4:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.STONE
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.SILVER
                elif 80 <= rn < 90:
                    world[y][x] = Tiles.GOLD
                elif 90 <= rn < 100:
                    world[y][x] = Tiles.DIAMOND

    # Add some caves
    for cave_i in range(random.randint(1, 3)):
        cave_len = random.randint(10, 20)  # how long is the cave?
        cave_x = random.randint(3, 10)  # where to start the cave, x position
        cave_y = random.randint(7, 14)  # where to start the cave, y position
        cave_bg = random.choice([IMG_GREEN_VINES])
        for _ in range(cave_len):
            world[cave_y][cave_x] = Tiles.AIR
            background[cave_y][cave_x] = cave_bg
            direc = random.randint(1, 4)
            if direc == 1:
                cave_y -= 1
            elif direc == 2:
                cave_y += 1
            elif direc == 3:
                cave_x -= 1
            elif direc == 4:
                cave_x += 1
            cave_x = constrain(cave_x, 0, level_width)
            cave_y = constrain(cave_y, overworld + 2, level_height)

    # Add some cave rooms
    for room_i in range(random.randint(1, 3)):
        room_x = random.randrange(level_width - 4) + 2
        room_y = random.randrange(level_height // 2) + (level_height // 2) - 3
        room_size = random.randint(2, 4)

        room_bg = random.choice([IMG_BLUE_BRICKS, IMG_RED_BRICKS, IMG_GRAY_BRICKS])
        room_tile = Tiles.AIR
        room_reward = Tiles.REWARD_URN

        for jj in range(room_size):
            for ii in range(room_size):
                yyy = constrain(room_y + jj, 0, level_height - 1)
                xxx = constrain(room_x + ii, overworld + 2, level_width - 1)
                world[yyy][xxx] = room_tile
                background[yyy][xxx] = room_bg
            if jj == room_size - 1:
                world[room_y + jj][room_x] = room_reward
                background[room_y + jj][room_x] = room_bg

    return world, background


if __name__ == '__main__':
    generate_world(40, 50)
