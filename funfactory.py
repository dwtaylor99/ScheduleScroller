import random

from anims.deathray import DeathRay
from anims.elsanto_flying import ElSantoFlying
from anims.fingal import Fingal
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
from anims.vi_head import ViHead
from anims.widowmaker import Widowmaker
from anims.zap_beer import ZapBeer
from scroller import screen


def get_by_epnum(epnum: str):
    objs = []

    if epnum in ['302', '304', '308', '312', '316', '1307']:
        print("Fun: Gamera")
        objs.append(Gamera(screen))
    elif epnum in ['322', '324']:
        print("Fun: Shuriken")
        for _ in range(random.randrange(2, 5)):
            objs.append(Shuriken(screen))
    elif epnum == "410":
        print("Fun: Sandstorm")
        for _ in range(random.randrange(5, 10)):
            objs.append(SandStorm(screen))
    elif epnum in ["413", "417"]:
        print("Fun: OrbitJet")
        objs.append(OrbitJet(screen))
    elif epnum == "414":
        print("Fun: ViHead")
        objs.append(ViHead(screen))
    elif epnum == "609":
        print("Fun: Skydiver")
        objs.append(Skydiver(screen))
    elif epnum == "611":
        print("Fun: HorseRunning")
        objs.append(HorseRunning(screen))
    elif epnum == "612":
        print("Fun: Starfighters")
        for _ in range(random.randrange(3, 5)):
            objs.append(Starfighter(screen))
    elif epnum == "620":
        print("Fun: Deathray")
        objs.append(DeathRay(screen))
    elif epnum == "624":
        print("Fun: ElSanto")
        objs.append(ElSantoFlying(screen))
    elif epnum == "821":
        print("Fun: TimeChasers")
        objs.append(TimeChasersPlane(screen))
        if random.randrange(1, 2) == 1:
            print("Fun: TimeChasersOther")
            objs.append(TimeChasersPlaneOther(screen))
    elif epnum == "822":
        print("Fun: Fingal")
        objs.append(Fingal(screen))
    elif epnum == "910":
        if random.randrange(1, 2) == 1:
            print("Fun: Troy")
            objs.append(TroyCsonka(screen))
        else:
            print("Fun: Zap")
            objs.append(ZapBeer(screen))
    elif epnum == "1007":
        print("Fun: Meteorite")
        for _ in range(random.randrange(3, 8)):
            objs.append(Meteorite(screen))
    elif epnum == "1306":
        print("Fun: MoodServo")
        objs.append(MoodServo(screen))

    return objs


def get(title: str, epnum: str) -> []:
    anim_list = ['302', '304', '308', '312', '316', '322', '324', '410', '413', '414', '417',
                 '609', '611', '612', '620', '624', '812', '821', '822', '910', '1007',
                 '1306', '1307']

    # If the episode has an animation, choose it 50% of the time
    if epnum in anim_list and random.randrange(1, 2) == 1:
        # Choose the specific animation for this episode
        return get_by_epnum(epnum)
    else:
        # Choose a random animation
        if random.randrange(1, 10) == 1:
            # Generic animation
            rn = random.randrange(1, 3)
            if rn == 1:
                print("Fun: SOL")
                return [SOL(screen)]
            elif rn == 2:
                print("Fun: SOL, Widowmaker")
                return [SOL(screen), Widowmaker(screen)]
            elif rn == 3:
                print("Fun: MST3KMoon")
                return [MST3KMoon(screen)]
        else:
            return get_by_epnum(random.choice(['302', '322', '410', '413', '414', '609', '611', '612', '620', '624',
                                               '812', '821', '822', '910', '1007', '1306', '1307']))


class FunFactory:
    pass
