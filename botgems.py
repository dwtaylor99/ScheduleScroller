import json
import os.path

GEM = "💎"
GEM_FILE = "data/gems.json"
GEM_REDEEM = 5


def verify_file():
    if not os.path.exists(GEM_FILE):
        with open(GEM_FILE, "w+") as f:
            f.write("[]")
            f.close()


def get_gems(username: str) -> int:
    verify_file()

    gems = 0
    with open(GEM_FILE, "r", encoding='utf-8') as jsonfile:
        winners = json.load(jsonfile)
        jsonfile.close()
        for w in winners:
            if w["name"].lower() == username.lower():
                gems = w["gems"]
                break

    return gems


def save_gems(username: str, gems: int):
    verify_file()

    with open(GEM_FILE, "r") as jsonfile:
        winners = json.load(jsonfile)
        jsonfile.close()

    found = False
    for k in winners:
        if k["name"].lower() == username.lower():
            k["gems"] = gems
            found = True
            break

    if not found:
        winners.append({"name": username, "gems": gems})

    with open(GEM_FILE, "w") as jsonfile:
        json.dump(winners, jsonfile, indent=2)
        jsonfile.close()


def save_winners(winner_list: [str], sub_list):
    """Save winner and number of wins to file."""
    verify_file()

    with open(GEM_FILE, "r") as jsonfile:
        winners = json.load(jsonfile)
        jsonfile.close()

    # If the 'gems.json' file is empty, re-init the 'winners' obj as an array
    if len(winners) == 0:
        winners = []

    for author in winner_list:
        found = False
        for k in winners:
            if k["name"].lower() == author.lower():
                # add the mixed case version of the name
                k["gems"] = k["gems"] + (1 if author not in sub_list else 2)
                found = True
                break

        if not found:
            winners.append({"name": author, "gems": 1})

    with open(GEM_FILE, "w") as jsonfile:
        json.dump(winners, jsonfile, indent=2)
        jsonfile.close()


if __name__ == '__main__':
    save_gems("LeftFourDave", 100)
    print(get_gems("LeftFourDave"))
