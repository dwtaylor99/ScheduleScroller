import random

from dig_game_tiles import Tiles
from dig_game_utils import constrain


def generate_world(level_width, level_height):
    world = [[Tiles.AIR for _ in range(level_width)] for _ in range(level_height)]

    """
    Plan:
    upper levels should be dirt, clay, stone
    gradually add more valuable ores: copper, iron, silver, gold, diamond
    
    split world height into 4 regions
    """

    level_1 = int(level_height * 0.25)
    level_2 = int(level_height * 0.25) + level_1
    level_3 = int(level_height * 0.25) + level_1 + level_2
    level_4 = int(level_height * 0.25) + level_1 + level_2 + level_3

    for y in range(level_height):
        for x in range(level_width):
            # rn = random.randrange(100) + y
            rn = random.randrange(100)

            if y == 0:
                world[y][x] = Tiles.AIR

            if 1 <= y < level_1:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.DIRT
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.STONE
                elif 80 <= rn < 90:
                    world[y][x] = Tiles.CLAY
                elif 90 <= rn < 100:
                    world[y][x] = Tiles.COPPER

            elif level_1 <= y < level_2:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.STONE
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.CLAY
                elif 80 <= rn < 90:
                    world[y][x] = Tiles.COPPER
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
        for _ in range(cave_len):
            world[cave_y][cave_x] = Tiles.AIR
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
            cave_y = constrain(cave_y, 0, level_height)

    # Add some cave rooms
    for room_i in range(random.randint(1, 3)):
        room_x = random.randrange(level_width - 4) + 2
        room_y = random.randrange(level_height // 2) + (level_height // 2) - 3

        room_size = random.randint(2, 4)
        for jj in range(room_size):
            for ii in range(room_size):
                yyy = constrain(room_y + jj, 0, level_height - 1)
                xxx = constrain(room_x + ii, 0, level_width - 1)
                world[yyy][xxx] = Tiles.AIR
            if jj == room_size - 1:
                world[room_y + jj][room_x] = Tiles.REWARD_URN

    return world


def generate_world1(level_width, level_height):
    # world = [[Tiles.AIR for ix in range(level_width)] for iy in range(level_height)]
    world = [[Tiles.AIR for _ in range(level_width)] for _ in range(level_height)]

    for y in range(level_height):
        for x in range(level_width):
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

    # Add some caves
    for cave_i in range(random.randint(1, 3)):
        cave_len = random.randint(10, 20)  # how long is the cave?
        cave_x = random.randint(3, 10)  # where to start the cave, x position
        cave_y = random.randint(7, 14)  # where to start the cave, y position
        for _ in range(cave_len):
            world[cave_y][cave_x] = Tiles.AIR
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
            cave_y = constrain(cave_y, 0, level_height)

    # Add some cave rooms
    for room_i in range(random.randint(1, 3)):
        room_x = random.randrange(level_width - 4) + 2
        room_y = random.randrange(level_height // 2) + (level_height // 2) - 3

        room_size = random.randint(2, 4)
        for jj in range(room_size):
            for ii in range(room_size):
                yyy = constrain(room_y + jj, 0, level_height - 1)
                xxx = constrain(room_x + ii, 0, level_width - 1)
                world[yyy][xxx] = Tiles.AIR
            if jj == room_size - 1:
                world[room_y + jj][room_x] = Tiles.REWARD_URN

    return world
