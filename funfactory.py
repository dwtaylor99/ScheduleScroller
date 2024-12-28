import random

from pygame import Surface

from anims.deathray import DeathRay
from anims.elsanto_flying import ElSantoFlying
from anims.gamera import Gamera
from anims.horse_running import HorseRunning
from anims.meteorite import Meteorite
from anims.mood_servo import MoodServo
from anims.mst3k_moon import MST3KMoon
from anims.orbit_jet import OrbitJet
from anims.sandstorm import SandStorm
from anims.shuriken import Shuriken
from anims.skydiver import Skydiver
from anims.sol import SOL
from anims.starfighter import Starfighter
from anims.time_chasers_plane import TimeChasersPlane
from anims.time_chasers_plane_other import TimeChasersPlaneOther
from anims.troy_csonka import TroyCsonka
from anims.vampire_woman import VampireWoman
from anims.vi_head import ViHead
from anims.widowmaker import Widowmaker
from anims.zap_beer import ZapBeer
from scroller import DEBUG


def get_by_epnum(screen, epnum: str):
    objs = []

    if epnum in ['302', '304', '308', '312', '316', '1307']:
        objs.append(Gamera(screen))
    elif epnum in ['322', '324']:
        for _ in range(random.randrange(2, 5)):
            objs.append(Shuriken(screen))
    elif epnum == "410":
        for _ in range(random.randrange(5, 10)):
            objs.append(SandStorm(screen))
    elif epnum in ["413", "417"]:
        objs.append(OrbitJet(screen))
    elif epnum == "414":
        objs.append(ViHead(screen))
    elif epnum == "609":
        objs.append(Skydiver(screen))
    elif epnum == "611":
        objs.append(HorseRunning(screen))
    elif epnum == "612":
        for _ in range(random.randrange(3, 5)):
            objs.append(Starfighter(screen))
    elif epnum == "620":
        objs.append(DeathRay(screen))
    elif epnum == "624":
        vamp_wom = VampireWoman(screen)
        objs.append(vamp_wom)
        objs.append(ElSantoFlying(screen, vamp_wom.x, vamp_wom.y))
    elif epnum == "821":
        if random.randrange(1, 2) == 1:
            objs.append(TimeChasersPlane(screen))
        else:
            objs.append(TimeChasersPlane(screen))
            objs.append(TimeChasersPlaneOther(screen))
    elif epnum == "910":
        if random.randrange(1, 2) == 1:
            objs.append(TroyCsonka(screen))
        else:
            objs.append(ZapBeer(screen))
    elif epnum == "1007":
        for _ in range(random.randrange(3, 8)):
            objs.append(Meteorite(screen))
    elif epnum == "1306":
        objs.append(MoodServo(screen))

    return objs


def get(screen: Surface, title: str, epnum: str) -> []:
    anim_list = ['302', '304', '308', '312', '316', '322', '324', '410', '413', '414', '417',
                 '609', '611', '612', '620', '624', '812', '821', '910', '1007',
                 '1306', '1307']

    if DEBUG:
        return [TroyCsonka(screen)]

    # If the episode has an animation, choose it 50% of the time
    if epnum in anim_list and random.randrange(1, 2) == 1:
        # Choose the specific animation for this episode
        return get_by_epnum(screen, epnum)
    else:
        # Choose a random animation
        if random.randrange(1, 10) == 1:
            # Generic animation
            rn = random.randrange(1, 3)
            if rn == 1:
                return [SOL(screen)]
            elif rn == 2:
                return [SOL(screen), Widowmaker(screen)]
            elif rn == 3:
                return [MST3KMoon(screen)]
        else:
            return get_by_epnum(screen, random.choice(anim_list))


class FunFactory:
    pass
