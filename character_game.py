import os.path
from os import listdir
from os.path import isfile, join

CHARACTER_PATH = "images/characters/"


class Character:
    def __init__(self, img_file: str, names: [str]):
        self.img_file = img_file
        self.names = names


CHARACTERS = [
    Character("Ardy.png", ["Ardy"]),
    Character("beeper.png", ["Beeper"]),
    Character("Bobo.png", ["Bobo", "Professor Bobo"]),
    Character("crenshaw.png", ["Crenshaw"]),
    Character("crow.png", ["Crow", "Crow T Robot", "Art"]),
    Character("dave.png", ["Dave", "Dave Randall"]),
    Character("debbie.png", ["Debbie"]),
    Character("DoctorKabahl.png", ["Dr Kabahl", "Kabahl"]),
    Character("donna.png", ["Donna", "Donna Bixby"]),
    Character("EmilyConnor.png", ["Emily", "Emily Connor"]),
    Character("erhardt.png", ["Erhardt", "Larry", "Dr Erhardt", "Dr Larry Erhardt", "Dr Laurence Erhardt"]),
    Character("fingal.png", ["Fingal", "Aram Fingal", "Aram"]),
    Character("forrester.png", ["Forrester", "Dr Forrester", "Clayton Forrester", "Dr Clayton Forrester"]),
    Character("goosio.png", ["Goosio"]),
    Character("Growler.png", ["Growler"]),
    Character("Gypsy_mst3k.png", ["Gypsy", "GPC"]),
    Character("hobgoblins.png", ["Hobgoblins"]),
    Character("jack_perkins.png", ["Jack Perkins", "Perkins"]),
    Character("jan.png", ["Jan in the Pan", "Jan"]),
    Character("Joel.png", ["Joel", "Joel Robinson"]),
    Character("JonahHeston.png", ["Jonah", "Jonah Heston"]),
    Character("judy.png", ["Judy"]),
    Character("kinga.png", ["Kinga", "Kinga Forrester"]),
    Character("Margaret.png", ["Margaret"]),
    Character("master.png", ["The Master", "Master"]),
    Character("max.png", ["Max", "TV's Max", "TV's Son of TV's Frank"]),
    Character("MegaSynthia.png", ["Mega Synthia", "MegaSynthia"]),
    Character("MichaelManos.png", ["Michael"]),
    Character("Mike.png", ["Mike", "Mike Nelson"]),
    Character("mrb.png", ["Mr B Natural", "Mr B"]),
    Character("MWaverly.png", ["M Waverly"]),
    Character("Nanites.png", ["Nanites"]),
    Character("Natalie.png", ["Natalie", "Natalie Burke"]),
    Character("observer.png", ["Observer", "Brain Guy", "Brainguy"]),
    Character("Pearl.png", ["Pearl", "Pearl Forrester"]),
    Character("phipps.png", ["Alexander Phipps", "Alex", "Alexander", "Alex Phipps", "Phipps"]),
    Character("pipper.png", ["Pipper", "Mike Pipper"]),
    Character("pitch.png", ["Pitch"]),
    Character("sam_the_keeper.png", ["Sam", "Sam the Keeper"]),
    Character("steve.png", ["Steve", "Steve Dunlap"]),
    Character("Synthia.png", ["Synthia"]),
    Character("Tom_Servo.png", ["Servo", "Tom Servo", "Htom Sirveaux"]),
    Character("torgo.png", ["Torgo"]),
    Character("troy.png", ["Troy", "Troy McGreggor"]),
    Character("TVs_Frank.png", ["Frank", "TV's Frank"]),
    Character("Yuri.png", ["Yuri"]),
    Character("ZapRowsdower.png", ["Rowsdower", "Zap", "Zap Rowsdower"]),

    Character("barugon.png", ["Barugon"]),
    Character("gamera.png", ["Gamera"]),
    Character("gaos.png", ["Gaos", "Gyaos"]),
    Character("guiron.png", ["Guiron"]),
    Character("zigra.png", ["Zigra"]),
    Character("jiger.png", ["Jiger"]),

    Character("geronimo.png", ["Geronimo", "Thomas Jefferson Geronimo", "Thomas Jefferson Geronimo III", "Deputy Sheriff Thomas Jefferson Geronimo III"]),
    Character("mitchell.png", ["Mitchell"]),
    Character("ortega.png", ["Ortega"]),
    Character("pumaman.png", ["Puma Man", "Pumaman"]),
    Character("godzilla.png", ["Godzilla", "Gojira"]),
    Character("gorgo.png", ["Gorgo"]),
    Character("trumpy.png", ["Trumpy"]),
    Character("derek.png", ["Derek"]),
    Character("betty.png", ["Betty", "Betty Morgan"]),
    Character("captjoe.png", ["Captain Joe", "Capt Joe", "Cap Joe"]),
    Character("daddy-o.png", ["Daddy-O", "DaddyO", "Phil", "Phil Sandifer"]),
    Character("pepe.png", ["Pepe"]),
    Character("godo.png", ["Godo"]),
    Character("johnny_longbow.png", ["Johnny Longbow", "Johnny Long Bow", "Johnny Longbone", "Johnny Long Bone"]),
    Character("frost.png", ["Morozko", "Father Frost", "Jack Frost", "Frost", "Frosty"]),
    Character("hercules.png", ["Hercules"]),

    Character("tom_stewart.png", ["Tom Stewart", "Tom"]),
    Character("vi.png", ["Vi", "movievVi"]),
    Character("Cleolanta.png", ["Cleolanta", "Cleolanthe"]),
    Character("winky.png", ["Winky"]),
    Character("rocky_jones.png", ["Rocky Jones"]),
    Character("Vena.png", ["Vena", "Vena Ray"]),
    Character("kolos.png", ["Kolos", "Dr Kolos"]),
    Character("lisa.png", ["Lisa", "Lisa Dornheimer"]),
    Character("bart_fargo.png", ["Bart Fargo", "Bart", "Fargo"]),
    Character("Eegah.png", ["Eegah"]),
    Character("bix.png", ["Bix Dugan", "Big Stupid", "Bix"]),
    Character("carrie.png", ["Carrie", "Carrie Anders"]),
    Character("mikey.png", ["Mikey"]),

    Character("Batwoman.png", ["Batwoman", "Bat Woman"]),
    Character("cabot.png", ["Cabot"]),
    Character("watney.png", ["Watney", "Whatney"]),
    Character("xenos.png", ["Xenos"]),
    Character("lara.png", ["Lara"]),

    Character("gloria.png", ["Gloria", "Gloria Henderson"]),
    Character("dirk.png", ["Dirk", "Dirk Williams"]),
    Character("marv.png", ["Marv", "Marv Grant"]),

    Character("cherokee_jack.png", ["Cherokee Jack"]),
    Character("exeter.png", ["Exeter"]),
    Character("hal_moffat.png", ["Hal Moffat", "The Creeper", "Hal", "Creeper"]),

    Character("billy.png", ["Billy", "Billy Duncan"]),
    Character("froggy.png", ["Froggy"]),
    Character("trash.png", ["Trash"]),
    Character("dablone.png", ["Dablone", "Toblerone"]),
    Character("deathstalker.png", ["Deathstalker", "Death Stalker"]),
    Character("Princeofspace.png", ["Prince of Space"]),
    Character("vance.png", ["Vance", "Dr Vance"]),
    Character("Vorelli.png", ["Vorelli", "The Great Vorelli"]),

    Character("david_ryder.png", ["Dave Ryder", "David Ryder", "Ryder"]),
    Character("eddie.png", ["Eddie", "Eddie Nelson"]),
    Character("krankor.png", ["Phantom of Krankor", "Krankor"]),
    Character("space_chief.png", ["Space Chief"]),
    Character("apollonia.png", ["Apollonia", "Apollonia James"]),
    Character("frank_chapman.png", ["Frank Chapman", "Chapman"]),
    Character("Vadinho.png", ["Vadinho"]),
    Character("Roadrash.png", ["Roadrash", "Road Rash"]),
    Character("dorkin.png", ["Dorkin"]),
    Character("mickey.png", ["Mickey"]),

    Character("Leonardo.png", ["Leonardo"]),
    Character("thena.png", ["Thena"]),
    Character("Merlin.png", ["Merlin"]),
    Character("hamlet.png", ["Hamlet"]),
    Character("tim.png", ["Tim", "Tim Thorton"]),
    Character("diabolik.png", ["Diabolik"]),
    Character("santo.png", ["Santo", "El Santo"]),
    Character("drake.png", ["Drake", "Marion Drake"]),
    Character("east_eddie.png", ["East Eddie"]),
    Character("nereus.png", ["Nereus"]),
    Character("syrene.png", ["Syrene"]),
    Character("munchie.png", ["Munchie"]),
    Character("drmordrid.png", ["Dr Mordrid", "Doctor Mordrid", "Anton Mordrid", "Dr Anton Mordrid", "Mordrid"]),
    Character("cabal.png", ["Cabal"]),
    Character("nickmoon.png", ["Nick Moon"]),
    Character("Batwoman2.png", ["Batwoman", "Bat Woman"]),
    Character("boong.png", ["Boong", "President Boong"]),
    Character("sumuru.png", ["Sumuru"]),
    Character("omus.png", ["Omus"]),
    Character("gpc2.png", ["GPC 2", "GPC2"]),
    Character("Cambot.png", ["Cambot"]),
    Character("Sorri_Andropoli.png", ["Sorri", "Sorri Andropoli"]),
    Character("Leonard_Maltin.png", ["Leonard Maltin", "Maltin"]),
    Character("glennmanning.png", ["Glenn Manning", "Glen Manning"]),
    Character("megaweapon.png", ["Megaweapon", "Mega Weapon"]),
    Character("Minsky.png", ["Minsky"]),
    Character("nuveena.png", ["Nuveena"]),
    Character("big_jake.png", ["Big Jake"]),
    Character("steffi.png", ["Steffi", "Steffi the Babysitter"]),
    Character("tibby.png", ["Tibby"]),
    Character("timmy.png", ["Timmy"]),
    Character("Scooter.png", ["Scooter"]),
    Character("valeria.png", ["Valeria"]),
    Character("mooney.png", ["Mooney", "Moon", "Bob Mooney"]),
    Character("Gooch.png", ["Gooch", "Cooch"]),
    Character("monad.png", ["Monad"]),
    Character("mothra.png", ["Mothra"]),
    Character("mac.png", ["Mac"]),

    # Character("", [""]),
]


if __name__ == '__main__':
    # Verify the file names are correct.
    for c in CHARACTERS:
        if not os.path.exists(CHARACTER_PATH + c.img_file):
            print(c.img_file + " is missing")

    allfiles = [f for f in listdir(CHARACTER_PATH) if isfile(join(CHARACTER_PATH, f))]
    for file in allfiles:
        found = False
        for c in CHARACTERS:
            if c.img_file == file:
                found = True
                break
        if not found:
            print("File " + file + " has no Character")
