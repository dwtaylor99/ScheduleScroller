import csv
import datetime
import json
import os.path
import random
import re
import time
import urllib.error
import urllib.request

import util_text
from bottrivia import Trivia, TriviaCollection

EMOJI_GAME_ON = True
EMOJI_MINUTE = 13  # Minute of the hour to start emoji game (13 means XX:13, or minute 13 of every hour)
FILE_NAME = "data/emoji.csv"
FILE_NAME_LAST = "data/emoji_last.csv"
QUESTION_HISTORY = []
QUESTION_HISTORY_SIZE = 10
PERCENTS = [1.0, 1.0, 1.0, 1.0, 0.75, 0.9, 0.8]


def approx_equal(expected: str, s: str) -> bool:
    r = util_text.levenshtein_distance(expected, s)

    if len(expected) > len(PERCENTS):
        ratio_needed = PERCENTS[-1]
    else:
        ratio_needed = PERCENTS[len(expected) - 1]

    return r['ratio'] >= ratio_needed


def convert_time_str(time):
    return datetime.datetime.strftime(datetime.datetime.fromtimestamp(time), "%m/%d %I:%M %p")


def check_date(username: str) -> str:
    if not os.path.exists(FILE_NAME_LAST):
        with open(FILE_NAME_LAST, "w+") as jsf:
            json.dump([], jsf)
            jsf.close()

    # Check if the user played today:
    with open(FILE_NAME_LAST, "r+") as jsf:
        winners = json.load(jsf)
        jsf.close()

    last_times = []
    for o in winners:
        if o["username"] == username:
            last_times = o["times"]

    if len(last_times) < 3:
        return ""

    max_time = 0
    for t in last_times:
        if t > max_time:
            max_time = t

    # If we allow play, return "", otherwise return the date of the next time play is allowed
    rval = ""
    next_play = max_time + 86400
    if next_play >= time.time():
        rval = convert_time_str(next_play)

    return rval


def save_last(username: str):
    with open(FILE_NAME_LAST, "r+") as jsf:
        winners = json.load(jsf)
        jsf.close()

    found = False
    for w in winners:
        if w["username"] == username:
            last_times = w["times"]
            last_times.append(time.time())
            if len(last_times) > 3:
                # Just keep the last 3 times (the most recent times)
                last_times.pop(0)
                w["times"] = last_times
            else:
                w["times"] = last_times
            found = True

    if not found:
        winners.append({
            "username": username,
            "times": [time.time()]
        })

    # json.dump(winners, sys.stdout, indent=2)

    with open(FILE_NAME_LAST, "w") as jsf:
        json.dump(winners, jsf, indent=2)
        jsf.close()


def process_str(answer: str) -> str:
    ans = answer.lower()

    # Remove articles and small words like "the", "and", "a", "an".
    word_list = ["the", "and", "a", "an", "of"]
    for word in word_list:
        ans = re.sub(r'\b' + word.lower() + r'\b', '', ans)

    ans = re.sub(r'[^0-9a-zA-Z]', '', ans)

    return ans


def get() -> Trivia:
    global QUESTION_HISTORY, QUESTION_HISTORY_SIZE

    quest = None
    found = True
    while found:
        quest = random.choice(load().trivia)
        found = False
        for q in QUESTION_HISTORY:
            if quest.question == q.question:
                found = True
                break

    # def add_to_history(question: Trivia):
    QUESTION_HISTORY.append(quest)
    if len(QUESTION_HISTORY) > QUESTION_HISTORY_SIZE:
        QUESTION_HISTORY.pop(0)

    return quest


def load() -> TriviaCollection:
    """Load all emoji questions and answers into a TriviaCollection object."""
    emoji_coll = TriviaCollection()
    with open(FILE_NAME, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            if reader.line_num < 5 and len(line) > 0 and line[0].lower() == "<!doctype html>":
                break

            if reader.line_num > 0 and len(line) > 1:
                question = line.pop(0)
                answers = list(filter(None, line))  # Only add non-empty strings to the list of answers
                emoji_coll.trivia.append(Trivia(question, answers))

        csvfile.close()

    return emoji_coll


def load_as_array() -> [Trivia]:
    """Load all emoji questions and answers into an array."""
    emoji_coll = []
    with open(FILE_NAME, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            if reader.line_num < 5 and len(line) > 0 and line[0].lower() == "<!doctype html>":
                break

            if reader.line_num > 0 and len(line) > 1:
                question = line.pop(0)
                answers = list(filter(None, line))  # Only add non-empty strings to the list of answers
                emoji_coll.append(Trivia(question, answers))

        csvfile.close()

    return emoji_coll


def update():
    """Download the emoji trivia from the Internet."""
    try:
        url = "https://docs.google.com/spreadsheets/d/1sgw2WNNbE_TAILNNdmfAh-1V9ZKHSz0QhVx2SqAjFI8/gviz/tq?tqx=out:csv&sheet=Emoji "
        urllib.request.urlretrieve(url, FILE_NAME)
    except urllib.error.HTTPError:
        print("HTTPError trying to download Emoji spreadsheet")


if __name__ == '__main__':
    # update()

    username = "LeftFourDave"
    print("allow emoji:", check_date(username))
    save_last(username)

    # a = process_str("Mitchell")
    # print(a)
    # b = process_str("Mitchel")
    # print(b)
    # assert approx_equal(a, b)
