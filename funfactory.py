import random

from pygame import Surface

from anims.deathray import DeathRay
from anims.elsanto_flying import ElSantoFlying
from anims.gamera import Gamera
from anims.horse_running import HorseRunning
from anims.meteorite import Meteorite
from anims.mood_servo import MoodServo
from anims.mst3k_moon import MST3KMoon
from anims.sandstorm import SandStorm
from anims.shuriken import Shuriken
from anims.skydiver import Skydiver
from anims.sol import SOL
from anims.starfighter import Starfighter
from anims.time_chasers_plane import TimeChasersPlane
from anims.time_chasers_plane_other import TimeChasersPlaneOther
from anims.vampire_woman import VampireWoman
from anims.vi_head import ViHead
from anims.widowmaker import Widowmaker
from anims.zap_beer import ZapBeer


def get(screen: Surface, title: str, epnum: str) -> []:
    fun_objs = []

    r = random.randint(1, 17)

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

    if r == 17:
        for _ in range(random.randrange(2, 5)):
            fun_objs.append(Shuriken(screen))

    return fun_objs


class FunFactory:
    pass
