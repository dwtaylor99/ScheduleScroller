from datetime import datetime
import os

ADS_FILE = "data/ads.txt"


def convert_int_to_date(time_int: int):
    return datetime.strftime(datetime.fromtimestamp(time_int), "%I:%M:%S %p")


def convert_int_to_datetime(time_int: int):
    return datetime.strftime(datetime.fromtimestamp(time_int), "%Y-%m-%d %I:%M:%S %p")


def load_ads_time():
    lines = []
    if os.path.exists(ADS_FILE):
        with open(ADS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            f.close()
    return lines


def save_ads_time(time_int: int, time_formatted: str = ""):
    if time_formatted == "":
        time_formatted = convert_int_to_date(time_int)

    with open(ADS_FILE, "w+", encoding="utf-8") as f:
        f.write(str(time_int) + "\n" + time_formatted)
        f.close()
