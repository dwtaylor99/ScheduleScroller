import os

ADS_FILE = "data/ads.txt"


def load_ads_time():
    lines = []
    if os.path.exists(ADS_FILE):
        with open(ADS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            f.close()
    return lines


def save_ads_time(time_int, time_formatted):
    with open(ADS_FILE, "w+", encoding="utf-8") as f:
        f.write(str(time_int) + "\n" + time_formatted)
        f.close()
