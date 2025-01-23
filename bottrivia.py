import csv
import json
import operator
import os
import urllib.error
import urllib.request
from datetime import datetime
from random import shuffle

IS_DEBUG = False
MAX_RESULTS: int = 5  # Default number of top players to display
TRIVIA_MINUTE: int = 10  # Minute of the hour to start Triva
TRIVIA_GAUNTLET: bool = False  # Are we currently in a Trivia Gauntlet?
TRIVIA_WINNERS = "/me Congratulations to trivia winners "
TRIVIA_FILE = "data/trivia.csv"
TRIVIA_ORDER_FILE = "data/trivia_order.txt"
TRIVIA_WINNERS_FILE = "../../MovieVox/trivia_winners.json"


class Trivia:
    def __init__(self, question, answers):
        self.question: str = question
        self.answers: list[str] = answers

    def __str__(self):
        return "[Q: {}, A: {}]".format(self.question, self.answers)


class TriviaCollection:
    def __init__(self):
        self.trivia: list[Trivia] = []
        self.trivia_winners: list[str] = []

    def __str__(self):
        s = ""
        for t in self.trivia:
            s += "[Q: {}, A: {}]".format(t.question, t.answers)
        return s


def format_winners(winners):
    """Format list of top N winners"""
    if len(winners) == 0:
        return "No trivia winners yet."

    output = []
    player_rank = 1
    for w in winners:
        output.append("{}. {} ({})".format(player_rank, w["name"], w["points"]))
        player_rank += 1

    return " | ".join(output)


def format_round_winners(name_and_points: [str]) -> str:
    """Format winners of the trivia round with commas and 'and'."""
    output = ""
    if len(name_and_points) == 1:
        output = TRIVIA_WINNERS + name_and_points[0]
    elif len(name_and_points) == 2:
        output = TRIVIA_WINNERS + name_and_points[0] + " and " + name_and_points[1]
    elif len(name_and_points) > 2:
        output = TRIVIA_WINNERS + ", ".join(name_and_points[:-1]) + ", and " + name_and_points[-1]
    return output


def get_monthly_filename() -> str:
    return "trivia_winners_" + datetime.strftime(datetime.now(), "%Y_%m") + ".json"


def get_backup_filename() -> str:
    return "trivia_one_point_" + datetime.strftime(datetime.now(), "%Y_%m") + ".json"


def get_trivia_question_new(trivia_coll):
    """Load the trivia history and choose a new question not in the history"""

    if not os.path.exists("trivia_history.txt"):
        with open("trivia_history.txt", "w+", encoding="utf-8") as f:
            f.close()

    with open("trivia_history.txt", "r", encoding="utf-8") as trivia_file:
        lines = trivia_file.readlines()
        trivia_file.close()

    print(lines)


def get_trivia_question(trivia_coll):
    """Lookup the next trivia question and advance the index in the trivia_order file."""
    with open("trivia_order.txt", "r", encoding="utf-8") as trivia_order_file:
        lines = trivia_order_file.readlines()
        trivia_order_file.close()

    count = int(lines[0].strip().split('=')[1])
    index = int(lines[1].strip().split('=')[1])
    num = int(lines[index + 2].strip())

    if num > len(lines) - 2:
        print("Skipping trivia num: " + str(num))
        trivia_order_update(lines, index)

        with open("trivia_order.txt", "r", encoding="utf-8") as trivia_order_file:
            lines = trivia_order_file.readlines()
            trivia_order_file.close()

        count = int(lines[0].strip().split('=')[1])
        index = int(lines[1].strip().split('=')[1])
        num = int(lines[index + 2].strip())

    if index == count - 1:
        trivia_order_shuffle()
    else:
        trivia_order_update(lines, index)

    return trivia_coll.trivia[num]


def get_trivia_points(name):
    """Get the trivia points for a user."""
    points = 0

    with open(TRIVIA_WINNERS_FILE, "r", encoding='utf-8') as jsonfile:
        winners = json.load(jsonfile)
        jsonfile.close()
        for w in winners:
            if w["name"].lower() == name.lower():
                points = w["points"]
                break

    return points


def load_sorted_list():
    """Load the trivia winners and sort the list from most points to least."""
    with open(TRIVIA_WINNERS_FILE, "r") as jsonfile:
        data = json.load(jsonfile)
        jsonfile.close()

    data.sort(key=operator.itemgetter('points'), reverse=True)
    return data


def load() -> TriviaCollection:
    """Load all trivia questions and answers into a TriviaCollection object."""
    trivia_coll = TriviaCollection()
    with open(TRIVIA_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            if reader.line_num < 5 and len(line) > 0 and line[0].lower() == "<!doctype html>":
                break

            if reader.line_num > 1 and len(line) > 1:
                question = line.pop(0)
                answers = list(filter(None, line))  # Only add non-empty strings to the list of answers
                trivia_coll.trivia.append(Trivia(question, answers))

        csvfile.close()

    return trivia_coll


def load_as_array() -> [Trivia]:
    """Load all trivia questions and answers into an array (not a TriviaCollection)."""
    trivia_coll = []
    with open(TRIVIA_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            if reader.line_num < 5 and len(line) > 0 and line[0].lower() == "<!doctype html>":
                break

            if reader.line_num > 1 and len(line) > 1:
                question = line.pop(0)
                answers = list(filter(None, line))  # Only add non-empty strings to the list of answers
                trivia_coll.append(Trivia(question, answers))

        csvfile.close()

    return trivia_coll


def rank(username):
    """Find the rank of the player in the list of all players."""
    rk = 0
    tops = load_sorted_list()

    for winner in tops:
        rk += 1
        if winner["name"].lower() == username.lower():
            break

    return rk


def refresh():
    """Update the trivia from the Internet then load the trivia."""
    update()
    return load()


def save_trivia_user_with_points(username: str, points: int):
    with open(TRIVIA_WINNERS_FILE, "r") as jsonfile:
        winners = json.load(jsonfile)
        jsonfile.close()

    found = False
    for k in winners:
        if k["name"].lower() == username.lower():
            # delete the lowercase version of the name, if one exists
            winners.remove(k)

            # add the mixed case version of the name
            winners.append({
                "name": username,
                "points": points
            })
            found = True
            break

    if not found:
        winners.append({"name": username, "points": points})

    if IS_DEBUG:
        print(winners)
    else:
        with open(TRIVIA_WINNERS_FILE, "w") as jsonfile:
            json.dump(winners, jsonfile, indent=2)
            jsonfile.close()


def save_trivia_winners(winner_list: [str]):
    """Save winner and number of wins to file."""
    if not os.path.exists(TRIVIA_WINNERS_FILE):
        with open(TRIVIA_WINNERS_FILE, "w") as jsonfile:
            json.dump({}, jsonfile)
            jsonfile.close()

    # if not os.path.exists(get_monthly_filename()):
    #     with open(get_monthly_filename(), "w+") as monthlyjson:
    #         json.dump({}, monthlyjson)
    #         monthlyjson.close()

    with open(TRIVIA_WINNERS_FILE, "r") as jsonfile:
        winners = json.load(jsonfile)
        jsonfile.close()

    # If the 'trivia_winners.json' file is empty, re-init the 'winners' obj as an array
    if len(winners) == 0:
        winners = []

    for author in winner_list:
        found = False
        for k in winners:
            if k["name"].lower() == author.lower():
                wins = k["points"]

                # delete the lowercase version of the name, if one exists
                winners.remove(k)

                # add the mixed case version of the name
                winners.append({
                    "name": author,
                    "points": wins + 1
                })
                found = True
                break

        if not found:
            winners.append({"name": author, "points": 1})

    with open(TRIVIA_WINNERS_FILE, "w") as jsonfile:
        json.dump(winners, jsonfile, indent=2)
        jsonfile.close()

    # with open(get_monthly_filename(), "a+") as f:
    #     json.dump(winners, jsonfile, indent=2)
    #     f.close()


def remove_1point_users():
    w = load_sorted_list()
    new_list = []
    one_point_list = []
    for a in w:
        if a['points'] > 1:
            new_list.append(a)
        else:
            one_point_list.append(a)

    # save the 1-pointers to a backup file
    with open(get_backup_filename(), "w") as jsonfile:
        json.dump(one_point_list, jsonfile, indent=2)
        jsonfile.close()

    # save the multi-pointers back to the winners file.
    save_trivia_winners(new_list)


def top(max_results: int = MAX_RESULTS):
    """Parse the 'max_results' param as an int. Valid values are between 1 and 10, inclusive."""
    try:
        num_results = int(max_results)
        if num_results < 1 or num_results > 10:
            num_results = MAX_RESULTS
    except ValueError:
        num_results = MAX_RESULTS

    tops = load_sorted_list()
    num = min(10, num_results, len(tops))  # limit length of results
    return tops[:num]


def trivia_order_update(lines, index):
    """Increment the index of the trivia_order file."""
    lines[1] = "index=" + str(index + 1) + "\n"

    with open(TRIVIA_ORDER_FILE, "w") as trivia_order_file:
        trivia_order_file.writelines(lines)
        trivia_order_file.close()


def trivia_order_shuffle():
    """Randomize the indexes of the trivia questions and store the list in a file. This eliminates repeats."""
    lines = []
    with open(TRIVIA_FILE, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            if reader.line_num > 1 and len(line) > 1:
                lines.append(str(reader.line_num) + "\n")
        csvfile.close()

    shuffle(lines)
    lines.insert(0, "count=" + str(len(lines)) + "\n")
    lines.insert(1, "index=0\n")

    with open(TRIVIA_ORDER_FILE, "w+") as t:
        t.writelines(lines)
        t.close()


def update():
    """Download the trivia from the Internet."""
    try:
        url = "https://docs.google.com/spreadsheets/d/1sgw2WNNbE_TAILNNdmfAh-1V9ZKHSz0QhVx2SqAjFI8/gviz/tq" \
              "?tqx=out:csv&sheet=Trivia "
        urllib.request.urlretrieve(url, TRIVIA_FILE)
    except urllib.error.HTTPError:
        print("HTTPError trying to download Trivia spreadsheet")


if __name__ == '__main__':
    update()
    r = load()
    # trivia_order_shuffle()
    # remove_1point_users()
    # print(r.trivia[283])
    get_trivia_question(r)
