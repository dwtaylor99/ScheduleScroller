
def prepare_summary(summary: str) -> str:
    return summary.replace("--", "—")


def update_title(title, epnum):
    title_display = title
    if title.startswith("The Incredibly Strange Creatures"):
        title_display = "The Incredibly Strange Creatures Who Stopped Living…"
    if epnum != "":
        title_display += " (" + epnum + ")"
    return title_display


def wrap_text(text) -> str:
    s = ""
    last_space = 0
    for i in range(0, len(text)):
        t = text[i]

        if i % 54 == 0:
            s = s[:last_space + 1] + "\n" + s[last_space + 2:]

        if t == " ":
            last_space = i

        s += t
    return s
