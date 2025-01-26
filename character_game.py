import os.path

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
    Character("crow.png", ["Crow", "Crow T Robot"]),
    Character("dave.png", ["Dave", "Dave Randall"]),
    Character("debbie.png", ["Debbie"]),
    Character("DoctorKabahl.png", ["Dr Kabahl", "Kabahl"]),
    Character("donna.png", ["Donna", "Donna Bixby"]),
    Character("EmilyConnor.png", ["Emily", "Emily Connor"]),
    Character("erhardt.png", ["Erhardt", "Larry", "Dr Erhardt", "Dr Larry Erhardt"]),
    Character("fingal.png", ["Fingal", "Aram Fingal", "Aram"]),
    Character("forrester.png", ["Forrester", "Dr Forrester", "Clayton Forrester"]),
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
    Character("max.png", ["Max", "TV's Max"]),
    Character("MegaSynthia.png", ["Mega Synthia", "MegaSynthia"]),
    Character("MichaelManos.png", ["Michael"]),
    Character("Mike.png", ["Mike", "Mike Nelson"]),
    Character("mrb.png", ["Mr B Natural", "Mr B"]),
    Character("MWaverly.png", ["M Waverly"]),
    Character("Natalie.png", ["Natalie", "Natalie Burke"]),
    Character("observer.png", ["Observer", "Brain Guy", "Brainguy"]),
    Character("Pearl.png", ["Pearl", "Pearl Forrester"]),
    Character("phipps.png", ["Phipps", "Alex", "Alexander", "Alex Phipps", "Alexander Phipps"]),
    Character("pipper.png", ["Pipper"]),
    Character("pitch.png", ["Pitch"]),
    Character("sam_the_keeper.png", ["Sam", "Sam the Keeper"]),
    Character("steve.png", ["Steve", "Steve Dunlap"]),
    Character("Synthia.png", ["Synthia"]),
    Character("Tom_Servo.png", ["Servo", "Tom Servo", "Htom Sirveaux"]),
    Character("torgo.png", ["Torgo"]),
    Character("troy.png", ["Troy"]),
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
    Character("pumaman.png", ["Pumaman", "Puma Man"]),
    Character("godzilla.png", ["Godzilla"]),
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
    Character("vi.png", ["Vi"]),
    Character("Cleolanta.png", ["Cleolanta", "Cleolanthe"]),
    Character("winky.png", ["Winky"]),
    Character("rocky_jones.png", ["Rocky Jones"]),
    Character("Vena.png", ["Vena", "Vena Ray"]),
    Character("kolos.png", ["Kolos", "Dr Kolos"]),
    Character("lisa.png", ["Lisa", "Lisa Dornheimer"]),
    Character("bart_fargo.png", ["Bart Fargo", "Bart", "Fargo"]),
    Character("Eegah.png", ["Eegah"]),

    # Character("", [""]),
    # Character("", [""]),
    # Character("", [""]),
]


if __name__ == '__main__':
    # Verify the file names are correct.
    for c in CHARACTERS:
        if not os.path.exists(CHARACTER_PATH + c.img_file):
            print(c.img_file + " is missing")

"""
TODO:
Johnny (Time of Apes)
Godo (Time of Apes)
Krankor
"""
