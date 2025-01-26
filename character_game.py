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

"""
