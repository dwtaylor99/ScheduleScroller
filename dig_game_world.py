import random

from dig_game_tiles import Tiles, IMG_BLUE_BRICKS, IMG_RED_BRICKS, IMG_GRAY_BRICKS, IMG_GREEN_VINES, IMG_BUSH_04, \
    IMG_BUSH_03, IMG_BUSH_02, IMG_BUSH_01
from dig_game_utils import constrain


def add_vein(world, ore, ox, oy, length):
    ore_x = ox
    ore_y = oy

    world_w = len(world[0])
    world_h = len(world)

    for _ in range(length):
        direc = random.randint(1, 4)
        if direc == 1:
            ore_y -= 1
        elif direc == 2:
            ore_y += 1
        elif direc == 3:
            ore_x -= 1
        elif direc == 4:
            ore_x += 1
        ore_x = constrain(ore_x, 0, world_w - 1)
        ore_y = constrain(ore_y, 0, world_h - 1)
        # print(ore_x, ore_y)
        world[ore_y][ore_x] = ore


def generate_world(level_width, level_height):
    world = [[Tiles.AIR for _ in range(level_width)] for _ in range(level_height)]
    background = [[None for _ in range(level_width)] for _ in range(level_height)]

    overworld = 5
    level_1 = int(level_height * 0.25) + overworld
    level_2 = int(level_height * 0.25) + level_1
    level_3 = int(level_height * 0.25) + level_2

    for y in range(level_height):
        for x in range(level_width):
            # rn = random.randrange(100) + y
            rn = random.randrange(100)

            # Top 5 levels are Air so player has some build height
            if y < overworld:
                world[y][x] = Tiles.AIR

            # Add trees
            if y == overworld - 1:
                if 0 <= rn < 50 and x < level_width - 5:
                    background[y][x] = random.choice([IMG_BUSH_01, IMG_BUSH_02, IMG_BUSH_03, IMG_BUSH_04])
                if 50 <= rn < 75:
                    world[y][x] = random.choice([Tiles.TREE_01, Tiles.TREE_02, Tiles.TREE_03, Tiles.TREE_04])

            if overworld <= y < level_1:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.DIRT
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.STONE
                elif 80 <= rn < 100:
                    world[y][x] = Tiles.CLAY

            # Fill rest of the world with stone
            if level_1 <= y < level_height:
                world[y][x] = Tiles.STONE

    ore_density = int(level_width * level_height * 0.005)
    print(ore_density)

    # Add veins of dirt
    # Add veins of clay

    # Add veins of coal
    for _ in range(random.randrange(ore_density)):
        x = random.randrange(level_width)
        y = random.randrange(level_1, level_2)
        add_vein(world, Tiles.COAL, x, y, random.randrange(4, 20))

    # Add veins of copper
    for _ in range(random.randrange(ore_density)):
        x = random.randrange(level_width)
        y = random.randrange(level_1, level_2)
        add_vein(world, Tiles.COPPER, x, y, random.randrange(4, 20))

    # Add veins of iron
    for _ in range(random.randrange(ore_density)):
        x = random.randrange(level_width)
        y = random.randrange(level_2, level_3)
        add_vein(world, Tiles.IRON, x, y, random.randrange(6, 20))

    # Add veins of silver
    for _ in range(random.randrange(ore_density)):
        x = random.randrange(level_width)
        y = random.randrange(level_2, level_3)
        add_vein(world, Tiles.SILVER, x, y, random.randrange(6, 20))

    # Add veins of gold
    for _ in range(random.randrange(ore_density)):
        x = random.randrange(level_width)
        y = random.randrange(level_3, level_height)
        add_vein(world, Tiles.GOLD, x, y, random.randrange(3, 20))

    # Add veins of diamond
    for _ in range(random.randrange(ore_density)):
        x = random.randrange(level_width)
        y = random.randrange(level_3, level_height)
        add_vein(world, Tiles.DIAMOND, x, y, random.randrange(1, 10))

    # Place a house on the left side of level 5 and overwrite whatever is there
    world[4][random.randrange(2, min(level_width // 4, 50))] = Tiles.HOUSE_1

    # Add some caves
    for cave_i in range(random.randint(1, 8)):
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
        room_reward = random.choice([Tiles.REWARD_URN, Tiles.REWARD_CHALICE])

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


def generate_world_old(level_width, level_height):
    world = [[Tiles.AIR for _ in range(level_width)] for _ in range(level_height)]
    background = [[None for _ in range(level_width)] for _ in range(level_height)]

    overworld = 5
    level_1 = int(level_height * 0.25) + overworld
    level_2 = int(level_height * 0.25) + level_1
    level_3 = int(level_height * 0.25) + level_2

    for y in range(level_height):
        for x in range(level_width):
            # rn = random.randrange(100) + y
            rn = random.randrange(100)

            # Top 5 levels are Air so player has some build height
            if y < overworld:
                world[y][x] = Tiles.AIR

            # Add trees
            if y == overworld - 1:
                if 0 <= rn < 50 and x < level_width - 5:
                    background[y][x] = random.choice([IMG_BUSH_01, IMG_BUSH_02, IMG_BUSH_03, IMG_BUSH_04])
                if 50 <= rn < 75:
                    world[y][x] = random.choice([Tiles.TREE_01, Tiles.TREE_02, Tiles.TREE_03, Tiles.TREE_04])

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

            elif level_3 <= y < level_height:
                if 0 <= rn < 60:
                    world[y][x] = Tiles.STONE
                elif 60 <= rn < 80:
                    world[y][x] = Tiles.SILVER
                elif 80 <= rn < 90:
                    world[y][x] = Tiles.GOLD
                elif 90 <= rn < 100:
                    world[y][x] = Tiles.DIAMOND

    # Place a house on level 5 and overwrite whatever is there
    world[4][random.randrange(level_width // 4)] = Tiles.HOUSE_1

    # Add some caves
    for cave_i in range(random.randint(1, 8)):
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
        room_reward = random.choice([Tiles.REWARD_URN, Tiles.REWARD_CHALICE])

        for jj in range(room_size):
            for ii in range(room_size):
                yyy = constrain(room_y + jj, 0, level_height - 1)
                xxx = constrain(room_x + ii, overworld + 2, level_width - 1)
                world[yyy][xxx] = room_tile
                background[yyy][xxx] = room_bg
            if jj == room_size - 1:
                world[room_y + jj][room_x] = room_reward
                background[room_y + jj][room_x] = room_bg

    world[0][0] = Tiles.DIAMOND

    return world, background


if __name__ == '__main__':
    generate_world(40, 50)
