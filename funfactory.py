import random

from anims.ator_glider import AtorGlider
from anims.bloodbeast import BloodBeast
from anims.deathray import DeathRay
from anims.deathray_crow import DeathRayCrow
from anims.elsanto_flying import ElSantoFlying
from anims.enforcer import Enforcer
from anims.enforcer_chase import EnforcerChase
from anims.exeter import Exeter
from anims.fingal import Fingal
from anims.forklift import Forklift
from anims.gamera import Gamera
from anims.horse_running import HorseRunning
from anims.meteorite import Meteorite
from anims.mood_servo import MoodServo
from anims.moonbug import MoonBug
from anims.mst3k_moon import MST3KMoon
from anims.munchie_pizza import MunchiePizza
from anims.oh_wow import OhWow
from anims.orbit_jet import OrbitJet
from anims.pumaman import Pumaman
from anims.sandstorm import SandStorm
from anims.shuriken import Shuriken
from anims.skull import ScreamingSkull
from anims.skydiver import Skydiver
from anims.sol import SOL
from anims.starfighter import Starfighter
from anims.time_chasers_plane import TimeChasersPlane
from anims.time_chasers_plane_other import TimeChasersPlaneOther
from anims.torgo import Torgo
from anims.troy_dream import TroyDream
from anims.trumpy import Trumpy
from anims.vi_head import ViHead
from anims.whitedot import WhiteDot
from anims.widowmaker import Widowmaker
from anims.zap_beer import ZapBeer

ANIMS_BY_EPNUM = {
    "001": (SOL, 1),
    "002": ([SOL, Widowmaker], 1),
    "003": (MST3KMoon, 1),
    "004": (WhiteDot, 1),
    "005": (Exeter, 1),
    "111": (MoonBug, 1),
    "301": (AtorGlider, 1),
    "302": (Gamera, 1),
    "303": (Trumpy, 1),
    "304": (Gamera, 1),
    "308": (Gamera, 1),
    "310": (Forklift, 1),
    "312": (Gamera, 1),
    "316": (Gamera, 1),
    "322": (Shuriken, random.randint(2, 5)),
    "324": (Shuriken, random.randint(2, 5)),
    "410": (SandStorm, random.randint(8, 12)),
    "413": (OrbitJet, 1),
    "414": (ViHead, 1),
    "417": (OrbitJet, 1),
    "424": (Torgo, 1),
    "609": (Skydiver, 1),
    "611": (HorseRunning, 1),
    "612": (Starfighter, random.randint(3, 5)),
    "620": (DeathRay if random.randint(1, 2) == 1 else DeathRayCrow, 1),
    "624": (ElSantoFlying, 1),
    "701": (BloodBeast, random.randint(6, 10)),
    "701T": (BloodBeast, random.randint(6, 10)),
    "820": (Enforcer if random.randint(1, 2) == 1 else EnforcerChase, 1),
    "821": ([TimeChasersPlane, TimeChasersPlaneOther] if random.randint(1, 2) == 1 else TimeChasersPlane, 1),
    "822": (Fingal, 1),
    "903": (Pumaman, 1),
    "910": (ZapBeer if random.randint(1, 2) == 1 else TroyDream, 1),
    "912": (ScreamingSkull, 1),
    "1007": ([OhWow, Meteorite], random.randint(3, 8)),
    "1304": (MunchiePizza, 1),
    "1306": (MoodServo, 1),
    "1307": (Gamera, 1),
}


def get_by_epnum(screen, epnum: str):
    objs = []

    if epnum in ANIMS_BY_EPNUM.keys():
        anims, count = ANIMS_BY_EPNUM[epnum]
        for i in range(count):
            if type(anims) is list:
                for a in anims:
                    objs.append(a(screen))
            else:
                objs.append(anims(screen))

    return objs


def get(screen, title: str, epnum: str) -> []:
    # If the episode has a specific animation, choose it 50% of the time
    if epnum in ANIMS_BY_EPNUM.keys() and random.randint(1, 2) == 1:
        return get_by_epnum(screen, epnum)
    else:
        # Choose a random animation
        return get_by_epnum(screen, random.choice(
            ['001', '002', '003', '004', '005',
             '111', '301', '302', '303', '310', '322', '410', '413', '414', '424', '609', '611', '612', '620', '624',
             '701', '820', '821', '822', '903', '910', '912', '1007', '1304', '1306', '1307']))


class FunFactory:
    pass
