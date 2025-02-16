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

from colors import WHITE, DK_GRAY
from fonts import FONT_EMOJI_SM, FONT_EMOJI_MD, FONT_EMOJI_LG

FPS = 60

AREA_SIZES = [35, 35, 40, 40, 40]
AREA_COLORS = [(80, 80, 80), (130, 130, 0), (30, 100, 30), (0, 0, 100), (100, 0, 0)]

STANDING = ["🧍‍♂️", "🧍🏻‍♂️", "🧍🏼‍♂️", "🧍🏽‍♂️", "🧍🏾‍♂️", "🧍🏿‍♂️", "🧍‍♀️", "🧍🏻‍♀️", "🧍🏼‍♀️", "🧍🏽‍♀️", "🧍🏾‍♀️", "🧍🏿‍♀️"]
WALKING = ["🚶‍♂️", "🚶🏻‍♂️", "🚶🏼‍♂️", "🚶🏽‍♂️", "🚶🏾‍♂️", "🚶🏿‍♂️", "🚶‍♀️", "🚶🏻‍♀️", "🚶🏼‍♀️", "🚶🏽‍♀️", "🚶🏾‍♀️", "🚶🏿‍♀️"]
RUNNING = ["🏃‍♂️", "🏃🏻‍♂️", "🏃🏼‍♂️", "🏃🏽‍♂️", "🏃🏾‍♂️", "🏃🏿‍♂️", "🏃‍♀️", "🏃🏻‍♀️", "🏃🏼‍♀️", "🏃🏽‍♀️", "🏃🏾‍♀️", "🏃🏿‍♀️"]
BIKING = ["🚴‍♂️", "🚴🏻‍♂️", "🚴🏼‍♂️", "🚴🏽‍♂️", "🚴🏾‍♂️", "🚴🏿‍♂️", "🚴‍♀️", "🚴🏻‍♀️", "🚴🏼‍♀️", "🚴🏽‍♀️", "🚴🏾‍♀️", "🚴🏿‍♀️"]

HOUSES = ["🏚️", "🏠", "🏡", "🏛️"]
HOUSE_UPGRADE_1 = 75
HOUSE_UPGRADE_2 = 150
HOUSE_UPGRADE_3 = 400

BACKPACK_UPGRADE = 100
KEY_COST = 25

HANDS = "🤛"
HAMMER = "🔨"
HAMMER_WRENCH = "🛠️"
AXE = "🪓"
PICKAXE = "⛏️"
HAMMER_PICK = "⚒️"

BACKPACK = "🎒"
CART = "🛒"

CHEST_SYM = "🧰"
OLD_KEY = "🗝️"
SCROLL = "📜"
GAMBLE1 = "🎲"
GAMBLE2 = "🎰"
GAMBLE3 = "🎱"
MONEY_BAG = "💰"
HOLE = "🕳️"

BOMB = "💣"
EXPLOSION = "💥"

BOOT_SYM = "🥾"
BIKE_SYM = "🚲"
SCOOTER_SYM = "🛴"
MOTOR_SCOOTER_SYM = "🛵"

HOME_X = 20
SPACE_W = SPACE_H = 22

TIME_PER_ITEM = 500
TIME_TO_EMPTY_INV = 2000
INFINITE_DURABILITY = 999999

BOULDER_SYM = "⚪"
TXT_BOULDER = FONT_EMOJI_SM.render(BOULDER_SYM, True, WHITE)
TXT_CHEST = FONT_EMOJI_SM.render(CHEST_SYM, True, WHITE)
TXT_PAUSED = FONT_EMOJI_LG.render("PAUSED", True, WHITE)
TXT_PAUSED_X = 0
TXT_PAUSED_Y = 0

TRAN_NAME = 0
TRAN_COST = 1
TRAN_EMOJI = 2
TRAN_SPEED = 3

DROP_NAME = 0
DROP_COST = 1
DROP_EMOJI = 2

is_paused = False


class Action(Enum):
    STANDING = 0
    WALKING_LEFT = 1
    WALKING_RIGHT = 2
    DIGGING = 3


class Transport(Enum):
    """TRANSPORT = (Name, Cost, Rep, Speed)"""
    BOOTS = ("Boots", 0, BOOT_SYM, 1.0)
    SCOOTER = ("Scooter", 30, SCOOTER_SYM, 1.5)
    BIKE = ("Bike", 60, BIKE_SYM, 2.0)
    MOTOR_SCOOTER = ("Motor Scooter", 100, MOTOR_SCOOTER_SYM, 3.0)


class Drop(Enum):
    """DROP = (Name, Value, Inventory_Representation)"""
    EMPTY = ("", 0, "")  # A cave space that has already been dug out.
    NONE = ("None", 0, "")  # A cave space with no reward, but still needs to be dug out.
    CLAY = ("Clay", 1, "🟤")
    STONE = ("Stone", 2, "⚫")
    COPPER = ("Copper", 3, "🔶")
    IRON = ("Iron", 5, "🔷")
    SILVER = ("Silver", 10, "⬜")
    GOLD = ("Gold", 20, "🟨")
    DIAMOND = ("Diamond", 30, "💎")
    CHEST = ("Chest", 0, CHEST_SYM)
    BOULDER = ("Boulder", 0, BOULDER_SYM)
    EXPOSED_BOULDER = ("Exposed Boulder", 0, BOULDER_SYM)


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
        self.status = ""
        self.area = 0
        self.level = generate_area(self.area)
        self.level_strikes = [0] * AREA_SIZES[self.area]
        self.x = HOME_X
        self.transport = Transport.BOOTS
        self.speed = self.transport.value[TRAN_SPEED]
        self.house_index = 0
        self.icon_index = random.randrange(0, 12)
        self.action = Action.STANDING
        self.target_x = 0
        self.target_index = 0
        self.tool: Tool = Pick1()
        self.tick = 0
        self.backpack_level = 0
        self.max_inventory = 3
        self.inventory = []
        self.chest_count = 0
        self.money = 0

    def draw_level(self, scrn, num):
        y = (SPACE_H * num) + (num * 50) + 32

        # Draw the area cells
        if self.area < len(AREA_SIZES):
            for i, lvl in enumerate(self.level):
                x = 50 + (i * SPACE_W)

                if lvl in [Drop.EMPTY, Drop.EXPOSED_BOULDER]:
                    pygame.draw.rect(scrn, AREA_COLORS[self.area], (x, y, SPACE_W + 1, SPACE_H), 1)
                    scrn.blit(WALLS[self.area], (x, y))
                    if lvl == Drop.EXPOSED_BOULDER:
                        scrn.blit(TXT_BOULDER, (x, y))
                else:
                    pygame.draw.rect(scrn, AREA_COLORS[self.area], (x, y, SPACE_W + 1, SPACE_H))

            if self.action == Action.DIGGING and self.tick < (self.tool.speed // 2):
                tool_img = FONT_EMOJI_SM.render(self.tool.emoji, True, WHITE)
                tool_img = pygame.transform.flip(tool_img, True, False)
                scrn.blit(tool_img, (self.x + SPACE_W - 4, y))
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)
                scrn.blit(person, (self.x, y))

            elif self.action == Action.DIGGING and self.tick >= (self.tool.speed // 2):
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)
                scrn.blit(person, (self.x, y))

            elif self.action == Action.WALKING_LEFT and self.transport in [Transport.SCOOTER, Transport.MOTOR_SCOOTER]:
                # person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                transp = FONT_EMOJI_SM.render(self.transport.value[TRAN_EMOJI], True, WHITE)
                # scrn.blit(person, (self.x, y))
                scrn.blit(transp, (self.x, y))
            elif self.action == Action.WALKING_RIGHT and self.transport in [Transport.SCOOTER, Transport.MOTOR_SCOOTER]:
                # person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                # person = pygame.transform.flip(person, True, False)
                transp = FONT_EMOJI_SM.render(self.transport.value[TRAN_EMOJI], True, WHITE)
                transp = pygame.transform.flip(transp, True, False)
                # scrn.blit(person, (self.x, y))
                scrn.blit(transp, (self.x, y))

            elif self.action == Action.WALKING_LEFT and self.transport == Transport.BIKE:
                person = FONT_EMOJI_SM.render(BIKING[self.icon_index], True, WHITE)
                scrn.blit(person, (self.x, y))
            elif self.action == Action.WALKING_RIGHT and self.transport == Transport.BIKE:
                person = FONT_EMOJI_SM.render(BIKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)
                scrn.blit(person, (self.x, y))

            elif self.action == Action.WALKING_LEFT and self.transport == Transport.BOOTS:
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                scrn.blit(person, (self.x, y))
            elif self.action == Action.WALKING_RIGHT and self.transport == Transport.BOOTS:
                person = FONT_EMOJI_SM.render(WALKING[self.icon_index], True, WHITE)
                person = pygame.transform.flip(person, True, False)
                scrn.blit(person, (self.x, y))

            else:
                person = FONT_EMOJI_SM.render(STANDING[self.icon_index], True, WHITE)
                scrn.blit(person, (self.x, y))

        # Draw the player's house
        house = FONT_EMOJI_MD.render(HOUSES[self.house_index], True, WHITE)
        scrn.blit(house, (HOME_X - 8, y - 2))

        # Display legends
        # scrn.blit(txt_progress, (10, scrn.get_height() - 48))
        # scrn.blit(txt_items, (10, scrn.get_height() - 24))

        # Status:
        inv_list = []
        for inv in self.inventory:
            inv_list.append(inv.value[DROP_EMOJI])
        inven = "".join(inv_list)

        dur = "-" if self.tool.durability == INFINITE_DURABILITY else self.tool.durability

        scrn.blit(FONT_EMOJI_SM.render(self.name, True, WHITE), (HOME_X - 5, y - SPACE_H - 3))
        if self.area < len(AREA_SIZES):
            FONT_EMOJI_SM.set_bold(True)
            scrn.blit(FONT_EMOJI_SM.render("⛰️: {}".format(self.area + 1), True, AREA_COLORS[self.area]), (HOME_X + 170, y - SPACE_H))
            FONT_EMOJI_SM.set_bold(False)
        scrn.blit(FONT_EMOJI_SM.render("💲{}".format(self.money), True, "#00cc00"), (HOME_X + 220, y - SPACE_H - 3))
        scrn.blit(FONT_EMOJI_SM.render("{} ({})".format(self.tool.emoji, dur), True, WHITE), (HOME_X + 300, y - SPACE_H - 3))
        if self.chest_count > 0:
            scrn.blit(FONT_EMOJI_SM.render("{}×{}".format(CHEST_SYM, self.chest_count), True, WHITE), (HOME_X + 460, y - SPACE_H - 3))
        scrn.blit(FONT_EMOJI_SM.render("️{}".format(self.transport.value[TRAN_EMOJI]), True, WHITE), (HOME_X + 540, y - SPACE_H - 3))
        scrn.blit(FONT_EMOJI_SM.render("️{}: {}".format(BACKPACK if self.backpack_level == 0 else CART, inven), True, WHITE), (HOME_X + 565, y - SPACE_H - 3))

    def dig(self):
        status = []

        # Is the player done with all areas?
        if self.area >= len(AREA_SIZES):
            status.append("Player is finished with all areas.")
            # Sell all remaining inventory if nothing left to do.
            if len(self.inventory) > 0:
                for inv in self.inventory:
                    name, val, emoji = inv.value
                    self.money += val * (self.house_index + 1)
                self.inventory.clear()
                self.tick = 0
            return

        # Is it time to advance areas?
        if self.x <= HOME_X:
            self.x = HOME_X
            non_empty_spaces = 0
            for lvl in self.level:
                if lvl != Drop.EMPTY:
                    non_empty_spaces += 1
            if non_empty_spaces == 0:
                status.append("Moving to next area.")
                self.area += 1
                if self.area < len(AREA_SIZES):
                    self.level = generate_area(self.area)
                    self.level_strikes = [0] * AREA_SIZES[self.area]

        # If inventory is full, return home
        if len(self.inventory) == self.max_inventory and self.x > HOME_X:
            status.append("Inventory full so returning home.")
            self.action = Action.WALKING_LEFT
            self.x = round(self.x - self.speed, 2)
            self.target_x = HOME_X

        # If we have items, and we're home, start emptying the inventory
        elif len(self.inventory) > 0 and self.x == HOME_X and self.tick < TIME_TO_EMPTY_INV:
            # Waiting (emptying inventory)
            status.append("Emptying inventory.")
            self.action = Action.STANDING
            self.tick += dt

        # After waiting long enough to empty inventory, gain money for each item
        elif len(self.inventory) > 0 and self.x == HOME_X and self.tick >= TIME_TO_EMPTY_INV:
            # Get money for inventory
            inv_amt = 0
            for inv in self.inventory:
                name, val, emoji = inv.value
                if name == "Chest":
                    self.chest_count += 1
                else:
                    inv_amt += val * (self.house_index + 1)

            status.append("Gained ${} from selling inventory.".format(str(inv_amt)))
            self.money += inv_amt

            self.inventory.clear()
            self.tick = 0

            # If we have any chests, buy keys
            while self.chest_count > 0 and self.money >= KEY_COST:
                status.append("Buying a key to open chest...")
                self.money -= KEY_COST
                self.chest_count -= 1

                # Choose an effect: decrease speed, break current tool, break bicycle
                eff = ""
                rn = random.randint(1, 100)
                if 1 <= rn <= 10:
                    eff = "Backpack upgrade"
                    if self.backpack_level == 0:
                        self.backpack_level += 1
                        self.max_inventory = 6
                elif 11 <= rn <= 20:
                    eff = "Backpack downgrade"
                    if self.backpack_level == 1:
                        self.backpack_level -= 1
                        self.max_inventory = 3
                elif 21 <= rn <= 30:
                    eff = "Gain best tool!"
                    self.tool = Pick5()
                elif 31 <= rn <= 40:
                    eff = "Broken tool"
                    self.tool = Hands()
                elif 41 <= rn <= 50:
                    eff = "Gain best transport!"
                    self.transport = Transport.MOTOR_SCOOTER
                    self.speed = Transport.MOTOR_SCOOTER.value[TRAN_SPEED]
                elif 51 <= rn <= 60:
                    eff = "Broken transport"
                    self.transport = Transport.BOOTS
                    self.speed = Transport.BOOTS.value[TRAN_SPEED]
                elif 61 <= rn <= 70:
                    eff = "Gain $100"
                    self.money += 100
                elif 71 <= rn <= 80:
                    eff = "Lose $100"
                    self.money -= 100
                    self.money = 0 if self.money < 0 else self.money
                elif 81 <= rn <= 90:
                    eff = "Gain $50"
                    self.money += 50
                elif 91 <= rn <= 100:
                    eff = "Lose $50"
                    self.money -= 50
                    self.money = 0 if self.money < 0 else self.money
                status.append(" chest effect: {}".format(eff))

        # If the player doesn't have a tool or tool is nearly broken, buy the best the player can afford
        elif self.x == HOME_X and (self.tool.name == "Hands" or self.tool.durability < 10) and self.money >= Pick1().cost:
            status.append("Buying a new tool...")
            pick_tool = Pick1()
            if self.money >= Pick5().cost:
                pick_tool = Pick5()
            elif self.money >= Pick4().cost:
                pick_tool = Pick4()
            elif self.money >= Pick3().cost:
                pick_tool = Pick3()
            elif self.money >= Pick2().cost:
                pick_tool = Pick2()
            status.append(" bought a {}".format(pick_tool.name))

            self.money -= pick_tool.cost
            self.tool = pick_tool

        # Check if player can afford a transport upgrade
        elif (self.x == HOME_X and self.tool.name != "Hands" and self.money >= Transport.MOTOR_SCOOTER.value[TRAN_COST] and
              self.transport in [Transport.BOOTS, Transport.SCOOTER, Transport.BIKE]):
            status.append("Buying a Motor Scooter...")
            self.transport = Transport.MOTOR_SCOOTER
            self.money -= Transport.MOTOR_SCOOTER.value[TRAN_COST]
            self.speed = Transport.MOTOR_SCOOTER.value[TRAN_SPEED]

        elif (self.x == HOME_X and self.tool.name != "Hands" and self.money >= Transport.BIKE.value[TRAN_COST] and
              self.transport in [Transport.BOOTS, Transport.SCOOTER]):
            status.append("Buying a Bike...")
            self.transport = Transport.BIKE
            self.money -= Transport.BIKE.value[TRAN_COST]
            self.speed = Transport.BIKE.value[TRAN_SPEED]

        elif (self.x == HOME_X and self.tool.name != "Hands" and self.money >= Transport.SCOOTER.value[TRAN_COST] and
              self.transport == Transport.BOOTS):
            status.append("Buying a Scooter...")
            self.transport = Transport.SCOOTER
            self.money -= Transport.SCOOTER.value[TRAN_COST]
            self.speed = Transport.SCOOTER.value[TRAN_SPEED]

        # Check if player can afford to upgrade the backpack
        elif self.x == HOME_X and self.backpack_level == 0 and self.money >= BACKPACK_UPGRADE:
            status.append("Upgrading backpack.")
            self.money -= BACKPACK_UPGRADE
            self.backpack_level += 1
            self.max_inventory = 6

        # Check if player can afford the first upgrade their house
        elif self.x == HOME_X and self.tool.name != "Hands" and self.house_index == 0 and self.money >= HOUSE_UPGRADE_1:
            status.append("Upgrading house (first upgrade).")
            self.money -= HOUSE_UPGRADE_1
            self.house_index = 1

        # Check if player can afford the second upgrade their house
        elif self.x == HOME_X and self.tool.name != "Hands" and self.house_index == 1 and self.money >= HOUSE_UPGRADE_2:
            status.append("Upgrading house (second upgrade).")
            self.money -= HOUSE_UPGRADE_2
            self.house_index = 2

        # Check if player can afford the third upgrade their house
        elif self.x == HOME_X and self.tool.name != "Hands" and self.house_index == 1 and self.money >= HOUSE_UPGRADE_3:
            status.append("Upgrading house (third upgrade).")
            self.money -= HOUSE_UPGRADE_3
            self.house_index = 3

        # If the player has no tool, they need to continue walking home to buy a tool
        elif self.target_x == HOME_X and self.action == Action.WALKING_LEFT and self.tool.name == "Hands":
            status.append("Continuing walk home.")
            self.x = round(self.x - self.speed, 2)

        else:
            # Find first diggable space (non-EMPTY)
            space_index = 0
            for space in self.level:
                if space == Drop.EMPTY:
                    space_index += 1
                else:
                    self.target_index = space_index
                    self.target_x = 50 + ((space_index - 1) * SPACE_W) + 4
                    break
            # status.append("Targeting cell {}.".format(str(self.target_index)))

            # Player is left of the target, so walk right
            if self.x < self.target_x:
                # status.append("Walking right.")
                self.action = Action.WALKING_RIGHT
                self.x = round(self.x + self.speed, 2)

            # Player is right of the target, so walk left
            elif self.x > self.target_x:
                # status.append("Walking left.")
                self.action = Action.WALKING_LEFT
                self.x = round(self.x - self.speed, 2)

            # Player is at the target x pos, start digging
            if abs(self.x - self.target_x) <= self.transport.value[TRAN_SPEED]:
                status.append("Digging.")
                self.x = self.target_x
                self.action = Action.DIGGING
                self.tick += dt

                # Enough time has passed for a "dig"
                if self.tick >= self.tool.speed:
                    self.tick = 0
                    self.level_strikes[self.target_index] += 1

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
                        status.append("Returning home to buy a tool.")
                        self.action = Action.WALKING_LEFT
                        self.x = round(self.x - self.speed, 2)
                        self.target_x = HOME_X

                # After (area + 2) strikes of the tool, gather any reward drops
                if self.level_strikes[self.target_index] == (self.area + 2):
                    self.tick = 0

                    # If a reward is dropped, add it to inventory
                    if self.level[self.target_index] not in [Drop.NONE, Drop.BOULDER, Drop.EXPOSED_BOULDER]:
                        # Add drop to inventory
                        drop = self.level[self.target_index]
                        status.append("Picked up {}.".format(drop.name))
                        self.inventory.append(drop)
                        # Mark the level space as EMPTY
                        self.level[self.target_index] = Drop.EMPTY

                    elif self.level[self.target_index] == Drop.BOULDER:
                        status.append("Discovered a boulder.")
                        self.level[self.target_index] = Drop.EXPOSED_BOULDER
                        self.level_strikes[self.target_index] = 0

                    elif self.level[self.target_index] == Drop.EXPOSED_BOULDER:
                        # 25% chance of dropping a diamond, otherwise drop gold
                        drop = Drop.DIAMOND if random.randint(1, 4) == 1 else Drop.GOLD
                        status.append("Picked up {} from boulder.".format(drop.name))
                        self.inventory.append(drop)
                        self.level[self.target_index] = Drop.EMPTY

                    else:
                        self.level[self.target_index] = Drop.EMPTY

                    # If all spaces of the level are empty, return home to move to next area
                    if self.target_index == AREA_SIZES[self.area] - 1:
                        status.append("Returning home to start a new area.")
                        self.action = Action.WALKING_LEFT
                        self.x = round(self.x - self.speed, 2)
                        self.target_x = HOME_X

        if len(status) > 0:
            current_status = self.name + ": " + (" ".join(status))
            if self.status != current_status:
                self.status = current_status
                print(current_status)


def generate_area(num):
    if num == 0:
        return generate_area1()
    elif num == 1:
        return generate_area2()
    elif num == 2:
        return generate_area3()
    elif num == 3:
        return generate_area4()
    elif num == 4:
        return generate_area5()
    else:
        return []


def generate_area1():
    area = []
    for depth in range(AREA_SIZES[0]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 60 <= rn <= 69:
            area.append(Drop.CLAY)
        elif 70 <= rn <= 90:
            area.append(Drop.STONE)
        elif 91 <= rn <= 98:
            area.append(Drop.COPPER)
        elif 99 <= rn <= 100:
            area.append(Drop.IRON)
        else:
            area.append(Drop.NONE)

    # Add 20% chance of a boulder around the mid-point of the area:
    if random.randint(1, 5) == 1:
        for i in range(AREA_SIZES[0] // 2, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.BOULDER
                break

    # Add 20% chance for a chest near the end of the area:
    if random.randint(1, 5) == 1:
        for i in range(AREA_SIZES[0] // 2 + 10, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.CHEST
                break

    # for i in range(30):
    #     area[i] = Drop.EMPTY

    return area


def generate_area2():
    area = []
    for depth in range(AREA_SIZES[1]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 40 <= rn <= 49:
            area.append(Drop.CLAY)
        elif 50 <= rn <= 70:
            area.append(Drop.STONE)
        elif 71 <= rn <= 89:
            area.append(Drop.COPPER)
        elif 90 <= rn <= 95:
            area.append(Drop.IRON)
        elif 96 <= rn <= 100:
            area.append(Drop.SILVER)
        else:
            area.append(Drop.NONE)

    # Add 25% chance of a boulder around the mid-point of the area:
    if random.randint(1, 4) == 1:
        for i in range(AREA_SIZES[0] // 2, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.BOULDER
                break
    # Add 25% chance of a chest near the end of the area:
    if random.randint(1, 4) == 1:
        for i in range(AREA_SIZES[0] // 2 + 10, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.CHEST
                break

    return area


def generate_area3():
    area = []
    for depth in range(AREA_SIZES[2]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 40 <= rn <= 49:
            area.append(Drop.STONE)
        elif 50 <= rn <= 70:
            area.append(Drop.COPPER)
        elif 71 <= rn <= 89:
            area.append(Drop.IRON)
        elif 90 <= rn <= 95:
            area.append(Drop.SILVER)
        elif 96 <= rn <= 100:
            area.append(Drop.GOLD)
        else:
            area.append(Drop.NONE)

    # Add 33% chance of a boulder around the mid-point of the area:
    if random.randint(1, 3) == 1:
        for i in range(AREA_SIZES[0] // 2, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.BOULDER
                break

    # Add 33% chance of a chest near the end of the area:
    if random.randint(1, 3) == 1:
        for i in range(AREA_SIZES[0] // 2 + 10, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.CHEST
                break

    return area


def generate_area4():
    area = []
    for depth in range(AREA_SIZES[3]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 40 <= rn <= 49:
            area.append(Drop.COPPER)
        elif 50 <= rn <= 70:
            area.append(Drop.IRON)
        elif 71 <= rn <= 89:
            area.append(Drop.SILVER)
        elif 90 <= rn <= 95:
            area.append(Drop.GOLD)
        elif 96 <= rn <= 100:
            area.append(Drop.DIAMOND)
        else:
            area.append(Drop.NONE)

    # Add 50% chance of a boulder around the mid-point of the area:
    if random.randint(1, 2) == 1:
        for i in range(AREA_SIZES[0] // 2, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.BOULDER
                break

    # Add 50% chance of a chest near the end of the area:
    if random.randint(1, 2) == 1:
        for i in range(AREA_SIZES[0] // 2 + 10, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.CHEST
                break

    return area


def generate_area5():
    area = []
    for depth in range(AREA_SIZES[4]):
        rn = random.randint(1, 100) + depth  # add the depth so items are more likely as you go deeper
        if 40 <= rn <= 60:
            area.append(Drop.IRON)
        elif 61 <= rn <= 75:
            area.append(Drop.SILVER)
        elif 76 <= rn <= 90:
            area.append(Drop.GOLD)
        elif 91 <= rn <= 100:
            area.append(Drop.DIAMOND)
        else:
            area.append(Drop.NONE)

    # Add a boulder around the mid-point of the area:
    for i in range(AREA_SIZES[0] // 2, AREA_SIZES[0]):
        if area[i] == Drop.NONE:
            area[i] = Drop.BOULDER
            break

    # Add 50% chance of a chest near the end of the area:
    if random.randint(1, 2) == 1:
        for i in range(AREA_SIZES[0] // 2 + 10, AREA_SIZES[0]):
            if area[i] == Drop.NONE:
                area[i] = Drop.CHEST
                break

    return area


def legend_progress():
    progress = ("{}(${})➡️{}(${})➡️{}(${})➡️{}(${})➡️{}(${}) | "
                .format(HAMMER, Pick1().cost, HAMMER_WRENCH, Pick2().cost, AXE, Pick3().cost,
                        PICKAXE, Pick4().cost, HAMMER_PICK, Pick5().cost))
    progress += "{}+${}➡️{}+${}➡️{} | ".format(HOUSES[0], HOUSE_UPGRADE_1, HOUSES[1], HOUSE_UPGRADE_2, HOUSES[2])
    # progress += "{}+${}➡️{} | ".format(BOOT, BIKE_COST, BIKE)
    progress += "{}+${}➡️{}".format(BACKPACK, BACKPACK_UPGRADE, CART)
    return FONT_EMOJI_SM.render(progress, True, WHITE)


def legend_items():
    legend = []
    for e in Drop:
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

    texture_scale = 0.16
    WALLS = [
        pygame.transform.smoothscale_by(pygame.image.load('images/game/walls/gray_wall.png'), texture_scale).convert(),
        pygame.transform.smoothscale_by(pygame.image.load('images/game/walls/yellow_wall.png'), texture_scale).convert(),
        pygame.transform.smoothscale_by(pygame.image.load('images/game/walls/green_wall.png'), texture_scale).convert(),
        pygame.transform.smoothscale_by(pygame.image.load('images/game/walls/blue_wall.png'), texture_scale).convert(),
        pygame.transform.smoothscale_by(pygame.image.load('images/game/walls/red_wall.png'), texture_scale).convert()
    ]

    TXT_PAUSED_X = (screen.get_width() - TXT_PAUSED.get_width()) // 2
    TXT_PAUSED_Y = (screen.get_height() - TXT_PAUSED.get_height()) // 2

    txt_progress = legend_progress()
    txt_items = legend_items()

    players = [Player("LeftFourDave"), Player("BigEdith"), Player("Rornicus"), Player("meshuggen8r"),
               Player("Bette_Meddler"), Player("ohjanji"), Player("ShirouHokuto")]

    for pl in players:
        pl.tool = Pick5()
        pl.tool.speed = 100
        pl.tool.durability = 5000
    #     pl.transport = Transport.BIKE
    #     pl.speed = Transport.BIKE.value[TRAN_SPEED]
    # players[1].transport = Transport.SCOOTER
    # players[1].speed = Transport.SCOOTER.value[TRAN_SPEED]
    #
    # players[2].transport = Transport.BIKE
    # players[2].speed = Transport.BIKE.value[TRAN_SPEED]
    #
    # players[3].transport = Transport.MOTOR_SCOOTER
    # players[3].speed = Transport.MOTOR_SCOOTER.value[TRAN_SPEED]

    while is_running:
        screen.fill((0, 0, 0))

        for ii, pl in enumerate(players):
            pl.draw_level(screen, ii)
            if not is_paused:
                pl.dig()

        if is_paused:
            pygame.draw.rect(screen, DK_GRAY, (TXT_PAUSED_X - 20, TXT_PAUSED_Y - 20, TXT_PAUSED.get_width() + 38, TXT_PAUSED.get_height() + 32), 0, 10)
            screen.blit(TXT_PAUSED, (TXT_PAUSED_X, TXT_PAUSED_Y))

        dt = clock.tick(FPS)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_paused = not is_paused

    pygame.quit()

"""
TODO:
* Add bombs that can clear a cell quickly. Bombs can be purchased from an upgraded home.
* Add gambling where player can win or lose money.
* Bonus/side areas? Accessed via a hole or something to get special items: gambling items, free upgrades, etc

+ Show the transport method over the player icon for (scooter and motor scooter)
+ Movement speed progression: 🥾 > 🛴 > 🚲 > 🛵
+ Chest supply positive/negative effects for player (decrease speed, break current tool, break bicycle, etc)
+ Replace tool when it's too low (<10 durability)
+ Digging takes more time in later levels (2 + area = 2, 3, 4, 5)
+ Add toolboxes (chests) that are returned home to be opened with keys. How do we get keys? Purchase or discover?
+ Add boulders: encountering a boulder adds X time to breaking but results in a guaranteed reward (best of the area?)
+ Sell inventory when nothing left to do.
+ When tool == Hands, draw a hand instead of a pickaxe.
+ Any time you go home, sell inventory
+ If using Hands, as soon as money is available, get a tool.
+ Backpack upgrade
"""
