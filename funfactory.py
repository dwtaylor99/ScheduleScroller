import random

from pygame import Surface

from deathray import DeathRay
from elsanto_flying import ElSantoFlying
from gamera import Gamera
from meteorite import Meteorite
from mst3k_moon import MST3KMoon
from sandstorm import SandStorm
from sol import SOL
from starfighter import Starfighter
from ufo import Ufo
from vampire_woman import VampireWoman
from widowmaker import Widowmaker


def get(screen: Surface, title: str, epnum: str) -> []:
    fun_objs = []

    if epnum == "1007":
        for _ in range(random.randrange(3, 8)):
            fun_objs.append(Meteorite(screen))

    if epnum == "620":
        fun_objs.append(DeathRay(screen))

    if epnum in ["302", "304", "308", "312", "316", "1307"]:
        fun_objs.append(Gamera(screen))

    if epnum == "410":
        for _ in range(random.randrange(5, 10)):
            fun_objs.append(SandStorm(screen))

    if epnum == "612":
        for _ in range(random.randrange(3, 5)):
            fun_objs.append(Starfighter(screen))

    if epnum == "624":
        vamp_wom = VampireWoman(screen)
        fun_objs.append(vamp_wom)
        fun_objs.append(ElSantoFlying(screen, vamp_wom.x, vamp_wom.y))

    # No special fun thing
    if len(fun_objs) == 0:
        r = random.randrange(1, 3)
        # r = 3
        if r == 1:
            fun_objs.append(Ufo(screen))
        elif r == 2:
            fun_objs.append(MST3KMoon(screen))
        elif r == 3:
            fun_objs.append(SOL(screen))
            fun_objs.append(Widowmaker(screen))

    return fun_objs


class FunFactory:
    pass
