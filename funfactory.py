import random

from anims.ator_glider import AtorGlider
from anims.bloodbeast import BloodBeast
from anims.deathray import DeathRay
from anims.deathray_crow import DeathRayCrow
from anims.elsanto_flying import ElSantoFlying
from anims.exeter import Exeter
from anims.fingal import Fingal
from anims.gamera import Gamera
from anims.horse_running import HorseRunning
from anims.meteorite import Meteorite
from anims.mood_servo import MoodServo
from anims.moonbug import MoonBug
from anims.mst3k_moon import MST3KMoon
from anims.oh_wow import OhWow
from anims.orbit_jet import OrbitJet
from anims.pizza import Pizza
from anims.pumaman import Pumaman
from anims.sandstorm import SandStorm
from anims.shuriken import Shuriken
from anims.skull import ScreamingSkull
from anims.skydiver import Skydiver
from anims.sol import SOL
from anims.starfighter import Starfighter
from anims.time_chasers_plane import TimeChasersPlane
from anims.time_chasers_plane_other import TimeChasersPlaneOther
from anims.troy_csonka import TroyCsonka
from anims.vi_head import ViHead
from anims.whitedot import WhiteDot
from anims.widowmaker import Widowmaker
from anims.zap_beer import ZapBeer

ANIMS_BY_EPNUM = {
    "111": (MoonBug, 1),
    "301": (AtorGlider, 1),
    "302": (Gamera, 1),
    "304": (Gamera, 1),
    "308": (Gamera, 1),
    "312": (Gamera, 1),
    "316": (Gamera, 1),
    "322": (Shuriken, random.randint(2, 5)),
    "324": (Shuriken, random.randint(2, 5)),
    "410": (SandStorm, random.randint(8, 12)),
    "413": (OrbitJet, 1),
    "414": (ViHead, 1),
    "417": (OrbitJet, 1),
    "609": (Skydiver, 1),
    "611": (HorseRunning, 1),
    "612": (Starfighter, random.randint(3, 5)),
    "620": (DeathRay if random.randint(1, 2) == 1 else DeathRayCrow, 1),
    "624": (ElSantoFlying, 1),
    "701": (BloodBeast, random.randint(6, 10)),
    "701T": (BloodBeast, random.randint(6, 10)),
    "821": ([TimeChasersPlane, TimeChasersPlaneOther] if random.randint(1, 2) == 1 else TimeChasersPlane, 1),
    "822": (Fingal, 1),
    "903": (Pumaman, 1),
    "910": (ZapBeer if random.randint(1, 2) == 1 else TroyCsonka, 1),
    "912": (ScreamingSkull, 1),
    "1007": ([OhWow, Meteorite], random.randint(3, 8)),
    "1304": (Pizza, 1),
    "1306": (MoodServo, 1),
    "1307": (Gamera, 1),
}


def get_by_epnum(screen, epnum: str):
    objs = []

    if epnum in ANIMS_BY_EPNUM.keys():
        anims, num = ANIMS_BY_EPNUM[epnum]
        # print("Fun: " + str(anims))
        for i in range(num):
            if type(anims) is list:
                for a in anims:
                    objs.append(a(screen))
            else:
                objs.append(anims(screen))

    return objs


def get(screen, title: str, epnum: str) -> []:
    return [ViHead(screen)]

    # If the episode has a specific animation, choose it 50% of the time
    if epnum in ANIMS_BY_EPNUM.keys() and random.randint(1, 2) == 1:
        # Choose the specific animation for this episode
        return get_by_epnum(screen, epnum)
    else:
        # Choose a random animation
        if random.randint(1, 10) == 1:
            # Generic animation
            return random.choice([[SOL(screen)],
                                  [SOL(screen), Widowmaker(screen)],
                                  [MST3KMoon(screen)],
                                  [WhiteDot(screen)],
                                  [Exeter(screen)]])

        else:
            return get_by_epnum(screen, random.choice(
                ['111', '301' '302', '322', '410', '413', '414', '701', '609', '611', '612', '620', '624', '821', '822',
                 '903', '910', '912', '1007', '1304', '1306', '1307']))


class FunFactory:
    pass
