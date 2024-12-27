import random

from pygame import Surface

from deathray import DeathRay
from elsanto_flying import ElSantoFlying
from gamera import Gamera
from horse_running import HorseRunning
from meteorite import Meteorite
from mood_servo import MoodServo
from mst3k_moon import MST3KMoon
from sandstorm import SandStorm
from santa_sleigh import SantaSleigh
from skydiver import Skydiver
from sol import SOL
from starfighter import Starfighter
from time_chasers_plane import TimeChasersPlane
from time_chasers_plane_other import TimeChasersPlaneOther
from vampire_woman import VampireWoman
from vi_head import ViHead
from widowmaker import Widowmaker
from zap_beer import ZapBeer


def get_old(screen: Surface, title: str, epnum: str) -> []:
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
        r = random.randrange(1, 4)
        print("Random number: ", r)
        if r == 1:
            fun_objs.append(SOL(screen))
        elif r == 2:
            fun_objs.append(MST3KMoon(screen))
        elif r == 3:
            fun_objs.append(SOL(screen))
            fun_objs.append(Widowmaker(screen))

    return fun_objs


def get(screen: Surface, title: str, epnum: str) -> []:
    fun_objs = []

    r = random.randint(1, 16)

    if r == 1:
        for _ in range(random.randrange(3, 8)):
            fun_objs.append(Meteorite(screen))

    if r == 2:
        fun_objs.append(DeathRay(screen))

    if r == 3:
        fun_objs.append(Gamera(screen))

    if r == 4:
        for _ in range(random.randrange(5, 10)):
            fun_objs.append(SandStorm(screen))

    if r == 5:
        for _ in range(random.randrange(3, 5)):
            fun_objs.append(Starfighter(screen))

    if r == 6:
        vamp_wom = VampireWoman(screen)
        fun_objs.append(vamp_wom)
        fun_objs.append(ElSantoFlying(screen, vamp_wom.x, vamp_wom.y))

    if r == 7:
        fun_objs.append(SOL(screen))

    if r == 8:
        fun_objs.append(MST3KMoon(screen))

    if r == 9:
        fun_objs.append(SOL(screen))
        fun_objs.append(Widowmaker(screen))

    if r == 10:
        fun_objs.append(ViHead(screen))

    if r == 11:
        fun_objs.append(TimeChasersPlane(screen))

    if r == 12:
        fun_objs.append(TimeChasersPlane(screen))
        fun_objs.append(TimeChasersPlaneOther(screen))

    if r == 13:
        fun_objs.append(HorseRunning(screen))

    if r == 14:
        # fun_objs.append(SantaSleigh(screen))
        fun_objs.append(ZapBeer(screen))

    if r == 15:
        fun_objs.append(Skydiver(screen))

    if r == 16:
        fun_objs.append(MoodServo(screen))

    return fun_objs


class FunFactory:
    pass
