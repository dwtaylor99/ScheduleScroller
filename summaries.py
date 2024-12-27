import csv
import schedule

import random
import re
import urllib.error
import urllib.request


def load() -> dict:
    summaries = {}
    with open("data/summaries.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            if reader.line_num < 5 and len(line) > 0 and line[0].lower() == "<!doctype html>":
                break

            if reader.line_num > 1 and len(line) > 1:
                title = line[0].strip()
                summary = line[3].strip()
                if title != "":
                    summaries[schedule.process_title(title)] = summary

        csvfile.close()

    return summaries


def process_title(title: str) -> str:
    """Relies on botmovie.process_summary() but adds extra processing for titles used in Summaries."""
    t = schedule.process_title(title)
    if t == "ctwaspwoman":
        t = "ctthewaspwoman"
    return t


def get(title: str) -> str:
    """Get a summary based on the given movie title."""
    summaries = load()
    about = "Summary not found."
    if len(summaries) > 0:
        if re.match(r"\d{3,4}", title):
            movie = schedule.find_by_number(title, True)
            if movie is not None:
                title = movie.title

        t = process_title(title)
        keys = summaries.keys()
        for key in keys:
            k = process_title(key)
            if k == t or k == "the" + t or "the" + k == t:
                about = summaries[key]

    return about


def refresh() -> dict:
    """Update from the internet and reload the list of Summaries."""
    update()
    return load()


def update():
    """Download a fresh copy of the Summaries from Google Sheets."""
    try:
        url = "https://docs.google.com/spreadsheets/d/1kHmgGySs0VaP9UPf74T0rdc2batgc7k_4I027fE50-s/gviz/tq" \
              "?tqx=out:csv&sheet=Sheet1"
        urllib.request.urlretrieve(url, "data/summaries.csv")
    except urllib.error.HTTPError:
        print("HTTPError trying to download Summaries spreadsheet")