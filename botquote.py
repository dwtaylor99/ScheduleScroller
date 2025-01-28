import csv
import random
import secrets

import re
import urllib.error
import urllib.request

import botglitch


QUOTES_FILE = 'data/quotes.csv'
QUOTES_URL = "https://docs.google.com/spreadsheets/d/1OEaga-2Jipt8WHkW2gYsyqVdove5xbhAsmFV7IcveGA/gviz/tq?tqx=out:csv&sheet=Quotes"


def action_add(groups) -> str:
    out = 0
    try:
        if len(groups) == 2:
            a = int(groups[0])
            b = int(groups[1])
            out = a + b
    except ValueError:
        pass
    finally:
        return str(out)


def action_capital(groups) -> str:
    return str(groups).capitalize()


def action_choice(groups) -> str:
    try:
        return str(random.choice(groups.split())).strip()
    except ValueError:
        pass
    return ""


def action_div(groups) -> str:
    out = 0.0
    try:
        if len(groups) >= 2:
            a = float(groups[0])
            b = float(groups[1])
            out = a / b
    except ValueError:
        pass
    finally:
        places = 1
        if len(groups) == 3:
            places = int(groups[2])
        if places == 0:
            return str(int(out))
        s = str(round(out, places))
        f = "{:." + str(places) + "f}"
        return f.format(round(out, places))


def action_eq(groups):
    result = 0
    if len(groups) == 2:
        a = int(groups[0])
        b = int(groups[1])
        result = a == b
    return result


def action_ge(groups):
    result = 0
    if len(groups) == 2:
        a = int(groups[0])
        b = int(groups[1])
        result = a >= b
    return result


def action_glitch(groups):
    return botglitch.glitch(str(groups))


def action_gt(groups):
    result = 0
    if len(groups) == 2:
        a = int(groups[0])
        b = int(groups[1])
        result = a > b
    return result


def action_le(groups):
    result = 0
    if len(groups) == 2:
        a = int(groups[0])
        b = int(groups[1])
        result = a <= b
    return result


def action_lt(groups):
    result = 0
    if len(groups) == 2:
        a = int(groups[0])
        b = int(groups[1])
        result = a < b
    return result


def action_lower(groups) -> str:
    return str(groups).lower()


def action_mult(groups) -> str:
    out = 0
    try:
        if len(groups) == 2:
            a = int(groups[0])
            b = int(groups[1])
            out = a * b
    except ValueError:
        pass
    finally:
        return str(out)


def action_random(groups) -> str:
    # check if we have an array or a string and copy the parameters
    params = []
    if isinstance(groups, tuple):
        params.append(groups[0])
        params.append(groups[1])
    else:
        params.append(groups)

    out = 0
    try:
        if len(params) >= 2:
            imin = int(params[0])
            imax = int(params[1])
            out = secrets.randbelow(imax - imin + 1) + imin
            if len(params) == 3:
                out += int(params[2])
        elif len(params) == 1:
            imax = int(params[0])
            out = secrets.randbelow(imax) + 1
    except ValueError:
        pass
    finally:
        return str(out)


def action_swap(groups) -> str:
    return str(groups).swapcase()


def action_sub(groups) -> str:
    out = 0
    try:
        if len(groups) == 2:
            a = int(groups[0])
            b = int(groups[1])
            out = a - b
    except ValueError:
        pass
    finally:
        return str(out)


def action_title(groups) -> str:
    return str(groups).title()


def action_torgo(groups) -> str:
    return torgo_say(groups)


def action_upper(groups) -> str:
    return str(groups).upper()


def torgo_say(s):
    text = ""

    # alter name capitalization
    c_index = 0
    for i in range(0, len(s)):
        if "A" <= s[i] <= "Z" or "a" <= s[i] <= "z":
            if c_index % 2 == 1:
                text += s[i].upper()
            else:
                text += s[i].lower()
            c_index += 1
        elif s[i] == " ":
            text += s[i]
            c_index = 0
        else:
            text += s[i]

    # scan for emotes are fix them
    orig_words = s.split()
    words = text.split()
    for i, w in enumerate(words):
        if w.lower().startswith("mst3k"):
            words[i] = orig_words[i]

    text = " ".join(words)

    return text


def run_macros_old(s: str, regex: str, action):
    text = s
    macros = re.search(regex, text, flags=re.IGNORECASE)
    print("1", macros)
    macros = re.findall(regex, text, flags=re.IGNORECASE)
    if macros is not None:
        print("macros.groups()", macros)
        for group in macros:
            print("group", group)
            text = re.sub(regex, action(group), text, flags=re.IGNORECASE)

    return text


def run_macros(s: str, regex: str, action, display_name: str, movie_title: str):
    text = s
    matches = re.findall(regex, s, flags=re.IGNORECASE)
    for match in matches:
        text = text.replace("@user", display_name)
        text = text.replace("@title", movie_title)
        text = re.sub(regex, action(match), text, 1, flags=re.IGNORECASE)
    return text


def apply_params(quote: str, msg: str, display_name: str = "", movie_title: str = ""):
    # remove the leading "!" character and tokenize the quote command in 'msg'
    # "!quote arg1 arg2" -> ["quote", "arg1", arg2"]
    params = msg[1:].split()

    if len(params) > 1:
        if params[1].isnumeric():
            quote = quote.replace("@params", " ".join(params[2:]))
        else:
            quote = quote.replace("@params", " ".join(params[1:]))

    for i in reversed(range(0, len(params))):
        quote = quote.replace("@param" + str(i), params[i])

    quote = quote.replace("@user", display_name)

    matches = re.findall(r"@title\((.*?)\)", quote)
    for match in matches:
        if match == "@title":
            s = str(movie_title).title()
        else:
            s = str(match).title()
        quote = re.sub(r"@title\((.*?)\)", s, quote, 1)

    quote = quote.replace("@title", movie_title)

    # Text conversion functions
    quote = run_macros(quote, r"@upper\(\s*(.*?)\s*\)", action_upper, display_name, movie_title)
    quote = run_macros(quote, r"@lower\(\s*(.*?)\s*\)", action_lower, display_name, movie_title)
    quote = run_macros(quote, r"@capital\(\s*(.*?)\s*\)", action_capital, display_name, movie_title)
    quote = run_macros(quote, r"@glitch\(\s*(.*?)\s*\)", action_glitch, display_name, movie_title)
    quote = run_macros(quote, r"@swap\(\s*(.*?)\s*\)", action_swap, display_name, movie_title)
    quote = run_macros(quote, r"@torgo\(\s*(.*?)\s*\)", action_torgo, display_name, movie_title)

    # Random functions
    quote = run_macros(quote, r"@random\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)\s*\)", action_random, display_name, movie_title)
    quote = run_macros(quote, r"@random\(\s*(\d+)\s*,\s*(\d+)\s*\)", action_random, display_name, movie_title)
    quote = run_macros(quote, r"@random\(\s*(\d+)\s*\)", action_random, display_name, movie_title)

    # Mathematics functions
    quote = run_macros(quote, r"@mult\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_mult, display_name, movie_title)
    quote = run_macros(quote, r"@div\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*\)", action_div, display_name, movie_title)
    quote = run_macros(quote, r"@div\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_div, display_name, movie_title)
    quote = run_macros(quote, r"@add\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_add, display_name, movie_title)
    quote = run_macros(quote, r"@sub\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_sub, display_name, movie_title)

    # Conditional functions
    # quote = run_macros(quote, r"@lt\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_lt)
    # quote = run_macros(quote, r"@le\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_le)
    # quote = run_macros(quote, r"@gt\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_gt)
    # quote = run_macros(quote, r"@ge\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)", action_ge)

    # These support floating point numbers (but are not perfect):
    # quote = run_macros(quote, r"@mult\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*(\d+)\s*\)", action_mult)
    # quote = run_macros(quote, r"@mult\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)", action_mult)
    # quote = run_macros(quote, r"@div\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*(\d+)\s*\)", action_div)
    # quote = run_macros(quote, r"@div\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)", action_div)
    # quote = run_macros(quote, r"@add\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*(\d+)\s*\)", action_add)
    # quote = run_macros(quote, r"@add\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)", action_add)
    # quote = run_macros(quote, r"@sub\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*,\s*(\d+)\s*\)", action_sub)
    # quote = run_macros(quote, r"@sub\(\s*([0-9.-]+)\s*,\s*([0-9.-]+)\s*\)", action_sub)
    quote = run_macros(quote, r"@choice\((.*?)\)", action_choice, display_name, movie_title)

    return quote


def load():
    quotes = {}
    count = 0
    with open(QUOTES_FILE, "r", encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            # skip the first line of the CSV file
            if count > 0:
                trigger = line[0]

                i = 1
                alt_quotes = []
                while i < len(line) and line[i] != "":
                    # if this wasn't a blank line, add the quote(s)
                    if trigger != "":
                        alt_quotes.append(line[i])
                    i += 1

                quotes[str(trigger).lower()] = Quote(alt_quotes)

            count += 1
        csvfile.close()

    return quotes


def refresh():
    update()
    return load()


def update():
    try:
        url = QUOTES_URL
        urllib.request.urlretrieve(url, QUOTES_FILE)
    except urllib.error.HTTPError:
        print("HTTPError trying to download Quotes spreadsheet")


class Quote:
    quotes = []
    last_random_value = -1

    def __init__(self, *arg):
        self.quotes = arg[0]

    def quote(self):
        return self.quotes[0]

    def random(self):
        if len(self.quotes) > 1:
            # Choose a random quote and store the index.
            index = random.randrange(0, len(self.quotes))
            while index == self.last_random_value:
                index = random.randrange(0, len(self.quotes))
            self.last_random_value = index
        else:
            index = 0

        return self.quotes[index]

    def __repr__(self):
        return ", ".join(self.quotes)


TEST_USER = "TestUser99"
TEST_MOVIE = "Really Bad Movie of Awful"

if __name__ == '__main__':
    update()
    qs = load()
    print(apply_params(qs['nite'].quotes[2], "!nite 3 @LeftFourDave", "LeftFiveDave", "Boggy Creek"))

    # print(apply_params("random(10): @random(10)", "msg", "display_name", "movie title"))
    # print(apply_params("random(5,10): @random(5,10)", "msg", "display_name", "movie title"))
    # print(apply_params("random(100): @random(100)", "msg", "display_name", "movie title"))
    # print(apply_params("glitch: @glitch(Testing)", "msg", "display_name", "movie title"))

    # for i in range(0, 20):
    #     print(qs['sandy'].random())
    # print(torgo_say("This is an mst3kTor emote test MST3K Channel."))

    # say = "This dis-a on'simple 123 test."
    # print(torgo_say_old(say))
    # print(torgo_say(say))

    # print(apply_params("@gt(@random(10), 5)", "!test", TEST_USER, TEST_MOVIE))
    # print("@upper((ab) @upper(test) @upper(@title @user)")
    # print(apply_params("@upper((ab) @upper(test) @upper(@title @user)", "!x", TEST_USER, TEST_MOVIE))
    # print()
    # print("input    = @title: @title(@title) :: @title(abc)")
    # print("output   = " + apply_params("@title: @title(@title) :: @title(abc)", "!test", TEST_USER, TEST_MOVIE))
    # print("expected = Really Bad Movie of Awful: Really Bad Movie Of Awful :: Abc")
    # print()
    # print()
    # print("input    = [@title] ++ @title(abc)")
    # print("output   = " + apply_params("[@title] ++ @title(abc)", "", TEST_USER, TEST_MOVIE))
    # print("expected = [Really Bad Movie of Awful] ++ Abc")
    # print()
    # print()
    # print("input    = @upper(@user) @lower(@title) @lower(@user)")
    # print("output   = " + apply_params("@upper(@user) @lower(@title) @lower(@user)", "!x",  TEST_USER, TEST_MOVIE))
    # print("expected = TESTUSER99 really bad movie of awful testuser99")
    # print()
    # print()
    # print("input    = @upper(@choice(a b c))")
    # print("output   = " + apply_params("@upper(@choice(a b c))", "!x", TEST_USER, TEST_MOVIE))
    # print("expected = A|B|C")
    # print()
    # print()
    # print("input    = @lower(@torgo(why bother))")
    # print("output   = " + apply_params("@lower(@torgo(why bother))", "!x", TEST_USER, TEST_MOVIE))
    # print("expected = why bother")

    # Add support for params in quotes: @params (all params), @param0 = !command, @param1 - @param9 = arguments
    # print(apply_params("This quote @params @param0 @param1", "!test word1 word2 word3 word4 word5 6 7 8 9"))
    # print(apply_params("@param0 @param1 @param2 @param3 @param4 @param5", "!0 1 2 3 4 5"))
    # print(apply_params(
    #     "@param0 @param31 @param12 @param13 @param4 @param5 @param6 @param7 @param8 @param9 @param10 @param11",
    #     "!0 A B C D E F G H I J K L M N O P Q R S T U V W X Y Z AA BB CC DD EE FF GG HH II JJ KK LL MM NN OO OP QQ RR SS TT UU VV WW XX YY ZZ"))
    # print(apply_params("Upper/lower: @Upper(@param1 ) KILLED THAT FAT BARKEEP! Yes, it was @lower(@param1)!", "!killer SomeoneElse"))
    # print(apply_params("Title/capital: @title(@params) / @capital(@params)!", "!quote1 another test"))
    # print(apply_params("Swap/Torgo: @swap(@params) / @torgo(@params)!", "!quote2 anotHER test"))
    # print(apply_params("Random10/Random3-6: @random(10) times a lady or @random(3, 6)!", "!quote3"))
    # print(apply_params("I choose @choice(@param1 @param2 @param3).", "!quote4 item1 item2 item3"))
    # print(apply_params("I choose @choice(@param1 @param2 @param3).", "!quote5 item1 item2"))
    # print(apply_params("I choose @upper(@choice(@params)).", "!quote6 upper1 upper2 upper3 upper4"))
    # print(apply_params("Torgo says, '@torgo(Time for go to @param1 with the Master and the) @lower(@param2)'", "!quote7 bed LOWERCASENAME"))
    # print(apply_params("mst3kTorgo @torgo(@params)", "!quote8 hello, chat!"))
    # print(apply_params("mst3kCrow 'Earth vs. @title(@params)' by Crow T. Robot", "!quote9 cream of chicken soup for the soul"))
    # print(apply_params("This is a test: @upper(@params) | @lower(@params) | @torgo(@params)", "!quote10 Ship a doobblee"))
    # print(apply_params("@user: title: @title(@user), upper: @upper(@user), lower: @lower(@user)", "!quote11", "SampleUser"))

    # print(apply_params("original: @params | title: @title(@params) | capital: @capital(@params)",
    #                    "!quote A short test.",
    #                    "SampleUser88",
    #                    "Big Movie Name"))
    # print(apply_params("original: @params | upper: @upper(@params) | lower: @lower(@params) | swap: @swap(@params)",
    #                    "!quote A short test.",
    #                    "SampleUser88",
    #                    "Big Movie Name"))
    #
    # print(apply_params("@torgo(@user: @title)", "!quote", "SampleUser88", "Big Movie Name"))
    #
    # print(apply_params("@user rolled a @random(100) on a d100.", "!d100", "SampleUser1", "Big Movie Name"))
    # print(apply_params("@user rolled a @random(3,18) on a 3d6.", "!3d6", "SampleUser1", "Big Movie Name"))
    # print(apply_params("@user rolled a @random(1,6,5) on a 1d6+5.", "!1d6+5", "SampleUser1", "Big Movie Name"))
    # print(apply_params("@user rolled a @random(1,6,-1) on a 1d6-1.", "!1d6-1", "SampleUser1", "Big Movie Name"))
    # print(apply_params("random choice from the params: @choice(@params)", "!choice1 first second third", "SampleUser1", "Big Movie Name"))
    # print(apply_params("combine commands: @upper(@choice(@params))", "!choice1 first second third", "SampleUser1", "Big Movie Name"))
    # print(apply_params("the !quote is 'param0', first parameter is 'param1': @param0 @param1 @param2 @param3 @param4",
    #                    "!quote p1 p2 p3 p4", "SampleUser1", "Big Movie Name"))
    # print(apply_params("limit to 'paramsN' is the 500 char msg length!: @param0 @param12 @param11 @param10 @param9 @param8 @param7 @param6 @param5 @param4 @param3 @param2 @param1",
    #                    "!quote p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12", "SampleUser1", "Big Movie Name"))
    # print(apply_params("use 'params' to represent all parameters: @param0 @params",
    #                    "!quote p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12", "SampleUser1", "Big Movie Name"))
    #
    # print(apply_params("don't get too whacky with math: 1 + 2 = @add(1, 2)", "", "", ""))
    # print(apply_params("math is limited to integers: 13 - 2 = @sub(13, 2)", "", "", ""))
    # print(apply_params("negative numbers are supported: -11 × -9 = @mult(-11, -9)", "", "", ""))
    # print(apply_params("division results in decimals (1 by default): 10 ÷ 2 = @div(10, 2)", "", "", ""))
    # print(apply_params("optional decimal count (3): 11 ÷ 2 = @div(11, 2, 3)", "", "", ""))
    # print(apply_params("optional decimal count (6): 2 ÷ 3 = @div(2, 3, 6)", "", "", ""))
    # print(apply_params("use 0 to drop the decimal places: 11 ÷ 2 = @div(11, 2, 0)", "", "", ""))
    # print(apply_params("test: @div(11, 2, 0)", "", "", ""))
    #
