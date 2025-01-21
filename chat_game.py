"""
* Generate a random grid

* Populate map:
    Zombies
    Treasure
        map,
        weapons: fists, bat, nightstick, katana, sword, machete, knife, axe, sledgehammer
    Buildings
        house,
        gas station,
        grocery store

* Chat can give commands:
    north, south, east, west
    attack, run, open (chest)
    etc
"""
import random
from enum import Enum

import pygame.display

import gradient
from colors import BLACK, WHITE, DK_GRAY, LT_GREEN, BLUE, MED_BLUE, PALE_BLUE
from game_weapons import *


pygame.init()

WIDTH = 960
HEIGHT = 540
FPS = 60

GRID_W = 10
GRID_H = 10
TILE_W = WIDTH // GRID_W // 1.5
TILE_H = HEIGHT // GRID_H
STATUS_X = int(GRID_W * TILE_W)
STATUS_W = WIDTH - STATUS_X

FONT = pygame.font.Font("fonts/HandelGo.ttf", 28)
BG_COLOR = (109, 150, 90)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
is_running = True
dt = 0
grid = []
hero_turn = True

IMG_TREES = pygame.image.load('images/game/trees02.png').convert_alpha()
IMG_TREES.set_clip((20, 0, 120, 150))
TREE_01 = IMG_TREES.subsurface(IMG_TREES.get_clip())

IMG_TREES.set_clip((150, 0, 100, 150))
TREE_02 = IMG_TREES.subsurface(IMG_TREES.get_clip())

IMG_TREES.set_clip((270, 0, 100, 150))
TREE_03 = IMG_TREES.subsurface(IMG_TREES.get_clip())

IMG_TREES.set_clip((380, 0, 100, 150))
TREE_04 = IMG_TREES.subsurface(IMG_TREES.get_clip())

tree_list = [TREE_01, TREE_02, TREE_03, TREE_04]
tree_pos_list = []

txt_fight = FONT.render("(F)ight", True, WHITE)
txt_item = FONT.render("(I)tem", True, WHITE)
txt_ability = FONT.render("(A)bility", True, WHITE)
txt_run = FONT.render("(R)un", True, WHITE)


class Action(Enum):
    NONE = 0
    FIGHT = 1
    ITEM = 2
    ABILITY = 3
    RUN = 4


class GameMode(Enum):
    MAP = 1
    BATTLE = 2
    TREASURE = 3
    BUILDING = 4
    GAME_OVER = 99


class GridItem:
    """Base class of all grid items"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.revealed = False

    def __repr__(self):
        return ""


class GridItemEmpty(GridItem):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __repr__(self):
        return " "


class Building(GridItem):
    def __init__(self, x, y):
        super().__init__(x, y)

    def __repr__(self):
        return "B"


class Item:
    def __init__(self, name):
        self.name = name
        self.use_in_battle = False

    def use(self, who):
        pass


class FirstAid(Item):
    def __init__(self):
        super().__init__("First Aid")
        self.use_in_battle = True

    def use(self, who):
        who.health += 10
        if who.health > who.max_health:
            who.health = who.max_health


class Hero(GridItem):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/idle01.png"), 2.0).convert_alpha()
        self.health = 10
        self.max_health = 10
        self.attack = 1
        self.weapon = Fists()
        self.hit_chance = 50
        self.run_chance = 80
        self.anim_step = 1
        self.max_inventory = 10
        self.inventory = [FirstAid(), FirstAid(), FirstAid()]

    def __repr__(self):
        return "H"


class Zombie(GridItem):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/zomb01.png"), 2.0).convert_alpha()
        self.health = 5
        self.damage = 1
        self.hit_chance = 60
        self.run_chance = 0
        self.anim_step = 1

        self.hurt_cycle = [
            pygame.transform.smoothscale_by(pygame.image.load("images/game/zomb_hurt01.png"), 2.0).convert_alpha(),
            pygame.transform.smoothscale_by(pygame.image.load("images/game/zomb_hurt02.png"), 2.0).convert_alpha(),
            pygame.transform.smoothscale_by(pygame.image.load("images/game/zomb_hurt03.png"), 2.0).convert_alpha(),
            pygame.transform.smoothscale_by(pygame.image.load("images/game/zomb_hurt04.png"), 2.0).convert_alpha()
        ]

    def __repr__(self):
        return "Z"


class Treasure(GridItem):
    def __init__(self, x, y):
        super().__init__(x, y)

    def open(self, who: Hero):
        if random.randint(1, 100) < 10:
            # Trapped Chest!
            pass
        else:
            rand = random.randint(1, 100)
            if rand < 10:
                pass

    def __repr__(self):
        return "T"


def print_grid():
    # Print out the grid
    for y in range(GRID_H):
        for x in range(GRID_W):
            print(grid[y][x], end='')
        print()


def find_empty():
    y = random.randrange(GRID_H)
    x = random.randrange(GRID_W)
    while type(grid[y][x]) is not GridItemEmpty or (x == hero.x and y == hero.y):
        y = random.randrange(GRID_H)
        x = random.randrange(GRID_W)
    return x, y


def setup():
    global grid, hero, game_mode

    game_mode = GameMode.MAP

    # Initialize the Grid to all Empty spaces
    for y in range(GRID_H):
        inner_array = []
        for x in range(GRID_W):
            inner_array.append(GridItemEmpty(x, y))
        grid.append(inner_array)

    # Place a Hero on the last row
    x = random.randrange(GRID_W)
    y = GRID_H - 1
    hero = Hero(x, y)
    grid[y][x].revealed = True

    # Place buildings
    for _ in range(6):
        x, y = find_empty()
        grid[y][x] = Building(x, y)

    # Place some zombies
    for _ in range(15):
        x, y = find_empty()
        grid[y][x] = Zombie(x, y)

    # Place some treasure
    for _ in range(6):
        x, y = find_empty()
        grid[y][x] = Treasure(x, y)

    # print_grid()
    pos_x = -20
    pos_y = 60
    for _ in range(30):
        tree_pos_list.append({
            "img": random.choice(tree_list),
            "x": pos_x,
            "y": pos_y
        })
        pos_x += random.randint(20, 50)
        pos_y += random.randint(-5, 5)


def draw_game_over():
    pad = 50
    w = WIDTH - (pad * 2)
    h = HEIGHT - (pad * 2)
    surf = pygame.Surface((w, h))
    surf.fill(BLACK)
    surf.set_colorkey(BLACK)

    # Background
    pygame.draw.rect(surf, DK_GRAY, (0, 0, w, h), 0, 10)
    # Border
    pygame.draw.rect(surf, WHITE, (0, 0, w, h), 4, 10)

    t = FONT.render("Game Over", True, WHITE)
    surf.blit(t, ((w - t.get_width()) // 2, (h - t.get_height()) // 2))

    screen.blit(surf, (pad, pad))


def draw_screen():
    screen.fill(BLACK)

    # Draw the grid
    for y in range(GRID_H):
        for x in range(GRID_W):
            tile_color = DK_GRAY
            if grid[y][x].revealed:
                tile_color = LT_GREEN
            pygame.draw.rect(screen, tile_color, (x * TILE_W, y * TILE_H, TILE_W, TILE_H))
            pygame.draw.rect(screen, DK_GRAY, (x * TILE_W, y * TILE_H, TILE_W, TILE_H), 1)
            t = FONT.render(str(grid[y][x]), True, WHITE)
            screen.blit(t, (x * TILE_W + 5, y * TILE_H + 5))

    t = FONT.render(str(hero), True, WHITE)
    screen.blit(t, (hero.x * TILE_W + (TILE_W - 24), hero.y * TILE_H + 5))


def draw_status():
    gradient.rect_gradient_h(screen, MED_BLUE, BLUE, pygame.Rect(STATUS_X, 0, STATUS_W, HEIGHT))
    pygame.draw.rect(screen, WHITE, (STATUS_X, 0, STATUS_W, HEIGHT), 4, 10)

    y = 20
    screen.blit(FONT.render("HP / MAX:", True, WHITE), (STATUS_X + 20, y))
    y += 30
    screen.blit(FONT.render("{} / {}".format(str(hero.health), str(hero.max_health)),
                            True, WHITE), (STATUS_X + 20, y))

    y += 60
    screen.blit(FONT.render("Weapon / Damage:", True, WHITE), (STATUS_X + 20, y))
    y += 30
    screen.blit(FONT.render("{} / {}".format(hero.weapon.name, str(hero.weapon.base_damage)),
                            True, WHITE), (STATUS_X + 20, y))


def draw_event_window():
    pad = 50
    w = STATUS_X - (pad * 2)
    h = HEIGHT - (pad * 2)
    surf = pygame.Surface((w, h))
    surf.fill(BLACK)
    surf.set_colorkey(BLACK)

    # Background
    pygame.draw.rect(surf, BG_COLOR, (0, 0, w, h), 0, 10)

    # Sky
    pygame.draw.rect(surf, PALE_BLUE, (0, 0, w, 10), 0, 0, 10, 10)
    gradient.rect_gradient_h(surf, PALE_BLUE, (180, 220, 190), pygame.Rect(0, 10, w, 120))

    # Dark green behind trees
    gradient.rect_gradient_h(surf, (10, 80, 30), DK_GRAY, pygame.Rect(0, 120, w, 70))

    # Trees in the distance
    for tree in tree_pos_list:
        surf.blit(tree['img'], (tree['x'], tree['y']))

    # Border
    pygame.draw.rect(surf, WHITE, (0, 0, w, h), 4, 10)

    # Draw the event window onto the main screen
    screen.blit(surf, (pad, pad))

    if hero.anim_step == 1:
        x = 60
        zx = w - 100
        while x <= 150:
            pygame.draw.rect(screen, BG_COLOR, (int(x), 300, 128, 128))
            screen.blit(hero.img, (x, 300))

            pygame.draw.rect(screen, BG_COLOR, (int(zx), 300, 128, 128))
            screen.blit(zombie.img, (zx, 300))

            pygame.display.flip()
            x += 0.05
            zx -= 0.05
        hero.anim_step += 1

    elif hero.anim_step == 2:
        screen.blit(hero.img, (150, 300))
        screen.blit(zombie.img, (350, 300))
        hero.anim_step += 1

    elif hero.anim_step == 3:
        screen.blit(hero.img, (150, 300))
        screen.blit(zombie.img, (350, 300))

        screen.blit(txt_fight, (STATUS_X + 10, HEIGHT - 40 * 4))
        screen.blit(txt_item, (STATUS_X + 10, HEIGHT - 40 * 3))
        screen.blit(txt_ability, (STATUS_X + 10, HEIGHT - 40 * 2))
        screen.blit(txt_run, (STATUS_X + 10, HEIGHT - 40 * 1))


def attack(attacker, target):
    global action, game_mode, grid, hero_turn

    # target = grid[hero.y][hero.x]
    if hero_turn:
        if random.randint(1, 100) <= target.hit_chance:
            print("target hit")
            target.health -= attacker.weapon.base_damage

            # show hurt animation
            zombie.anim_step = 0
            while zombie.anim_step < len(zombie.hurt_cycle):
                # hurt anim
                pygame.draw.rect(screen, BG_COLOR, (350, 300, 128, 128))
                screen.blit(zombie.hurt_cycle[int(zombie.anim_step)], (380, 300))
                pygame.display.flip()
                zombie.anim_step += 0.005

                # hero weapon anim
                screen.blit(attacker.weapon.img, (250, 320))

        else:
            print("target missed")
            t = FONT.render("MISS", True, BLACK)
            acc = 0
            while acc <= 480:
                pygame.draw.rect(screen, WHITE, (350, 240, t.get_width() + 40, t.get_height() + 20), 0, 10)
                screen.blit(t, (370, 250))
                pygame.display.flip()
                acc += clock.tick(FPS)

        if target.health <= 0:
            print("target defeated")
            grid[attacker.y][attacker.x] = GridItemEmpty(hero.x, hero.y)
            grid[attacker.y][attacker.x].revealed = True
            game_mode = GameMode.MAP

        hero_turn = False

    else:
        if random.randint(1, 100) <= attacker.hit_chance:
            print("Hero hit")
            attacker.health -= target.damage
        else:
            print("Hero not hit")

        if hero.health <= 0:
            game_mode = GameMode.GAME_OVER

        hero_turn = True


def choose_item(hero_user):
    pad = 20
    w = STATUS_W - (pad * 2)
    h = HEIGHT - (pad * 2)
    surf = pygame.Surface((w, h))
    surf.fill(BLACK)
    surf.set_colorkey(BLACK)

    # Background
    pygame.draw.rect(surf, MED_BLUE, (0, 0, w, h), 0, 10)

    # Border
    pygame.draw.rect(surf, WHITE, (0, 0, w, h), 4, 10)

    for i in range(len(hero_user.inventory)):
        surf.blit(FONT.render(str(i + 1)[-1] + ")", True, WHITE), (10, 10 + 40 * i))

        if i < len(hero_user.inventory):
            t = FONT.render(hero_user.inventory[i].name, True, WHITE)
            surf.blit(t, (50, 10 + 40 * i))

    surf.blit(FONT.render("B)ack", True, WHITE), (10, 450))

    # Draw the event window onto the main screen
    screen.blit(surf, (STATUS_X + pad, pad))

    valid_keys = []
    inv_len = 9 if len(hero_user.inventory) == 10 else len(hero_user.inventory)
    for i in range(inv_len):
        valid_keys.append(i + 49)
    if len(hero_user.inventory) == 10:
        valid_keys.append(48)
    print(valid_keys)

    item = None
    done = False
    while not done:
        for ev in pygame.event.get():
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_b:
                    done = True
                elif ev.key in valid_keys:
                    item = hero_user.inventory[ev.key - 49]
                    done = True
        screen.blit(surf, (STATUS_X + pad, pad))
        pygame.display.flip()
    if item is not None:
        item.use(hero_user)
        hero_user.inventory.remove(item)


def choose_ability(hero_user):
    print("Ability")


def run():
    print("Run away!")


def draw_event():
    global action, game_mode, hero_turn, zombie

    if game_mode == GameMode.MAP:
        if type(grid[hero.y][hero.x]) is Zombie:
            game_mode = GameMode.BATTLE
            action = Action.NONE
            hero_turn = True
            zombie = Zombie(hero.x, hero.y)
            draw_event_window()

    elif game_mode == GameMode.BATTLE:
        draw_event_window()
        if action == Action.FIGHT:
            attack(hero, zombie)
            attack(hero, zombie)
        elif action == Action.ITEM:
            choose_item(hero)
        elif action == Action.RUN:
            pass

        action = Action.NONE


# Game Status variables
game_mode = GameMode.MAP
action = Action.NONE
hero = Hero(0, 0)
zombie = Zombie(0, 0)

if __name__ == '__main__':
    setup()

    while is_running:
        draw_screen()
        draw_status()
        draw_event()

        if game_mode == GameMode.GAME_OVER:
            draw_game_over()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.KEYDOWN:
                if game_mode == GameMode.MAP:
                    if event.key == pygame.K_UP:
                        if hero.y - 1 >= 0:
                            hero.y -= 1
                    elif event.key == pygame.K_DOWN:
                        if hero.y + 1 < GRID_H:
                            hero.y += 1
                    elif event.key == pygame.K_LEFT:
                        if hero.x - 1 >= 0:
                            hero.x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if hero.x + 1 < GRID_W:
                            hero.x += 1

                elif game_mode == GameMode.BATTLE:
                    print("(F)ight, (I)tem, (A)bility, (R)un")
                    if event.key == pygame.K_f:
                        action = Action.FIGHT
                    elif event.key == pygame.K_i:
                        action = Action.ITEM
                    elif event.key == pygame.K_a:
                        action = Action.ABILITY
                    elif event.key == pygame.K_r:
                        action = Action.RUN

                elif game_mode == GameMode.TREASURE:
                    if event.key == pygame.K_o:
                        # Open?
                        pass

                elif game_mode == GameMode.BUILDING:
                    if event.key == pygame.K_s:
                        # Search?
                        pass

                grid[hero.y][hero.x].revealed = True

        pygame.display.flip()
        dt = clock.tick(FPS)

    pygame.quit()
