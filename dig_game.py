"""
Each player gets a row to dig.
Each row has 4 parts that are increasingly difficult to dig.
Some parts require certain level of tools to dig.
While digging, players discover coal, ore, diamonds, etc to trade at base for money.
Money and ores are used to upgrade/purchase new tools to dig faster/deeper.
While not digging, holes slowly refill. This allows players to always have a source of income.

Tools:
pickaxe: wooden, stone, iron, diamond

Every so often, digging stops to add reinforced walls? Going deeper requires more walls?
"""

import random
from enum import Enum

import pygame.display

from colors import WHITE
from fonts import FONT_EMOJI_SM, FONT_EMOJI_MD

FPS = 60

AREA_SIZES = [35, 35, 40, 40]
AREA_COLORS = [(100, 100, 100), (100, 100, 0), (30, 100, 30), (0, 0, 100)]

STANDING = ["🧍‍♂️", "🧍🏻‍♂️", "🧍🏼‍♂️", "🧍🏽‍♂️", "🧍🏾‍♂️", "🧍🏿‍♂️", "🧍‍♀️", "🧍🏻‍♀️", "🧍🏼‍♀️", "🧍🏽‍♀️", "🧍🏾‍♀️", "🧍🏿‍♀️"]
WALKING = ["🚶‍♂️", "🚶🏻‍♂️", "🚶🏼‍♂️", "🚶🏽‍♂️", "🚶🏾‍♂️", "🚶🏿‍♂️", "🚶‍♀️", "🚶🏻‍♀️", "🚶🏼‍♀️", "🚶🏽‍♀️", "🚶🏾‍♀️", "🚶🏿‍♀️"]
RUNNING = ["🏃‍♂️", "🏃🏻‍♂️", "🏃🏼‍♂️", "🏃🏽‍♂️", "🏃🏾‍♂️", "🏃🏿‍♂️", "🏃‍♀️", "🏃🏻‍♀️", "🏃🏼‍♀️", "🏃🏽‍♀️", "🏃🏾‍♀️", "🏃🏿‍♀️"]

BIKING = ["🚴‍♂️", "🚴🏻‍♂️", "🚴🏼‍♂️", "🚴🏽‍♂️", "🚴🏾‍♂️", "🚴🏿‍♂️", "🚴‍♀️", "🚴🏻‍♀️", "🚴🏼‍♀️", "🚴🏽‍♀️", "🚴🏾‍♀️", "🚴🏿‍♀️"]
BIKE_COST = 40
BICYCLE = "Bicycle"
BICYCLE_SPEED = 1.0

HOUSES = ["🏚️", "🏠", "🏡"]
HOUSE_UPGRADE_1 = 75
HOUSE_UPGRADE_2 = 150

BACKPACK_UPGRADE = 100

HANDS = "🤛"
HAMMER = "🔨"
HAMMER_WRENCH = "🛠️"
AXE = "🪓"
PICKAXE = "⛏️"
HAMMER_PICK = "⚒️"

BOOT = "🥾"
BIKE = "🚲"
BACKPACK = "🎒"
CART = "🛒"

OLD_KEY = "🗝️"
SCROLL = "📜"
BOMB = "💣"
EXPLOSION = "💥"

HOME_X = 20
SPACE_W = SPACE_H = 22

TIME_PER_ITEM = 2000
INFINITE_DURABILITY = 999999

is_paused = False


class Action(Enum):
    STANDING = 0
    WALKING_LEFT = 1
    WALKING_RIGHT = 2
    DIGGING = 3


class Reward(Enum):
    EMPTY = ("", 0, "")  # A cave space that has already been dug out.
    NONE = ("None", 0, "")  # A cave space with no reward, but still needs to be dug out.
    CLAY = ("Clay", 1, "🟤")
    STONE = ("Stone", 2, "⚫")
    COPPER = ("Copper", 3, "🔶")
    IRON = ("Iron", 5, "🔷")
    SILVER = ("Silver", 10, "⬜")
    GOLD = ("Gold", 20, "🟨")
    DIAMOND = ("Diamond", 30, "💎")


class Tool:
    name = ""
    speed = 0
    durability = 0
    cost = 0
    emoji = ""

    def __init__(self, name, speed, durability, cost, emoji):
        self.name = name
        self.speed = speed  # ticks per strike, lower is faster/better
        self.durability = durability
        self.cost = cost
        self.emoji = emoji


class Hands(Tool):
    def __init__(self):
        super().__init__("Hands", 5000, INFINITE_DURABILITY, 0, HANDS)


class Pick1(Tool):
    def __init__(self):
        super().__init__("Hammer", 4000, 30, 5, HAMMER)


class Pick2(Tool):
    def __init__(self):
        super().__init__("Hammer & Wrench", 3000, 40, 10, HAMMER_WRENCH)


class Pick3(Tool):
    def __init__(self):
        super().__init__("Axe", 2500, 60, 25, AXE)


class Pick4(Tool):
    def __init__(self):
        super().__init__("Pickaxe", 2000, 80, 40, PICKAXE)


class Pick5(Tool):
    def __init__(self):
        super().__init__("Pickaxe & Hammer", 1500, 100, 50, HAMMER_PICK)


class Player:
    def __init__(self, name: str):
        self.name = name
        self.area = 0
        self.level = generate_area(self.area)
        self.x = HOME_X
        self.transport = ""
        self.speed = 0.5
        self.house_index = 0
        self.icon_index = random.randrange(0, 12)
        self.action = Action.STANDING
        self.target_x = 0
        self.target_index = 0
        self.tool: Tool = Pick1()
        self.tick = 0
        self.dig_strike = 0
        self.backpack_level = 0
        self.max_inventory = 3
        self.inventory = []
        self.money = 0

    def draw_level(self, scrn, num):
        y = (SPACE_H * num) + (num * 50) + 32

        for i, lvl in enumerate(self.level):
            if lvl != Reward.EMPTY:
                pygame.draw.rect(scrn, AREA_COLORS[self.area], (50 + (i * SPACE_W), y, SPACE_W + 1, SPACE_H))
            else:
                pygame.draw.rect(scrn, AREA_COLORS[self.area], (50 + (i * SPACE_W), y, SPACE_W + 1, SPACE_H), 1)

        if self.area < len(AREA_SIZES):
            person = FONT_EMOJI_SM.render(STANDING[self.icon_index], True, WHITE)
            if self.action == Action.DIGGING and self.tick < (self.tool.speed // 2):
                tool_img = FONT_EMOJI_SM.render(self.tool.emoji, True, WHITE)
                tool_img = pygame.transform.flip(tool_img, True, False)
                scrn.blit(tool_img, (self.x + SPACE_W - 4, y))
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)
            elif self.action == Action.DIGGING and self.tick >= (self.tool.speed // 2):
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)
            elif self.action == Action.WALKING_LEFT and self.transport == BICYCLE:
                person = FONT_EMOJI_SM.render(BIKING[self.icon_index], True, WHITE)
            elif self.action == Action.WALKING_RIGHT and self.transport == BICYCLE:
                person = FONT_EMOJI_SM.render(BIKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)
            elif self.action == Action.WALKING_LEFT and self.transport == "":
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
            elif self.action == Action.WALKING_RIGHT and self.transport == "":
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)

            scrn.blit(person, (self.x, y))

        house = FONT_EMOJI_MD.render(HOUSES[self.house_index], True, WHITE)
        scrn.blit(house, (HOME_X - 8, y - 2))

        # Status:
        inv_list = []
        for inv in self.inventory:
            name, val, emoji = inv.value
            inv_list.append(emoji)
        inven = "".join(inv_list)
        if inven == "":
            inven = "(empty)"

        dur = self.tool.durability
        if dur == INFINITE_DURABILITY:
            dur = "-"

        # Display progress legend
        scrn.blit(txt_progress, (10, scrn.get_height() - 48))

        # Display item legend
        scrn.blit(txt_items, (10, scrn.get_height() - 24))

        scrn.blit(FONT_EMOJI_SM.render(self.name, True, WHITE), (HOME_X - 5, y - SPACE_H - 3))
        scrn.blit(FONT_EMOJI_SM.render("⛰️: {}".format(self.area + 1), True, WHITE), (HOME_X + 170, y - SPACE_H - 3))
        scrn.blit(FONT_EMOJI_SM.render("💲{}".format(self.money), True, WHITE), (HOME_X + 220, y - SPACE_H - 5))
        scrn.blit(FONT_EMOJI_SM.render("{}: {} ({})".format(self.tool.emoji, self.tool.name, dur), True, WHITE), (HOME_X + 300, y - SPACE_H - 5))
        scrn.blit(FONT_EMOJI_SM.render("️{}".format(BOOT if self.transport != BICYCLE else BIKE), True, WHITE), (HOME_X + 540, y - SPACE_H - 5))
        scrn.blit(FONT_EMOJI_SM.render("️{}: {}".format(BACKPACK if self.backpack_level == 0 else CART, inven), True, WHITE), (HOME_X + 565, y - SPACE_H - 5))

    def dig(self):

        # Is the player done with all areas?
        if self.area >= len(AREA_SIZES):
            # Sell all remaining inventory if nothing left to do.
            if len(self.inventory) > 0:
                for inv in self.inventory:
                    name, val, emoji = inv.value
                    self.money += val * (self.house_index + 1)
                self.inventory.clear()
                self.tick = 0
            return

        # Is it time to advance areas?
        if self.x == HOME_X:
            non_empty_spaces = 0
            for lvl in self.level:
                if lvl != Reward.EMPTY:
                    non_empty_spaces += 1
            if non_empty_spaces == 0:
                self.area += 1
                self.level = generate_area(self.area)

        # If inventory is full, return home
        if len(self.inventory) == self.max_inventory and self.x > HOME_X:
            self.action = Action.WALKING_LEFT
            self.x = round(self.x - self.speed, 2)
            self.target_x = HOME_X

        # If we have items and we're home, start emptying the inventory
        elif len(self.inventory) > 0 and self.x == HOME_X and self.tick < TIME_PER_ITEM:
            # Waiting (emptying inventory)
            self.action = Action.STANDING
            self.tick += dt

        # After waiting long enough to empty inventory, gain money for each item
        elif len(self.inventory) > 0 and self.x == HOME_X and self.tick >= TIME_PER_ITEM:
            # Get money for inventory
            for inv in self.inventory:
                name, val, emoji = inv.value
                self.money += val * (self.house_index + 1)
            self.inventory.clear()
            self.tick = 0

        # If the player doesn't have a tool, buy the best the player can afford
        elif self.x == HOME_X and self.tool.name == "Hands" and self.money >= Pick1().cost:
            pick_tool = Pick1()
            if self.money >= Pick5().cost:
                pick_tool = Pick5()
            elif self.money >= Pick4().cost:
                pick_tool = Pick4()
            elif self.money >= Pick3().cost:
                pick_tool = Pick3()
            elif self.money >= Pick2().cost:
                pick_tool = Pick2()

            self.money -= pick_tool.cost
            self.tool = pick_tool

        # Check if player can afford a bicycle
        elif self.x == HOME_X and self.tool.name != "Hands" and self.transport == "" and self.money >= BIKE_COST:
            self.money -= BIKE_COST
            self.transport = BICYCLE
            self.speed = 1.0

        # Check if player can afford to upgrade the backpack
        elif self.x == HOME_X and self.backpack_level == 0 and self.money >= BACKPACK_UPGRADE:
            self.money -= BACKPACK_UPGRADE
            self.max_inventory = 6

        # Check if player can afford the first upgrade their house
        elif self.x == HOME_X and self.tool.name != "Hands" and self.house_index == 0 and self.money >= HOUSE_UPGRADE_1:
            self.money -= HOUSE_UPGRADE_1
            self.house_index = 1

        # Check if player can afford the second upgrade their house
        elif self.x == HOME_X and self.tool.name != "Hands" and self.house_index == 1 and self.money >= HOUSE_UPGRADE_2:
            self.money -= HOUSE_UPGRADE_2
            self.house_index = 2

        # If the player has no tool, they need to continue walking home to buy a tool
        elif self.target_x == HOME_X and self.action == Action.WALKING_LEFT and self.tool.name == "Hands":
            self.x = round(self.x - self.speed, 2)

        else:
            # Find first diggable space (non-EMPTY)
            space_index = 0
            for space in self.level:
                if space == Reward.EMPTY:
                    space_index += 1
                else:
                    self.target_index = space_index
                    self.target_x = 50 + ((space_index - 1) * SPACE_W) + 4
                    break

            # Player is left of the target, so walk right
            if self.x < self.target_x:
                self.action = Action.WALKING_RIGHT
                self.x = round(self.x + self.speed, 2)

            # Player is right of the target, so walk left
            elif self.x > self.target_x:
                self.action = Action.WALKING_LEFT
                self.x = round(self.x - self.speed, 2)

            # Player is at the target x pos, start digging
            if abs(self.x - self.target_x) < 0.1:
                self.action = Action.DIGGING
                self.tick += dt

                # Enough time has passed for a "dig"
                if self.tick >= self.tool.speed:
                    self.tick = 0
                    self.dig_strike += 1

                    # Reduce tool durability, if possible
                    if self.tool.durability != INFINITE_DURABILITY:
                        self.tool.durability -= 1

                    # Break tool if durability reaches zero
                    if self.tool.durability <= 0:
                        self.tool = Hands()

                    # Calculate value of inventory
                    potential_money = 0
                    for inv in self.inventory:
                        name, val, emoji = inv.value
                        potential_money += val

                    # If player has no tool, but has money for a tool, return home to buy one
                    if self.tool.name == "Hands" and (self.money + potential_money) >= Pick1().cost:
                        self.action = Action.WALKING_LEFT
                        self.x = round(self.x - self.speed, 2)
                        self.target_x = HOME_X

                # After 5 strikes of the tool, gather any reward drops
                if self.dig_strike == 5:
                    self.tick = 0
                    self.dig_strike = 0

                    # If a reward dropped, add it to inventory
                    if self.level[self.target_index] != Reward.NONE:
                        self.inventory.append(self.level[self.target_index])

                    # Mark the level space as EMPTY
                    self.level[self.target_index] = Reward.EMPTY

                    # If all spaces of the level are empty, return home to move to next area
                    if self.target_index == AREA_SIZES[self.area] - 1:
                        self.action = Action.WALKING_LEFT
                        self.x = round(self.x - self.speed, 2)
                        self.target_x = HOME_X


def generate_area(num):
    if num == 0:
        return generate_area1()
    elif num == 1:
        return generate_area2()
    elif num == 2:
        return generate_area3()
    elif num == 3:
        return generate_area4()
    else:
        return []


def generate_area1():
    area = []
    for depth in range(AREA_SIZES[0]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 60 <= rn <= 69:
            area.append(Reward.CLAY)
        elif 70 <= rn <= 90:
            area.append(Reward.STONE)
        elif 91 <= rn <= 98:
            area.append(Reward.COPPER)
        elif 99 <= rn <= 100:
            area.append(Reward.IRON)
        else:
            area.append(Reward.NONE)
    return area


def generate_area2():
    area = []
    for depth in range(AREA_SIZES[1]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 40 <= rn <= 49:
            area.append(Reward.CLAY)
        elif 50 <= rn <= 70:
            area.append(Reward.STONE)
        elif 71 <= rn <= 89:
            area.append(Reward.COPPER)
        elif 90 <= rn <= 95:
            area.append(Reward.IRON)
        elif 96 <= rn <= 100:
            area.append(Reward.SILVER)
        else:
            area.append(Reward.NONE)
    return area


def generate_area3():
    area = []
    for depth in range(AREA_SIZES[2]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 40 <= rn <= 49:
            area.append(Reward.STONE)
        elif 50 <= rn <= 70:
            area.append(Reward.COPPER)
        elif 71 <= rn <= 89:
            area.append(Reward.IRON)
        elif 90 <= rn <= 95:
            area.append(Reward.SILVER)
        elif 96 <= rn <= 100:
            area.append(Reward.GOLD)
        else:
            area.append(Reward.NONE)
    return area


def generate_area4():
    area = []
    for depth in range(AREA_SIZES[3]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 40 <= rn <= 49:
            area.append(Reward.COPPER)
        elif 50 <= rn <= 70:
            area.append(Reward.IRON)
        elif 71 <= rn <= 89:
            area.append(Reward.SILVER)
        elif 90 <= rn <= 95:
            area.append(Reward.GOLD)
        elif 96 <= rn <= 100:
            area.append(Reward.DIAMOND)
        else:
            area.append(Reward.NONE)
    return area


def legend_progress():
    progress = ("{}(${})➡️{}(${})➡️{}(${})➡️{}(${})➡️{}(${}) | "
                .format(HAMMER, Pick1().cost, HAMMER_WRENCH, Pick2().cost, AXE, Pick3().cost,
                        PICKAXE, Pick4().cost, HAMMER_PICK, Pick5().cost))
    progress += "{}+${}➡️{}+${}➡️{} | ".format(HOUSES[0], HOUSE_UPGRADE_1, HOUSES[1], HOUSE_UPGRADE_2, HOUSES[2])
    progress += "{}+${}➡️{} | ".format(BOOT, BIKE_COST, BIKE)
    progress += "{}+${}➡️{}".format(BACKPACK, BACKPACK_UPGRADE, CART)
    return FONT_EMOJI_SM.render(progress, True, WHITE)


def legend_items():
    legend = []
    for e in Reward:
        name, value, emoji = e.value
        if emoji != "":
            legend.append("{}{}=${}".format(emoji, name, value))
    return FONT_EMOJI_SM.render(" | ".join(legend), True, WHITE)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((1920//2, 1080//2))
    clock = pygame.time.Clock()
    is_running = True
    dt = 0

    txt_progress = legend_progress()
    txt_items = legend_items()

    players = [Player("LeftFourDave"), Player("BigEdith"), Player("Rornicus"), Player("meshuggen8r"),
               Player("Bette_Meddler"), Player("ohjanji"), Player("ShirouHokuto")]

    for pl in players:
        pl.tool = Pick5()

    while is_running:
        screen.fill((0, 0, 0))

        for ii, pl in enumerate(players):
            pl.draw_level(screen, ii)
            if not is_paused:
                pl.dig()

        dt = clock.tick(FPS)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_paused = not is_paused
                    print("is_paused", is_paused)
                elif event.key in [pygame.K_PLUS, pygame.K_KP_PLUS]:
                    for pl in players:
                        pl.speed += 0.5
                    print("speed:", players[0].speed)
                elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                    for pl in players:
                        pl.speed -= 0.5
                    print("speed:", players[0].speed)

    pygame.quit()

"""
TODO:

+ Sell inventory when nothing left to do.
+ When tool == Hands, draw a hand instead of a pickaxe.
+ Any time you go home, sell inventory
+ If using Hands, as soon as money is available, get a tool.
+ Backpack upgrade

"""