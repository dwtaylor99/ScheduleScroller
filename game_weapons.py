import pygame


class Weapon:
    def __init__(self, name, base_damage=1):
        self.base_damage = base_damage
        self.name = name
        self.img = pygame.Surface((1, 1))


class Fists(Weapon):
    def __init__(self, base_damage=1):
        super().__init__("Fists", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/fist_r.png"),
                                                   0.5).convert_alpha()


class Knife(Weapon):
    def __init__(self, base_damage=2):
        super().__init__("Knife", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/kitchen_knife.png"),
                                                   0.5).convert_alpha()


class WoodenBat(Weapon):
    def __init__(self, base_damage=3):
        super().__init__("Wooden Bat", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/wooden_bat.png"),
                                                   0.5).convert_alpha()


class MetalBat(Weapon):
    def __init__(self, base_damage=4):
        super().__init__("Metal Bat", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/metal_bat.png"),
                                                   0.5).convert_alpha()


class Nightstick(Weapon):
    def __init__(self, base_damage=4):
        super().__init__("Nightstick", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/baton.png"),
                                                   0.5).convert_alpha()


class Machete(Weapon):
    def __init__(self, base_damage=5):
        super().__init__("Machete", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/machete.png"),
                                                   0.5).convert_alpha()


class Axe(Weapon):
    def __init__(self, base_damage=5):
        super().__init__("Axe", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/axe.png"),
                                                   0.5).convert_alpha()


class Sledgehammer(Weapon):
    def __init__(self, base_damage=5):
        super().__init__("Sledgehammer", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/sledgehammer.png"),
                                                   0.5).convert_alpha()


class Katana(Weapon):
    def __init__(self, base_damage=6):
        super().__init__("Katana", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/katana.png"),
                                                   0.5).convert_alpha()


class Sword(Weapon):
    def __init__(self, base_damage=6):
        super().__init__("Sword", base_damage)
        self.img = pygame.transform.smoothscale_by(pygame.image.load("images/game/weapon/sword.png"),
                                                   0.5).convert_alpha()
