import csv
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta

import pytz

import summaries

NUM_RESULTS: int = 6
NEAR_RATIO: float = 0.8

US_PAC = "US/Pacific"
PAC_TZ = pytz.timezone(US_PAC)

US_EAST = "US/Eastern"
EST_TZ = pytz.timezone(US_EAST)


class Movie:
    season = 0
    episode = 0
    title = ""
    year = ""
    shorts = []
    aired = ""
    movienum = ""
    match_ratio = 1.0  # Holds the Levenshtein Distance ratio when searching for a movie [see 'find()']
    imdb_id = ""

    def __init__(self, season, episode, title, year, shorts, aired, movienum, imdb_id: str = ""):
        self.season = season
        self.episode = episode
        self.title = title
        self.year = year
        self.shorts = shorts
        self.aired = aired
        self.movienum = movienum
        self.imdb_id = imdb_id

    def desc_old(self):  # , season, episode, title, year, shorts, aired):
        if self.season > 0:
            message = "{}{:02d}, \"{}\"".format(self.season, self.episode, self.title)
        else:
            if self.episode == 1:
                message = self.title
            else:
                message = "\"{}\"".format(self.title)

        if self.year:
            message += " ({})".format(self.year)

        if len(self.shorts) == 2:
            message += " with shorts \"" + self.shorts[0] + "\" and \"" + self.shorts[1] + "\""
        elif len(self.shorts) == 1:
            if self.season == 0 and self.episode == 1:
                message += ". " + self.shorts[0]
            else:
                message += " with short \"" + self.shorts[0] + "\""

        message += "."
        if self.aired:
            message += " Aired {}.".format(self.aired)

        episode_word = "Episode "
        if self.season > 0:
            episode_word = "Experiment "

        return episode_word + message

    def desc(self):  # , season, episode, title, year, shorts, aired):
        if self.season > 0:
            message = "{}{:02d}, \"{}\"".format(self.season, self.episode, self.title)
        else:
            if self.episode == 1:
                message = self.title
            else:
                message = "\"{}\"".format(self.title)

        if self.year:
            message += " ({})".format(self.year)

        if len(self.shorts) == 2:
            message += " with shorts \"" + self.shorts[0] + "\" and \"" + self.shorts[1] + "\""
        elif len(self.shorts) == 1:
            if self.season == 0 and self.episode == 1:
                message += ". " + self.shorts[0]
            else:
                message += " with short \"" + self.shorts[0] + "\""

        message += "."
        if self.aired:
            message += " Aired {}.".format(self.aired)

        episode_word = "Episode "
        if self.season > 0:
            episode_word = "Experiment "

        return episode_word + message

    def __str__(self):
        return (
            "[season: {}, episode: {}, title: {}, year: {}, shorts: {}, aired: {}, movienum: {}, match_ratio: {}, imdb_id: {}]"
            .format(self.season, self.episode, self.title, self.year, self.shorts, self.aired, self.movienum,
                    self.match_ratio, self.imdb_id))


def handle_date_abbrs(my_date: str) -> str:
    """Make sure no bad abbreviations sneak in, or we can't parse the date"""
    my_date = my_date.replace("March ", "Mar ")
    my_date = my_date.replace("April ", "Apr ")
    my_date = my_date.replace("June ", "Jun ")
    my_date = my_date.replace("July ", "Jul ")
    my_date = my_date.replace("Sept ", "Sep ")
    my_date = my_date.replace("Tues,", "Tue,")
    my_date = my_date.replace("Weds,", "Wed,")
    my_date = my_date.replace("Thurs,", "Thu,")
    my_date = my_date.replace("Thur,", "Thu,")
    return my_date


def adjust_time(dt):
    """Allows the times read in from the CSV file to be adjusted. Useful around DST changes."""
    # dt = dt + timedelta(hours=-1)
    # dt = dt + timedelta(minutes=35)
    return dt


def find_index_of_movie_in_schedule(time_movie_list) -> int:
    """Find the index of the currently playing title in the schedule."""

    # If the first month is Dec, we may need to increase the year during the loop
    try:
        first_month_in_file = time_movie_list[0].split()[1]
    except IndexError:
        # On error, just use the current month
        first_month_in_file = datetime.strftime(datetime.now(), "%b")

    count = 0
    index = 0
    for item in time_movie_list:
        if (count % 2) == 0:
            # sample date string: "Tue, Sep 26 7:16p"
            # add a year to the date/time string
            parts = item.split(" ")
            if len(parts) > 3:
                y = datetime.now(PAC_TZ).year
                m = datetime.now(PAC_TZ).month
                # If the file starts in Nov or Dec, and now we are in Jan or Feb, increment the year
                if first_month_in_file in ["Nov", "Dec"] and parts[1] in ["Jan", "Feb"]:
                    y += 1
                if first_month_in_file in ["Nov", "Dec"] and m == 1:
                    y -= 1

                newitem = handle_date_abbrs(" ".join(parts[0:3]) + " " + str(y) + " " + parts[3] + "m")
                try:
                    d = datetime.strptime(newitem, "%a, %b %d %Y %I:%M%p").replace(tzinfo=PAC_TZ)
                    d = adjust_time(d)

                    # Format the date/time of the movie as "yyyy-MM-dd hh:mm:ss"
                    sd = datetime.strftime(d, "%Y-%m-%d %H:%M:%S")

                    # Format the current date/time (all movie times are in US/Pacific)
                    # sn = datetime.strftime(adjust_time(datetime.now(bottimezone.PAC_TZ)), "%Y-%m-%d %H:%M:%S")
                    sn = datetime.strftime(datetime.now(PAC_TZ), "%Y-%m-%d %H:%M:%S")

                    if sd >= sn:
                        index = count - 2
                        break
                except ValueError:
                    pass

        count = count + 1

    if index < 0:
        index = 0

    if index >= len(time_movie_list):
        index = len(time_movie_list) - 1

    return index


def process_title(title: str) -> str:
    """
    Process the title text by doing the following:
        * remove leading episode numbers ("318 Star Force: Fugitive Alien II" -> "Star Force: Fugitive Alien II"),
        * standardize common title variations ("Star Force: Fugitive Alien II" -> "Star Force: Fugitive Alien 2"),
        * remove symbols and spaces ("Star Force: Fugitive Alien 2" -> "StarForceFugitiveAlien2"),
        * lowercase everything ("StarForceFugitiveAlien2" -> "starforcefugitivealien2")
    The processed title is returned.
    """
    title = str(re.sub(r"^\s*\d{3,4}\s+", "", title))  # remove leading episode number
    title = str(re.sub(r"^\s*CT\d+\s+", "CT", title))  # remove leading Cinematic Titanic episode number
    title = str(re.sub(r"^\s*FC\d+\s+", "FC", title))  # remove leading Film Crew episode number

    title = title.replace("Teen-Age", "Teenage")
    title = title.replace(" (aka Operation Kid Brother)", "")
    title = title.replace(" (aka Sampo)", "")
    title = title.replace(" (aka Five the Hard Way)", "")
    title = title.replace(" (aka ZaAt)", "")
    title = title.replace(" II", "2")
    title = title.replace("Ninja I", "Ninja")
    title = title.replace("The Alien Factor", "AlienFactor")
    title = title.replace(" (of Gor)", "")
    title = title.replace("OutlawOfGor", "Outlaw")
    title = title.replace("Gaous", "Gaos")
    title = title.replace("Wonders", "Wonder")
    title = title.replace(": and the Legend Continues", "")
    title = title.replace(", and the Legend Continues", "")
    title = title.replace(" Who Stopped Living and Became Mixed-Up Zombies", "")
    # title = title.replace(" at the Memory Bank", "")
    title = title.replace(" The Fighting Eagle", "")
    title = title.replace("Chapter", "Ch")
    title = title.replace("Backlot-SanDiegoComic-ConAtHome2020MST3KPanelPanorama",
                          "Comic-Con At Home 2020: MST3K Panel")
    title = title.replace("Backlot: MST3K: Gorgo", "Backlot-MST3KTheMakingOfGorgo")
    title = title.replace("Backlot: The History of MST3K, Part 1", "Backlot-HistoryOfMST3KPt1")
    title = title.replace("Backlot: The Incredible Mr Lippert", "Backlot: Lippert")
    title = title.replace("Backlot: MST3K 25th Anniversary: The Crew", "Backlot: Crew")
    title = title.replace("Backlot: MST3K 25th Anniversary: The Characters", "Backlot: Characters")
    title = title.replace("The Giant of Marathon", "Giant of Marathon")
    title = title.replace("Viking Women and Their Voyage to the Waters of the Great Sea Serpent",
                          "VikingWomenVsSeaSerpent")
    title = title.replace("Viking Women vs the Sea Serpent", "VikingWomenVsSeaSerpent")
    title = title.replace("thesagaofthevikingwomenvsseaserpent", "VikingWomenVsSeaSerpent")
    title = title.replace("The Sword and the Dragon", "SwordAndDragon")
    title = title.replace("Manos: The Hands of Fate", "Manos")
    title = title.replace("Being from Another Planet (aka Timewalker)", "TimeWalker-BeingFromAnotherPlanet")
    title = title.replace("Being from Another Planet", "TimeWalker-BeingFromAnotherPlanet")
    title = title.replace("TimeWalker-BeingFromAnotherPlanet", "BeingFromAnotherPlanet")
    title = title.replace("RiffAlong Special (Moon Zero Two)", "Moon Zero Two Riffalong")
    title = title.replace("Cinematic Titanic: The Wasp Woman", "ctthewaspwoman")
    title = title.replace("Cinematic Titanic: The Doomsday Machine", "ctdoomsdaymachine")
    title = title.replace("Cinematic Titanic", "CT")
    title = title.replace("ctwaspwoman", "ctthewaspwoman")
    title = title.replace("The Doomsday Machine", "doomsdaymachine")
    title = title.replace("TheDoomsdayMachine", "doomsdaymachine")
    title = title.replace("Film Crew", "FC")
    title = title.replace("FilmCrew", "FC")
    title = title.replace("Guardian of the Universe", "")
    title = title.replace("MST3K Shorts: A Young Man's Fancy", "Short-YoungMansFancy")
    title = title.replace("MST3K: Shorts", "Short")
    title = title.replace("MST3K Shorts", "Short")
    title = title.replace("Delinquincy", "Delinquency")
    title = title.replace("Juvenille", "Juvenile")
    title = title.replace("Hired, Part 2", "shorthired(part2of2)")
    title = title.replace("Hired, Part 1", "shorthired(part1of2)")

    title = title.replace(":", "")
    title = title.replace("!", "")
    title = title.replace("&", "")
    title = title.replace("?", "")
    title = title.replace(",", "")
    title = title.replace(".", "")
    title = title.replace("'", "")
    title = title.replace("-", "")
    title = title.replace(" ", "")

    return title.lower()


def levenshtein_distance(str1: str, str2: str):
    """
    Calculate how similar two strings are.
    https://rosettacode.org/wiki/Levenshtein_distance#Python
    """
    m = len(str1)
    n = len(str2)
    lensum = float(m + n)
    d = []
    for i in range(m + 1):
        d.append([i])
    del d[0][0]
    for j in range(n + 1):
        d[0].append(j)
    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if str1[i - 1] == str2[j - 1]:
                d[i].insert(j, d[i - 1][j - 1])
            else:
                minimum = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + 2)
                d[i].insert(j, minimum)
    ldist = d[-1][-1]
    ratio = (lensum - ldist) / lensum
    return {'distance': ldist, 'ratio': ratio}


def near(str1: str, str2: str) -> bool:
    return levenshtein_distance(str1, str2)['ratio'] > NEAR_RATIO


def find(title: str, include_unairing: bool = False) -> Movie:
    """
    Scan the movies array for a certain title (or close to it). If a specific title is not found,
    the Levenshtein Distance is used to find the closest match.
    """
    max_ratio = 0.0
    alt_found = None
    t = process_title(title)

    movie_list = movies.copy()
    if include_unairing:
        movie_list += movies_unairing.copy()

    for movie in movie_list:
        n = process_title(movie.title)
        if n == t or "the" + n == t or n == "the" + t:
            return movie

        ratio = levenshtein_distance(n, t)['ratio']
        if ratio > max_ratio:
            max_ratio = ratio
            alt_found = movie
            alt_found.match_ratio = ratio

    # If we made it here we didn't find the movie by the title,
    # so return the best guess based on levenshtein_distance().
    return alt_found


def find_by_number(epnum: str, include_unairing: bool = False) -> Movie:
    """Scan the movies array for a specific episode number (e.g. "306"). Returns a Movie object or None."""
    movie_list = movies.copy()
    if include_unairing:
        movie_list += movies_unairing.copy()

    for movie in movie_list:
        if movie.movienum == epnum:
            return movie


IMAGE_NAMES = {
    "Cinematic Titanic: The Alien Factor": "CTL-TheAlienFactor.png",
    "Cinematic Titanic: Blood of the Vampires": "CT-BloodoftheVampires.png",
    "Cinematic Titanic: Danger on Tiki Island": "CTL-DangeronTikiIsland.png",
    "Cinematic Titanic: The Doomsday Machine": "CT-TheDoomsdayMachine.png",
    "Cinematic Titanic: East Meets Watts": "CTL-EastMeetsWatts.png",
    "Cinematic Titanic: Frankenstein's Castle of Freaks": "CT-Frankenstein_27sCastleofFreaks.png",
    "Cinematic Titanic: Legacy of Blood": "CT-LegacyofBlood.png",
    "Cinematic Titanic: The Oozing Skull": "CT-TheOozingSkull.png",
    "Cinematic Titanic: Rattlers": "CTRattlersTitle.png",
    "Cinematic Titanic: Santa Claus Conquers the Martians": "CT-SantaClausConquerstheMartians.png",
    "Cinematic Titanic: War of the Insects": "CTWarInsects.png",
    "Cinematic Titanic: The Wasp Woman": "CT-TheWaspWoman.png",

    "RiffTrax: Abraxas": "RT-Abraxas.png",
    "RiffTrax: Breaker! Breaker!": "RT-BreakerBreaker.png",
    "RiffTrax: Hillbillys in a Haunted House": "RT-HillbillysHauntedHouse.png",
    "RiffTrax: Icebreaker": "RT-Icebreaker.png",
    "RiffTrax: Jack the Giant Killer": "RT-JackGiantKiller.png",
    "RiffTrax: Miami Connection (Live)": "RT-MiamiConnectionLive.png",
    "RiffTrax: Prisoners of the Lost Universe": "RT-PrisonersLost.png",
    "RiffTrax: Samurai Cop": "RT-SamuraiCop.png",
    "RiffTrax: Wonder Women": "RT-WonderWomen.png",
    "RiffTrax: Zindy, the Swamp Boy": "RT-ZindySwampBoy.png",

    "Film Crew: Hollywood After Dark": "FC-Hollywoodafterdark.png",
    "Film Crew: Killers from Space": "FC-Killersfromspace.png",
    "Film Crew: Wild Women of Wongo": "FC-Wildwomenofwongo.png",
    "Film Crew: The Giant of Marathon": "FC-GiantOfMarathon.png",

    "Backlot: MST3K 25th Anniversary: The Characters": "backlot.png",
    "Backlot: MST3K 25th Anniversary: The Crew": "backlot.png",
    "Backlot: Characters": "backlot.png",
    "Backlot: Crew": "backlot.png",
    "Backlot: MST3K 25th Anniversary: Big Changes": "backlot.png",
    "Backlot: MST3K Turkey Day!": "backlot.png",
    "Backlot: MST3K: Outlaw Of Gor Interview": "backlot.png",
    "Backlot: Outlaw of Gor": "backlot.png",
    "Backlot: Santa Versus Satan": "backlot.png",
    "Backlot: Gorgo": "backlot.png",
    "Backlot: MST3K: The Incredible Mr. Lippert": "backlot.png",
    "Backlot: Lippert": "backlot.png",
    "Backlot: Return to Eden Prairie: 25 Years of Mystery Science Theater 3000": "backlot.png",
    "Backlot: MST3K Yule Log": "yule_log.png",

    "Backlot: History": "backlot.png",
    "Backlot: History 2": "backlot.png",
    "Backlot: History 3": "backlot.png",

    "MST3K Shorts: The Home Economics Story": "home_economics.png",
    "MST3K Shorts: Mr B Natural (Max & Kinga version)": "mrb_natural_maxkinga.png",
    "MST3K Shorts: Mr B Natural": "mrb_natural.png",
    "MST3K Shorts: Posture Pals": "posture_pals.png",
    "MST3K Shorts: Appreciating Our Parents": "appreciating_parents.png",
    "MST3K Shorts: Johnny at the Fair": "johnny_at_fair.png",
    "MST3K Shorts: Circus on Ice": "circus_on_ice.png",

    "MST3K Shorts: What to Do on a Date": "what_to_do_date.png",
    "MST3K Shorts: Body Care and Grooming": "body_care_grooming.png",
    "MST3K Shorts: Is This Love?": "is_this_love.png",
    "MST3K Shorts: Cheating": "cheating.png",
    "MST3K Shorts: What About Juvenile Delinquency?": "juvenile_deliquency.png",
    "MST3K Shorts: Last Clear Chance": "last_clear_chance.png",
    "MST3K Shorts: Design for Dreaming": "design_for_dreaming.png",
    "MST3K Shorts: Uncle Jim's Dairy Farm": "uncle_jims_dairy_farm.png",
    "MST3K Shorts: A Day at the Fair": "day_at_fair.png",
    "MST3K Shorts: Why Study the Industrial Arts?": "industrial_arts.png",
    "MST3K Shorts: A Young Man's Fancy": "young_mans_fancy.png",
    "MST3K Shorts: Are You Ready for Marriage?": "ready_for_marriage.png",
    "MST3K Shorts: Once Upon a Honeymoon": "once_honeymoon.png",
    "MST3K Shorts: The Chicken of Tomorrow": "chicken_of_tomorrow.png",
    "MST3K Shorts: A Case of Spring Fever": "case_of_spring_fever.png",

    "MST3K Shorts: Speech: Platform Posture and Appearance": "speech_posture_appearance.png",
    "MST3K Shorts: Money Talks!": "money_talks.png",
    "MST3K Shorts: Progress Island USA": "progress_island.png",

    "MST3K Shorts: Alphabet Antics": "alphabet_antics.png",
    "MST3K Shorts: Aquatic Wizards": "aquatic_wizards.png",
    "MST3K Shorts: Assignment Venezuela": "assignment_venezuela.png",
    "MST3K Shorts: Catching Trouble": "catching_trouble.png",
    "MST3K Shorts: Century 21 Calling...": "century21_calling.png",
    "MST3K Shorts: A Date with Your Family": "date_with_family.png",
    "MST3K Shorts: The Days of Our Years": "days_of_our_years.png",
    "MST3K Shorts: Here Comes the Circus": "here_comes_circus.png",
    "MST3K Shorts: Hired! (Part 1 of 2)": "hired.png",
    "MST3K Shorts: Hired! (Part 2 of 2)": "hired.png",
    "MST3K Shorts: Junior Rodeo Daredevils": "junior_rodeo_daredevils.png",
    "MST3K Shorts: Keeping Clean and Neat": "keeping_clean_neat.png",
    "MST3K Shorts: Out of This World": "out_of_world.png",
    "MST3K Shorts: The Selling Wizard": "selling_wizard.png",
    "MST3K Shorts: Speech: Using Your Voice": "speech_using_voice.png",
    "MST3K Shorts: The Sport Parade: Snow Thrills": "snow_thrills.png",
    "MST3K Shorts: The Truck Farmer": "truck_farmer.png",
    "MST3K Shorts: X Marks the Spot": "x_marks_spot.png",

    "MST3K Shorts: The Phantom Creeps - Chapter 1: The Menacing Power": "phantom_creeps.png",
    "MST3K Shorts: The Phantom Creeps - Chapter 2: Death Stalks the Highways": "phantom_creeps.png",
    "MST3K Shorts: The Phantom Creeps - Chapter 3: Crashing Towers": "phantom_creeps.png",

    "MST3K Shorts: Undersea Kingdom - Chapter 1: Beneath The Ocean Floor": "undersea_kingdom.png",
    "MST3K Shorts: Undersea Kingdom - Chapter 2: The Undersea City": "undersea_kingdom.png",

    "MST3K Shorts: Radar Men from the Moon - Chapter 1: Moon Rocket": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 2: Molten Terror": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 3: Bridge of Death": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 4: Flight to Destruction": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 5: Murder Car": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 6: Hills of Death": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 7: Camouflaged Destruction": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 8: The Enemy Planet": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon - Chapter 9: Battle in the Stratosphere": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 1": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 2": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 3": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 4": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 5": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 6": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 7": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 8": "radar_men_moon.png",
    "MST3K Shorts: Radar Men from the Moon 9": "radar_men_moon.png",
    "Radar Men from the Moon": "radar_men_moon.png",

    "MST3K Shorts: Pipeline to the Clouds": "pipeline_to_clouds.png",
    "MST3K Shorts: Let's Make a Meal in 20 Minutes!": "meal_in_20_minutes.png",
    "MST3K Shorts: Court Case": "court_case.png",
    "MST3K Shorts: Sleep for Health": "sleep_for_health.png",
    "MST3K Shorts: The Wonder of Reproduction": "wonder_of_reproduction.png",
    "MST3K Shorts: Cavalcade": "cavalcade.png",
    "MST3K Shorts: Balance Beam for Girls": "balance_beam.png",
    "MST3K Shorts: Season 13's 13 Shorts": "s13_gizmo.png",
    "MST3K Shorts: Bicycling Visual Skills": "bicycle_visual_skills.png",
    "MST3K Shorts: The Bicycle Driver": "bicycle_driver.png",
    "MST3K Shorts: Let's Keep Food Safe to Eat": "keep_food_safe.png",
    "MST3K Shorts: Better Breakfast USA": "better_breakfasts.png",
    "MST3K Shorts: Doing Things for Ourselves in School": "ourselves_in_school.png",

    "Moon Zero Two Riffalong": "moon_zero_two_riffalong.png",
    "ComicCon Panel": "ComicCon.png",
    "Poopie!": "Poopie1.png",
    "Poopie! II": "Poopie2.png",
    "Poopie Parade of Values": "PoopieParadeOfValues.png",

    "MST3K Little Gold Statue Preview 1995": "little_gold_statue.png",
    "MST3K Summer Blockbuster Review 1997": "blockbuster_review_1997.png",
    "MST3K Summer Blockbuster Review 1998": "blockbuster_review_1998.png",
    "MST3K Academy of Robots' Choice Awards Special": "academy_robots_choice.png",

    "Godzilla vs. Megalon (Host Segments)": "212.png",
    "Godzilla vs. the Sea Monster (Host Segments)": "213.png",
    "The Amazing Colossal Man (Host Segments)": "309.png",
    "It Conquered the World (Host Segments)": "311.png",
    "Space Travelers (Host Segments)": "401.png",
    "Fire Maidens of Outer Space (Host Segments)": "416.png",
    "Attack of the The Eye Creatures (Host Segments)": "418.png",
    "Teen-Age Crime Wave (Host Segments)": "522.png",
    "12 to the Moon (Host Segments)": "524.png",
    "Girls Town (Host Segments)": "601.png",
    "Colossus and the Headhunters (Host Segments)": "605.png",
    "San Francisco International (Host Segments)": "614.png",
    "Kitten with a Whip (Host Segments)": "615.png",
    "This Island Earth (Host Segments)": "700.png",
    "The Incredible Melting Man (Host Segments)": "704.png",
    "Revenge of the Creature (Host Segments)": "801.png",
    "The Leech Woman (Host Segments)": "802.png",
    "The Mole People (Host Segments)": "803.png",
    "The Deadly Mantis (Host Segments)": "804.png",
    "The Thing That Couldn't Die (Host Segments)": "805.png",
    "Terror from the Year 5000 (Host Segments)": "807.png",
    "I Was a Teenage Werewolf (Host Segments)": "809.png",
    "Riding with Death (Host Segments)": "814.png",
    "Agent for H.A.R.M. (Host Segments)": "815.png",
    "The Projected Man (Host Segments)": "901.png",
    "The Deadly Bees (Host Segments)": "905.png",
    "The Space Children (Host Segments)": "906.png",
    "Soultaker (Host Segments)": "1001.png",
    "Squirm (Host Segments)": "1012.png",
    "Diabolik (Host Segments)": "1013.png",

    "MST Hour 301 Cave Dwellers": "MST_Hour.png",
    "MST Hour 302 Gamera": "MST_Hour.png",
    "MST Hour 303 Pod People": "MST_Hour.png",
    "MST Hour 306 Time of the Apes": "MST_Hour.png",
    "MST Hour 307 Daddy-O": "MST_Hour.png",
    "MST Hour 309 The Amazing Colossal Man": "MST_Hour.png",
    "MST Hour 310 Fugitive Alien": "MST_Hour.png",
    "MST Hour 311 It Conquered the World": "MST_Hour.png",
    "MST Hour 312 Gamera vs Guiron": "MST_Hour.png",
    "MST Hour 313 Earth vs the Spider": "MST_Hour.png",
    "MST Hour 317 Viking Women vs the Sea Serpent": "MST_Hour.png",
    "MST Hour 319 War of the Colossal Beast": "MST_Hour.png",
    "MST Hour 320 The Unearthly": "MST_Hour.png",
    "MST Hour 321 Santa Claus Conquers the Martians": "MST_Hour.png",
    "MST Hour 401 Space Travelers": "MST_Hour.png",
    "MST Hour 402 The Giant Gila Monster": "MST_Hour.png",
    "MST Hour 404 Teenagers from Outer Space": "MST_Hour.png",
    "MST Hour 408 Hercules Unchained": "MST_Hour.png",
    "MST Hour 410 Hercules Against the Moon Men": "MST_Hour.png",
    "MST Hour 411 The Magic Sword": "MST_Hour.png",
    "MST Hour 414 Tormented": "MST_Hour.png",
    "MST Hour 415 The Beatniks": "MST_Hour.png",
    "MST Hour 417 Crash of Moons": "MST_Hour.png",
    "MST Hour 418 Attack of the The Eye Creatures": "MST_Hour.png",
    "MST Hour 420 The Human Duplicators": "MST_Hour.png",
    "MST Hour 422 The Day the Earth Froze": "MST_Hour.png",
    "MST Hour 424 Manos the Hands of Fate": "MST_Hour.png",
    "MST Hour 504 Secret Agent Super Dragon": "MST_Hour.png",
    "MST Hour 505 The Magic Voyage of Sinbad": "MST_Hour.png",
    "MST Hour 507 I Accuse My Parents": "MST_Hour.png"
}
"""
    "Reptilicus": "",
    "Cry Wilderness": "",
    "The Time Travelers": "",
    "Avalanche": "",
    "The Beast of Hollow Mountain": "",
    "Starcrash": "",
    "The Land That Time Forgot": "",
    "The Loves of Hercules": "",
    "Yongary - Monster from the Deep": "",
    "Wizards of the Lost Kingdom": "",
    "Wizards of the Lost Kingdom II": "",
    "Carnival Magic": "",
    "The Christmas that Almost Wasn't": "",
    "At the Earth's Core": "",
    "Mac and Me": "",
    "Atlantic Rim": "",
    "Lords of the Deep": "",
    "The Day Time Ended": "",
    "Killer Fish": "",
    "Ator, the Fighting Eagle": ""
"""


def get_image_name(title: str) -> str:
    if title in IMAGE_NAMES.keys():
        return IMAGE_NAMES[title]
    else:
        return "mst3k.png"


def print_schedule(movies_times: [str], index: int, num_results: int, tz_desc: str):
    """Format the next <num_results> movies on the schedule into a printable string for a specific timezone."""

    time_zn = PAC_TZ

    # num_results = 20 #  botutils.constrain(num_results, 1, 500)

    # first_month_in_file = movies_times[0].split()[1]
    try:
        first_month_in_file = movies_times[0].split()[1]
    except IndexError:
        # On error, just use the current month
        first_month_in_file = datetime.strftime(datetime.now(), "%b")

    schedule = []

    # Just loop until we run out of entries to read.
    # We'll allow the IndexError and build the schedule from the rows up to that point.
    s = ""
    try:
        for i in range(index, index + (num_results * 2), 2):
            if movies_times[i] != "":
                y = datetime.now(PAC_TZ).year
                m = datetime.now(PAC_TZ).month
                if first_month_in_file in ["Nov", "Dec"] and movies_times[i].split()[1] in ["Jan", "Feb"]:
                    y += 1
                if first_month_in_file in ["Nov", "Dec"] and m == 1:
                    y -= 1

                # Add an "m" to make "am" or "pm" then add the current year
                d = handle_date_abbrs(movies_times[i]) + "m " + str(y)
                # Convert the date string to a date object
                dt = datetime.strptime(d, "%a, %b %d %I:%M%p %Y")
                # Apply any time adjustments
                dt = adjust_time(dt)
                # Interpret the date and time as being from the US/Pacific timezone.
                dt = PAC_TZ.localize(dt)
                dz = dt.astimezone(time_zn)
                # Convert date/time to a string and remove leading 0 from time, "07:00 PM" -> "7:00 PM"
                # t = datetime.strftime(dz, "%I:%M%p").lstrip("0").replace("AM", "a").replace("PM", "p")
                t = datetime.strftime(dz, "%I:%M %p").lstrip("0")
                t = datetime.strftime(dz, "%a ") + t

                dz2 = dt.astimezone(EST_TZ)
                t2 = datetime.strftime(dz2, "%I:%M %p").lstrip("0")
                t2 = datetime.strftime(dz2, "%a ") + t2

                m = movies_times[i + 1]  # 'i' will hold the index of the date/time, so 'i+1' will be the movie name
                mv = find(m)  # find the Movie object based on the title in the array
                if mv is not None:
                    m = mv.title

                ep = ""
                if mv.season > 0 and mv.episode > 0:
                    ep = "{}{:02d}".format(mv.season, mv.episode)

                if i == index:
                    s = s + " " + t + " " + m
                    if ep != "":
                        s += " (" + ep + ")"
                else:
                    s = s + " | " + t + " " + m
                    if ep != "":
                        s += " (" + ep + ")"

                if ep != "":
                    obj = {
                        'title': mv.title,
                        'year': mv.year,
                        'epnum': ep,
                        'datetime': d,
                        'datetime_est': datetime.strftime(dz2, "%a, %b %d %I:%M%p %Y"),
                        'time': t,
                        'time_est': t2,
                        'about': summaries.get(mv.title),
                        'image': ep + ".png"
                    }
                else:
                    obj = {
                        'title': mv.title,
                        'year': mv.year,
                        'epnum': '',
                        'datetime': d,
                        'datetime_est': datetime.strftime(dz2, "%a, %b %d %I:%M%p %Y"),
                        'time': t,
                        'time_est': t2,
                        'about': summaries.get(mv.title),
                        'image': get_image_name(mv.title)
                    }
                schedule.append(obj)
    except IndexError:
        pass

    # tz = datetime.strftime(datetime.now(time_zn), "[%Z/%z]")
    # return "Playing now " + tz + s
    return schedule


def get_schedule(tz_desc: str = US_PAC, num: int = -1):
    """
    Performs a few steps to load a printable movie schedule for a specific timezone, if provided.
    First, the schedule is loaded from file (the file is NOT downloaded before loading).
    Next, the index of the current movie is found using the date/time of the schedule.
    Then the details the current movie are loaded and the global 'current_movie' value is set.
    Finally, a printable version of the movie schedule is built and returned as a str.
    """
    global current_movie
    schedule = load()
    movie_index = find_index_of_movie_in_schedule(schedule)
    current_movie = find(schedule[movie_index + 1])
    if num == -1:
        num = NUM_RESULTS
    return print_schedule(schedule, movie_index, num, tz_desc)


def load() -> [str]:
    """
    Loads the csv file as a flat array like [Date/Time, Title, Date/Time, Title, ...]
    Date/Time - formatted like "Fri, Nov 11 9:53p" or "%a, %b %d %I:%M%p" (add a trailing "m")
    Title - formatted like "1002 Girl in Gold Boots" or "CT11 War of the Insects"
    """
    csvmovies = []
    with open("data/times.csv", "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for line in reader:
            if reader.line_num > 1:
                csvmovies = csvmovies + line[0:2]
        csvfile.close()

    return csvmovies


def refresh() -> [str]:
    """Download the CSV and load it."""
    update()
    return load()


def update() -> None:
    try:
        url = "https://docs.google.com/spreadsheets/d/1fNpYG3BTl06V-X-bVdwKW7QF4xrDQj1-5V-3oP9q5RM/gviz/tq?tqx=out" \
              ":csv&sheet=Times"
        urllib.request.urlretrieve(url, 'data/times.csv')
    except urllib.error.HTTPError:
        print("HTTPError trying to download Movie Times spreadsheet")


movies_unairing = [
    Movie(2, 12, "Godzilla vs. Megalon", "1973", [], "Jan 19, 1991", "212", "0070122"),
    Movie(2, 13, "Godzilla vs. the Sea Monster", "1966", [], "Feb 2, 1991", "213", "0060464"),
    Movie(3, 9, "The Amazing Colossal Man", "1957", [], "Aug 3, 1991", "309", "0050118"),
    Movie(3, 11, "It Conquered the World", "1956", ["Snow Thrills"], "Aug 24, 1991", "311", "0049370"),
    Movie(4, 1, "Space Travelers", "1969", [], "Jun 6, 1992", "401", "0064639"),
    Movie(4, 16, "Fire Maidens of Outer Space", "1956", [], "Nov 26, 1992", "416", "0046977"),
    Movie(4, 18, "Attack of the The Eye Creatures", "1967", [], "Dec 5, 1992", "418", "0059161"),
    Movie(5, 22, "Teen-Age Crime Wave", "1955", [], "Jan 15, 1994", "522", "0048701"),
    Movie(5, 24, "12 to the Moon", "1960", ["Design for Dreaming"], "Feb 5, 1994", "524", "0054415"),
    Movie(6, 1, "Girls Town", "1959", [], "Jul 16, 1994", "601", "0052850"),
    Movie(6, 5, "Colossus and the Headhunters", "1963", [], "Aug 20, 1994", "605", "0056207"),
    Movie(6, 14, "San Francisco International", "1970", [], "Nov 19, 1994", "614", "0065343"),
    Movie(6, 15, "Kitten with a Whip", "1964", [], "Nov 23, 1994", "615", "0058267"),
    Movie(0, 0, "This Island Earth", "1955", [], "Apr 19, 1996", "M01", "0047577"),
    Movie(7, 4, "The Incredible Melting Man", "1977", [], "Feb 24, 1996", "704", "0076191"),
    Movie(8, 1, "Revenge of the Creature", "1955", [], "Feb 1, 1997", "801", "0048554"),
    Movie(8, 2, "The Leech Woman", "1960", [], "Feb 8, 1997", "802", "0054020"),
    Movie(8, 3, "The Mole People", "1956", [], "Feb 15, 1997", "803", "0049516"),
    Movie(8, 4, "The Deadly Mantis", "1957", [], "Feb 22, 1997", "804", "0050294"),
    Movie(8, 5, "The Thing That Couldn't Die", "1958", [], "Mar 1, 1997", "805", "0052289"),
    Movie(8, 7, "Terror from the Year 5000", "1958", [], "Mar 15, 1997", "807", "0052286"),
    Movie(8, 9, "I Was a Teenage Werewolf", "1957", [], "Apr 19, 1997", "809", "0050530"),
    Movie(8, 14, "Riding with Death", "1976", [], "Jul 19, 1997", "814", "0075142"),
    Movie(8, 15, "Agent for H.A.R.M.", "1966", [], "Aug 2, 1997", "815", "0060074"),
    Movie(9, 1, "The Projected Man", "1966", [], "Mar 14, 1998", "901", "0062159"),
    Movie(9, 5, "The Deadly Bees", "1966", [], "May 9, 1998", "905", "0061557"),
    Movie(9, 6, "The Space Children", "1958", ["Century 21 Calling"], "Jun 13, 1998", "906", "0052227"),
    Movie(10, 1, "Soultaker", "1990", [], "Apr 11, 1999", "1001", "0100665"),
    Movie(10, 12, "Squirm", "1976", ["A Case of Spring Fever"], "Aug 1, 1999", "1012", "0075261"),
    Movie(10, 13, "Diabolik", "1968", [], "Aug 8, 1999", "1013", "0062861"),
    Movie(11, 1, "Reptilicus", "1961", [], "Apr 14, 2017", "1101", "0056405"),
    Movie(11, 2, "Cry Wilderness", "1987", [], "Apr 14, 2017", "1102", "0126848"),
    Movie(11, 3, "The Time Travelers", "1964", [], "Apr 14, 2017", "1103", "0058659"),
    Movie(11, 4, "Avalanche", "1978", [], "Apr 14, 2017", "1104", "0077189"),
    Movie(11, 5, "The Beast of Hollow Mountain", "1956", [], "Apr 14, 2017", "1105", "0048992"),
    Movie(11, 6, "Starcrash", "1978", [], "Apr 14, 2017", "1106", "0079946"),
    Movie(11, 7, "The Land That Time Forgot", "1975", [], "Apr 14, 2017", "1107", "0073260"),
    Movie(11, 8, "The Loves of Hercules", "1960", [], "Apr 14, 2017", "1108", "0053598"),
    Movie(11, 9, "Yongary - Monster from the Deep", "1967", [], "", "1109", "0061549"),
    Movie(11, 10, "Wizards of the Lost Kingdom", "1985", [], "Apr 14, 2017", "1110", "0090333"),
    Movie(11, 11, "Wizards of the Lost Kingdom II", "1989", [], "Apr 14, 2017", "1111", "0090334"),
    Movie(11, 12, "Carnival Magic", "1981", [], "Apr 14, 2017", "1112", "0207374"),
    Movie(11, 13, "The Christmas that Almost Wasn't", "1966", [], "Apr 14, 2017", "1113", "0059032"),
    Movie(11, 14, "At the Earth's Core", "1976", [], "Apr 14, 2017", "1114", "0074157"),
    Movie(12, 1, "Mac and Me", "1988", [], "Nov 22, 2018", "1201", "0095560"),
    Movie(12, 2, "Atlantic Rim", "2013", [], "Nov 22, 2018", "1202", "2740710"),
    Movie(12, 3, "Lords of the Deep", "1980", [], "Nov 22, 2018", "1203", "0097781"),
    Movie(12, 4, "The Day Time Ended", "1980", [], "Nov 22, 2018", "1204", "0080596"),
    Movie(12, 5, "Killer Fish", "1979", [], "Nov 22, 2018", "1205", "0077800"),
    Movie(12, 6, "Ator, the Fighting Eagle", "1982", [], "Nov 22, 2018", "1206", "0085183")
]

# Special episodes that no longer air:
# Movie(0, 0, "#MakeMoreMST3K Livestream", "2021", [], "", "MMML1"),
# Movie(0, 0, "#MakeMoreMST3K Untamed Youth", "2021", [], "", "MMML2"),
# Movie(0, 0, "#MakeMoreMST3K Quest of the Delta Knights", "2021", [], "", "MMML3"),
# Movie(0, 0, "#MakeMoreMST3K Gamera vs Guiron", "2021", [], "", "MMML4"),
# Movie(0, 0, "#MakeMoreMST3K Jackbox Game Night!", "2021", [], "", "MMML5"),
# Movie(0, 0, "#MakeMoreMST3K Werewolf", "2021", [], "", "MMML6"),
# Movie(0, 0, "#MakeMoreMST3K Zombie Nightmare", "2021", [], "", "MMML7"),
# Movie(0, 0, "#MakeMoreMST3K Final Countdown Telethon", "2021", [], "", "MMML8"),
# Movie(0, 0, "Turkey Day Marathon 2016", "2016", [], "", "TD1"),
# Movie(0, 0, "Turkey Day Marathon 2017", "2017", [], "", "TD2"),
# Movie(0, 0, "Comic-Con At Home 2020: MST3K Panel", "2020", [], "", "CCH"),
# Movie(0, 0, "ComicCon Panel", "2020", [], "", "CCH"),
# Movie(0, 0, "MST3K Summer Film Series #1 - 817 Horror of Party Beach", "", [], "", ""),
# Movie(0, 0, "MST3K Summer Film Series #2 - 414 Tormented", "", [], "", ""),
# Movie(0, 0, "MST3K Summer Film Series #3 - 1005 Blood Waters Of Dr. Z", "", [], "", ""),
# Movie(0, 0, "MST3K Summer Film Series #4 - 204 Catalina Caper", "", [], "", ""),
# Movie(0, 0, "MST3K Summer Film Series #5 - 608 Code Name: Diamond Head", "", [], "", ""),

movies = [
    Movie(0, 0, "ComicCon Panel", "2020", [], "", "CCH", ""),

    Movie(0, 0, "Cinematic Titanic: The Alien Factor", "1978", [], "", "CT9", "0075656"),
    Movie(0, 0, "Cinematic Titanic: Blood of the Vampires", "1958", [], "", "CT7", "0051422"),
    Movie(0, 0, "Cinematic Titanic: Danger on Tiki Island", "1968", [], "", "CT10", "0062758"),
    Movie(0, 0, "Cinematic Titanic: The Doomsday Machine", "1972", [], "", "CT2", "0061592"),
    Movie(0, 0, "Cinematic Titanic: East Meets Watts", "1974", [], "", "CT8", "0132933"),
    Movie(0, 0, "Cinematic Titanic: Frankenstein's Castle of Freaks", "1974", [], "", "CT6", "0069851"),
    Movie(0, 0, "Cinematic Titanic: Legacy of Blood", "1978", [], "", "CT4", "0066845"),
    Movie(0, 0, "Cinematic Titanic: The Oozing Skull", "1971", [], "", "CT1", "0068313"),
    Movie(0, 0, "Cinematic Titanic: Rattlers", "1976", [], "", "CT12", "0073609"),
    Movie(0, 0, "Cinematic Titanic: Santa Claus Conquers the Martians", "1964", [], "", "CT5", "0058548"),
    Movie(0, 0, "Cinematic Titanic: War of the Insects", "1968", [], "", "CT11", "0063195"),
    Movie(0, 0, "Cinematic Titanic: The Wasp Woman", "1959", [], "", "CT3", "0054462"),

    Movie(0, 0, "RiffTrax: Abraxas", "1990", [], "", "RT1", "0101264"),
    Movie(0, 0, "RiffTrax: Breaker! Breaker!", "1977", [], "", "RT2", "0075783"),
    Movie(0, 0, "RiffTrax: Hillbillys in a Haunted House", "1967", [], "", "RT3", "0061765"),
    Movie(0, 0, "RiffTrax: Icebreaker", "2000", [], "", "RT4", "0179861"),
    Movie(0, 0, "RiffTrax: Jack the Giant Killer", "1962", [], "", "RT5", "0056112"),
    Movie(0, 0, "RiffTrax: Miami Connection (Live)", "1987", [], "", "RT6", "0092549"),
    Movie(0, 0, "RiffTrax: Prisoners of the Lost Universe", "1983", [], "", "RT7", "0086141"),
    Movie(0, 0, "RiffTrax: Samurai Cop", "1991", [], "", "RT8", "0130236"),
    Movie(0, 0, "RiffTrax: Wonder Women", "1973", [], "", "RT9", "0070926"),
    Movie(0, 0, "RiffTrax: Zindy, the Swamp Boy", "1973", [], "", "RT10", "0324659"),

    Movie(0, 0, "Film Crew: Hollywood After Dark", "1969", [], "Jul 7, 2007", "FC1", "0055612"),
    Movie(0, 0, "Film Crew: Killers from Space", "1954", [], "Aug 7, 2007", "FC2", "0047149"),
    Movie(0, 0, "Film Crew: Wild Women of Wongo", "1959", [], "Sep 11, 2007", "FC3", "0052394"),
    Movie(0, 0, "Film Crew: The Giant of Marathon", "1959", [], "Oct 9, 2007", "FC4", "0052604"),

    Movie(0, 0, "Backlot: MST3K 25th Anniversary: The Characters", "", [], "", "BL1"),
    Movie(0, 0, "Backlot: MST3K 25th Anniversary: The Crew", "", [], "", "BL2"),
    Movie(0, 0, "Backlot: Characters", "", [], "", "BL3"),
    Movie(0, 0, "Backlot: Crew", "", [], "", "BL4"),
    Movie(0, 0, "Backlot: MST3K 25th Anniversary: Big Changes", "", [], "", "BL5"),
    Movie(0, 0, "Backlot: MST3K Turkey Day!", "", [], "", "BL6"),
    Movie(0, 0, "Backlot: MST3K: Outlaw Of Gor Interview", "", [], "", "BL7"),
    Movie(0, 0, "Backlot: Outlaw of Gor", "", [], "", "BL8"),
    Movie(0, 0, "Backlot: Santa Versus Satan", "", [], "", "BL9"),
    Movie(0, 0, "Backlot: Gorgo", "", [], "", "BL10"),
    Movie(0, 0, "Backlot: MST3K: The Incredible Mr. Lippert", "", [], "", "BL11"),
    Movie(0, 0, "Backlot: Lippert", "", [], "", "BL12"),
    Movie(0, 0, "Backlot: Return to Eden Prairie: 25 Years of Mystery Science Theater 3000", "2013", [], "", "EP1"),
    Movie(0, 0, "Backlot: MST3K Yule Log", "2017", [], "", "YL1"),

    Movie(0, 1, "MST3K Shorts: X Marks the Spot", "1944", ['Originally from Episode 210, "King Dinosaur"'], "", "SHORT-210-XMTS", "0280209"),
    Movie(0, 1, "MST3K Shorts: Alphabet Antics", "1951", ['Originally from Episode 307, "Daddy-O"'], "", "SHORT-307-ALPHAB", "2535904"),
    Movie(0, 1, "MST3K Shorts: Speech: Using Your Voice", "1950", ['Originally from Episode 313, "Earth vs the Spider"'], "", "SHORT-313-SUYV", "0292248"),
    Movie(0, 1, "MST3K Shorts: Aquatic Wizards", "1955", ['Originally from Episode 315, "Teenage Cave Man"  '], "", "SHORT-315-AQUAWIZ", "0279655"),
    Movie(0, 1, "MST3K Shorts: Catching Trouble", "1936", ['Originally from Episode 315, "Teenage Cave Man"'], "", "SHORT-315-CATCHTR", "0248722"),
    Movie(0, 1, "MST3K Shorts: The Home Economics Story", "1951", ['Originally from Episode 317, "Viking Women and the Sea Serpent"'], "", "SHORT-317-HOMEEC", "0308375"),
    Movie(0, 1, "MST3K Shorts: Mr B Natural (Max & Kinga version)", "1956", ['Originally from Episode 319, "War of the Colossal Beast"'], "", "SHORT-319-MRBMK", "0135558"),
    Movie(0, 1, "MST3K Shorts: Mr B Natural", "1956", ['Originally from Episode 319, "War of the Colossal Beast"'], "", "SHORT-319-MRB", "0135558"),
    Movie(0, 1, "MST3K Shorts: Posture Pals", "1952", ['Originally from Episode 320, "The Unearthly"'], "", "SHORT-320-POSTUREP", "0292194"),
    Movie(0, 1, "MST3K Shorts: Appreciating Our Parents", "1950", ['Originally from Episode 320, "The Unearthly"'], "", "SHORT-320-AOPARENTS", "0257411"),
    Movie(0, 1, "MST3K Shorts: Johnny at the Fair", "1947", ['Originally from Episode 419, "The Rebel Set"'], "", "SHORT-419-JATF", "0276240"),
    Movie(0, 1, "MST3K Shorts: Circus on Ice", "1954", ['Originally from Episode 421, "Monster A Go-Go"'], "", "SHORT-421-CIRCUSICE", "0289122"),
    Movie(0, 1, "MST3K Shorts: Here Comes the Circus", "1946", ['Originally from Episode 422, "The Day the Earth Froze"'], "", "SHORT-422-HCTCIRCUS", "0279858"),
    Movie(0, 1, "MST3K Shorts: What to Do on a Date", "1951", ['Originally from Episode 503, "Swamp Diamonds"'], "", "SHORT-503-WTDOAD", "0258312"),
    Movie(0, 1, "MST3K Shorts: The Truck Farmer", "1954", ['Originally from Episode 507, "I Accuse My Parents"'], "", "SHORT-507-TRUCFARM", "0292292"),
    Movie(0, 1, "MST3K Shorts: Body Care and Grooming", "1947", ['Originally from Episode 510, "The Painted Hills"'],"", "SHORT-510-BCAGROOM", "0308056"),
    Movie(0, 1, "MST3K Shorts: Is This Love?", "1957", ['Originally from Episode 514, "Teen-Age Strangler"'], "", "SHORT-514-ISLOVE", "0292024"),
    Movie(0, 1, "MST3K Shorts: Cheating", "1952", ['Originally from Episode 515, "The Wild Wild World of Batwoman"'], "", "SHORT-515-CHEATING", "0291806"),
    Movie(0, 1, "MST3K Shorts: What About Juvenile Delinquency?", "1955", ['Originally from Episode 518, "The Atomic Brain"'], "", "SHORT-518-WAJUVD", "0260549"),
    Movie(0, 1, "MST3K Shorts: Last Clear Chance", "1959", ['Originally from Episode 520, "Radar Secret Service"'], "", "SHORT-520-LCCHANCE", "0246747"),
    Movie(0, 1, "MST3K Shorts: Design for Dreaming", "1956", ['Originally from Episode 524, "12 to the Moon"'], "", "SHORT-524-DESIGNFD", "0279772"),
    Movie(0, 1, "MST3K Shorts: Uncle Jim's Dairy Farm", "1963", ['Originally from Episode 607, "Bloodlust!"'], "", "SHORT-608-UJDFARM", "0283100"),
    Movie(0, 1, "MST3K Shorts: A Day at the Fair", "1947", ['Originally from Episode 608, "Code Name: Diamond Head"'], "", "SHORT-608-ADATF", "0289147"),
    Movie(0, 1, "MST3K Shorts: Why Study the Industrial Arts?", "1956", ['Originally from Episode 609, "The Skydivers"'], "", "SHORT-609-WSTIA", "0260571"),
    Movie(0, 1, "MST3K Shorts: A Young Man's Fancy", "1952", ['Originally from Episode 610, "The Violent Years"'], "", "SHORT-610-AYMF", "0280218"),
    Movie(0, 1, "MST3K Shorts: Are You Ready for Marriage?", "1950", ['Originally from Episode 616, "Racket Girls"'], "", "SHORT-616-AYRFM", "0257412"),
    Movie(0, 1, "MST3K Shorts: Speech: Platform Posture and Appearance", "1949", ['Originally from Episode 619, "Red Zone Cuba"'], "", "SHORT-619-SPPAA", "0292247"),
    Movie(0, 1, "MST3K Shorts: Money Talks!", "1951", ['Originally from Episode 621, "The Beast of Yucca Flats"'], "", "SHORT-621-MONEYTALKS", "0292119"),
    Movie(0, 1, "MST3K Shorts: Progress Island USA", "1973", ['Originally from Episode 621, "The Beast of Yucca Flats"'], "", "SHORT-621-PROGISLD", "0308766"),
    Movie(0, 1, "MST3K Shorts: Once Upon a Honeymoon", "1956", ['Originally from Episode 701, "Night of the Blood Beast"'], "", "SHORT-701-OUAH", "0279997"),
    Movie(0, 1, "MST3K Shorts: The Chicken of Tomorrow", "1948", ['Originally from Episode 702, "The Brute Man"'], "", "SHORT-702-TCOT", "0291809"),
    Movie(0, 1, "MST3K Shorts: A Case of Spring Fever", "1940", ['Originally from Episode 1012, "Squirm"'], "", "SHORT-1012-ACOSF", "0282404"),
    Movie(0, 1, "MST3K Shorts: The Phantom Creeps - Chapter 1: The Menacing Power", "1939", ['Originally from Episode 203, "Jungle Goddess"'], "", "SHORT-203-PC1", "0031796"),
    Movie(0, 1, "MST3K Shorts: The Phantom Creeps - Chapter 2: Death Stalks the Highways", "1939", ['Originally from Episode 205, "Rocket Attack USA"'], "", "SHORT-205-PC2", "0031796"),
    Movie(0, 1, "MST3K Shorts: The Phantom Creeps - Chapter 3: Crashing Towers", "1939", ['Originally from Episode 206, "Ring of Terror"'], "", "SHORT-206-PC3", "0031796"),
    Movie(0, 1, "MST3K Shorts: The Sport Parade: Snow Thrills", "1945", ['Originally from Episode 311, "It Conquers the World"'], "", "SHORT-311-TSPST", "2594194"),
    Movie(0, 1, "MST3K Shorts: Undersea Kingdom - Chapter 1: Beneath The Ocean Floor", "1936", ['Originally from Episode 406, "Attack of the Giant Leeches"'], "", "SHORT-406-UK1", "0028444"),
    Movie(0, 1, "MST3K Shorts: Undersea Kingdom - Chapter 2: The Undersea City", "1936", ['Originally from Episode 409, "Indestructible Man"'], "", "SHORT-409-UK2", "0028444"),
    Movie(0, 1, "MST3K Shorts: Junior Rodeo Daredevils", "1949", ['Originally from Episode 407, "The Killer Shrews"'], "", "SHORT-407-JRRODEOD", "0289250"),
    Movie(0, 1, "MST3K Shorts: Hired! (Part 1 of 2)", "1940", ['Originally from Episode 423, "Bride of the Monster"'], "", "SHORT-423-HIRED1", "0282562"),
    Movie(0, 1, "MST3K Shorts: Hired! (Part 2 of 2)", "1940", ['Originally from Episode 424, "Manos: The Hands of Fate"'], "", "SHORT-424-HIRED2", "0282562"),
    Movie(0, 1, "MST3K Shorts: A Date with Your Family", "1950", ['Originally from Episode 602, "Invasion USA"'], "", "SHORT-602-ADWYF", "0276048"),
    Movie(0, 1, "MST3K Shorts: The Selling Wizard", "1954", ['Originally from Episode 603, "The Dead Talk Back"'], "", "SHORT-603-SELWIZ", "0282953"),
    Movie(0, 1, "MST3K Shorts: Keeping Clean and Neat", "1956", ['Originally from Episode 613, "The Sinister Urge"'], "", "SHORT-613-KCAN", "0289257"),
    Movie(0, 1, "MST3K Shorts: Out of This World", "1954", ['Originally from Episode 618, "High School Big Shot"'], "", "SHORT-618-OOTW", "0282822"),
    Movie(0, 1, "MST3K Shorts: The Days of Our Years", "1955", ['Originally from Episode 623, "The Amazing Transparent Man"'], "", "SHORT-623-TDOOY", "0276051"),
    Movie(0, 1, "MST3K Shorts: Century 21 Calling...", "1962", ['Originally from Episode 906, "The Space Children."'], "", "SHORT-906-C21CALL", "0246480"),
    Movie(0, 1, "MST3K Shorts: Assignment Venezuela", "1956", ['Originally from Unreleased MST3K CD-ROM'], "", "SHORT-ASSNVEN", "0297747"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 1: Moon Rocket", "1952", ['Originally from Episode 102, "The Robot vs the Aztec Mummy"'], "", "SHORT-102-RM1", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 2: Molten Terror", "1952", ['Originally from Episode 103, "The Mad Monster"'], "", "SHORT-103-RM2", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 3: Bridge of Death", "1952", ['Originally from Episode 105, "The Corpse Vanishes"'], "", "SHORT-105-RM3", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 4: Flight to Destruction", "1952", ['Originally from Episode 107, "Robot Monster"'], "", "SHORT-107-RM4", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 5: Murder Car", "1952", ['Originally from Episode 107, "Robot Monster"'], "", "SHORT-107-RM5", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 6: Hills of Death", "1952", ['Originally from Episode 108, "The Slime People"'], "", "SHORT-108-RM6", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 7: Camouflaged Destruction", "1952", ['Originally from Episode 109, "Project Moon Base"'], "", "SHORT-109-RM7", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 8: The Enemy Planet", "1952", ['Originally from Episode 109, "Project Moon Base"'], "", "SHORT-109-RM8", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon - Chapter 9: Battle in the Stratosphere", "1952", ['Originally from Episode 110, "Robot Holocaust"'], "", "SHORT-110-RM9", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 1", "1952", ['Originally from Episode 102, "The Robot vs the Aztec Mummy"'], "", "SHORT-102-RM1", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 2", "1952", ['Originally from Episode 103, "The Mad Monster"'], "", "SHORT-103-RM2", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 3", "1952", ['Originally from Episode 105, "The Corpse Vanishes"'], "", "SHORT-105-RM3", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 4", "1952", ['Originally from Episode 107, "Robot Monster"'], "", "SHORT-107-RM4", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 5", "1952", ['Originally from Episode 107, "Robot Monster"'], "", "SHORT-107-RM5", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 6", "1952", ['Originally from Episode 108, "The Slime People"'], "", "SHORT-108-RM6", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 7", "1952", ['Originally from Episode 109, "Project Moon Base"'], "", "SHORT-109-RM7", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 8", "1952", ['Originally from Episode 109, "Project Moon Base"'], "", "SHORT-109-RM8", "0045064"),
    Movie(0, 1, "MST3K Shorts: Radar Men from the Moon 9", "1952", ['Originally from Episode 110, "Robot Holocaust"'], "", "SHORT-110-RM9", "0045064"),

    Movie(0, 0, "Moon Zero Two Riffalong", "1969", [], "May 3, 2020", "", "0064691"),
    Movie(0, 0, "Radar Men from the Moon", "1952", [], "", ""),

    # Host Segments Only
    # Movie(0, 0, "Rocketship X-M (Host Segments)", "1950", [], "Sep 22, 1990", "201", "0042897"),
    Movie(0, 0, "Godzilla vs. Megalon (Host Segments)", "1973", [], "Jan 19, 1991", "212", "0070122"),
    Movie(0, 0, "Godzilla vs. the Sea Monster (Host Segments)", "1966", [], "Feb 2, 1991", "213", "0060464"),
    Movie(0, 0, "The Amazing Colossal Man (Host Segments)", "1957", [], "Aug 3, 1991", "309", "0050118"),
    Movie(0, 0, "It Conquered the World (Host Segments)", "1956", [], "Aug 24, 1991", "311", "0049370"),
    Movie(0, 0, "Space Travelers (Host Segments)", "1969", [], "Jun 6, 1992", "401", "0064639"),
    Movie(0, 0, "Fire Maidens of Outer Space (Host Segments)", "1956", [], "Nov 26, 1992", "416", "0046977"),
    Movie(0, 0, "Attack of the The Eye Creatures (Host Segments)", "1967", [], "Dec 5, 1992", "418", "0059161"),
    Movie(0, 0, "Teen-Age Crime Wave (Host Segments)", "1955", [], "Jan 15, 1994", "522", "0048701"),
    Movie(0, 0, "12 to the Moon (Host Segments)", "1960", [], "Feb 5, 1994", "524", "0054415"),
    Movie(0, 0, "Girls Town (Host Segments)", "1959", [], "Jul 16, 1994", "601", "0052850"),
    Movie(0, 0, "Colossus and the Headhunters (Host Segments)", "1963", [], "Aug 20, 1994", "605", "0056207"),
    Movie(0, 0, "San Francisco International (Host Segments)", "1970", [], "Nov 19, 1994", "614", "0065343"),
    Movie(0, 0, "Kitten with a Whip (Host Segments)", "1964", [], "Nov 23, 1994", "615", "0058267"),
    Movie(0, 0, "This Island Earth (Host Segments)", "1955", [], "Apr 19, 1996", "M01", "0047577"),
    Movie(7, 4, "The Incredible Melting Man (Host Segments)", "1977", [], "Feb 24, 1996", "704", "0076191"),
    Movie(8, 10, "Revenge of the Creature (Host Segments)", "1955", [], "Feb 1, 1997", "801", "0048554"),
    Movie(8, 2, "The Leech Woman (Host Segments)", "1960", [], "Feb 8, 1997", "802", "0054020"),
    Movie(8, 3, "The Mole People (Host Segments)", "1956", [], "Feb 15, 1997", "803", "0049516"),
    Movie(8, 4, "The Deadly Mantis (Host Segments)", "1957", [], "Feb 22, 1997", "804", "0050294"),
    Movie(8, 5, "The Thing That Couldn't Die (Host Segments)", "1958", [], "Mar 1, 1997", "805", "0052289"),
    Movie(8, 7, "Terror from the Year 5000 (Host Segments)", "1958", [], "Mar 15, 1997", "807", "0052286"),
    Movie(8, 9, "I Was a Teenage Werewolf (Host Segments)", "1957", [], "Apr 19, 1997", "809", "0050530"),
    Movie(8, 14, "Riding with Death (Host Segments)", "1976", [], "Jul 19, 1997", "814", "0075142"),
    Movie(8, 15, "Agent for H.A.R.M. (Host Segments)", "1966", [], "Aug 2, 1997", "815", "0060074"),
    Movie(9, 1, "The Projected Man (Host Segments)", "1966", [], "Mar 14, 1998", "901", "0062159"),
    Movie(9, 5, "The Deadly Bees (Host Segments)", "1966", [], "May 9, 1998", "905", "0061557"),
    Movie(9, 6, "The Space Children (Host Segments)", "1958", ["Century 21 Calling"], "Jun 13, 1998", "906", "0052227"),
    # Movie(9, 10, "The Final Sacrifice (Host Segments)", "1990", [], "Jul 25, 1998", "910", "0131550"),
    Movie(10, 1, "Soultaker (Host Segments)", "1990", [], "Apr 11, 1999", "1001", "0100665"),
    Movie(10, 12, "Squirm (Host Segments)", "1976", [], "Aug 1, 1999", "1012", "0075261"),
    Movie(10, 13, "Diabolik (Host Segments)", "1968", [], "Aug 8, 1999", "1013", "0062861"),

    Movie(1, 1, "The Crawling Eye", "1958", [], "Nov 18, 1989", "101", "0052320"),
    Movie(1, 2, "The Robot vs. The Aztec Mummy", "1959", ["Radar Men from the Moon, Part 1: 'Moon Rocket'"],
          "Nov 25, 1989", "102", "0050717"),
    Movie(1, 3, "The Mad Monster", "1942", ["Radar Men from the Moon, Part 2: 'Molten Terror'"], "Dec 2, 1989", "103",
          "0035009"),
    Movie(1, 4, "Women of the Prehistoric Planet", "1966", [], "Feb 20, 1990", "104", "0061203"),
    Movie(1, 5, "The Corpse Vanishes", "1942", ["Radar Men from the Moon, Part 3: 'Bridge of Death'"], "Dec 9, 1989",
          "105", "0034613"),
    Movie(1, 6, "The Crawling Hand", "1963", [], "Dec 16, 1989", "106", "0056961"),
    Movie(1, 7, "Robot Monster", "1953",
          ["Radar Men from the Moon, Part 4: 'Flight to Destruction'", "Part 5: 'Murder Car'"], "Dec 23, 1989", "107",
          "0046248"),
    Movie(1, 8, "The Slime People", "1964", ["Radar Men from the Moon, Part 6: 'Hills of Death'"], "Dec 30, 1989",
          "108", "0056499"),
    Movie(1, 9, "Project Moon Base", "1953", ["Radar Men from the Moon, Part 7: 'Camouflaged Destruction'", "Part 8: 'The Enemy Planet'"], "Jan 6, 1990", "109", "0046213"),
    Movie(1, 10, "Robot Holocaust", "1986", ["Radar Men from the Moon, Part 9: 'Battle in the Stratosphere' (Partial)"],
          "Jan 13, 1990", "110", "0093872"),
    Movie(1, 11, "Moon Zero Two", "1969", [], "Jan 20, 1990", "111", "0064691"),
    Movie(1, 12, "Untamed Youth", "1957", [], "Jan 27, 1990", "112", "0051139"),
    Movie(1, 13, "The Black Scorpion", "1957", [], "Feb 3, 1990", "113", "0050197"),

    Movie(2, 1, "Rocketship X-M", "1950", [], "Sep 22, 1990", "201", "0042897"),
    Movie(2, 2, "The Side Hackers", "1969", [], "Sep 29, 1990", "202", "0061671"),
    Movie(2, 3, "Jungle Goddess", "1948", ["The Phantom Creeps, Chapter 1: 'The Menacing Power'"], "Oct 6, 1990",
          "203", "0040500"),
    Movie(2, 4, "Catalina Caper", "1967", [], "Oct 13, 1990", "204", "0061456"),
    Movie(2, 5, "Rocket Attack U.S.A.", "1961", ["The Phantom Creeps, Chapter 2: 'Death Stalks the Highway'"],
          "Oct 27, 1990", "205", "0055380"),
    Movie(2, 6, "Ring of Terror", "1962", ["The Phantom Creeps, Chapter 3: 'Crashing Timbers'"], "Nov 3, 1990", "206",
          "0056415"),
    Movie(2, 7, "Wild Rebels", "1967", [], "Nov 17, 1990", "207", "0062493"),
    Movie(2, 8, "Lost Continent", "1951", [], "Nov 24, 1990", "208", "0043757"),
    Movie(2, 9, "The Hellcats", "1968", [], "Dec 8, 1990", "209", "0061759"),
    Movie(2, 10, "King Dinosaur", "1955", ["X Marks the Spot"], "Dec 22, 1990", "210", "0048256"),
    Movie(2, 11, "First Spaceship on Venus", "1960", [], "Dec 29, 1990", "211", "0053250"),
    # Movie(2, 12, "Godzilla vs. Megalon", "1973", [], "Jan 19, 1991", "212", "0070122"),
    # Movie(2, 13, "Godzilla vs. the Sea Monster", "1966", [], "Feb 2, 1991", "213", "0060464"),
    Movie(3, 1, "Cave Dwellers", "1984", [], "Jun 1, 1991", "301", "0086972"),
    Movie(3, 2, "Gamera", "1965", [], "Jun 8, 1991", "302", "0059080"),
    Movie(3, 3, "Pod People", "1983", [], "Jun 15, 1991", "303", "0086026"),
    Movie(3, 4, "Gamera vs Barugon", "1966", [], "Jun 22, 1991", "304", "0060446"),
    Movie(3, 5, "Stranded in Space", "1973", [], "Jun 29, 1991", "305", "0070742"),
    Movie(3, 6, "Time of the Apes", "1974", [], "Jul 13, 1991", "306", "0094153"),
    Movie(3, 7, "Daddy-O", "1959", ["Alphabet Antics"], "Jul 20, 1991", "307", "0052719"),
    Movie(3, 8, "Gamera vs Gaos", "1967", [], "Jul 27, 1991", "308", "0061695"),
    # Movie(3, 9, "The Amazing Colossal Man", "1957", [], "Aug 3, 1991", "309", "0050118"),
    Movie(3, 10, "Fugitive Alien", "1978", [], "Aug 17, 1991", "310", "0128224"),
    # Movie(3, 11, "It Conquered the World", "1956", ["Snow Thrills"], "Aug 24, 1991", "311", "0049370"),
    Movie(3, 12, "Gamera vs Guiron", "1969", [], "Sep 7, 1991", "312", "0064360"),
    Movie(3, 13, "Earth vs the Spider", "1958", ["Speech: Using Your Voice"], "Sep 14, 1991", "313", "0051570"),
    Movie(3, 14, "Mighty Jack", "1968", [], "Sep 21, 1991", "314", "0063300"),
    Movie(3, 15, "Teenage Cave Man", "1958", ["Aquatic Wizards", "Catching Trouble"], "Nov 9, 1991", "315", "0052279"),
    Movie(3, 16, "Gamera vs Zigra", "1971", [], "Oct 19, 1991", "316", "0067123"),
    Movie(3, 17, "Viking Women vs the Sea Serpent", "1957", ["The Home Economics Story"], "Oct 26, 1991", "317",
          "0052156"),
    Movie(3, 18, "Star Force: Fugitive Alien II", "1978", [], "Nov 16, 1991", "318", "0131028"),
    Movie(3, 19, "War of the Colossal Beast", "1958", ["Mr. B Natural"], "Nov 30, 1991", "319", "0052378"),
    Movie(3, 20, "The Unearthly", "1957", ["Posture Pals", "Appreciating Our Parents"], "Dec 14, 1991", "320", "0051134"),
    Movie(3, 21, "Santa Claus Conquers the Martians", "1964", [], "Dec 21, 1991", "321", "0058548"),
    Movie(3, 22, "Master Ninja I", "1984", [], "Jan 11, 1992", "322", "0086756"),
    Movie(3, 23, "The Castle of Fu Manchu", "1968", [], "Jan 18, 1992", "323", "0064338"),
    Movie(3, 24, "Master Ninja II", "1984", [], "Jan 25, 1992", "324", "0086756"),
    # Movie(4, 1, "Space Travelers", "1969", [], "Jun 6, 1992", "401", "0064639"),
    Movie(4, 2, "The Giant Gila Monster", "1959", [], "Jun 13, 1992", "402", "0052846"),
    Movie(4, 3, "City Limits", "1985", [], "Jun 20, 1992", "403", "0088925"),
    Movie(4, 4, "Teenagers from Outer Space", "1959", [], "Jun 27, 1992", "404", "0053337"),
    Movie(4, 5, "Being from Another Planet", "1982", [], "Jul 4, 1992", "405", "0084796"),
    Movie(4, 6, "Attack of the Giant Leeches", "1959", ["Undersea Kingdom, Part 1: 'Beneath the Ocean Floor'"], "Jul 18, 1992", "406", "0053611"),
    Movie(4, 7, "The Killer Shrews", "1959", ["Junior Rodeo Daredevils"], "Jul 25, 1992", "407", "0052969"),
    Movie(4, 8, "Hercules Unchained", "1959", [], "Aug 1, 1992", "408", "0052782"),
    Movie(4, 9, "Indestructible Man", "1956", ["Undersea Kingdom, Part 2: 'The Undersea City'"], "Aug 15, 1992", "409", "0049363"),
    Movie(4, 10, "Hercules Against the Moon Men", "1964", [], "Aug 22, 1992", "410", "0058311"),
    Movie(4, 11, "The Magic Sword", "1962", [], "Aug 29, 1992", "411", "0056211"),
    Movie(4, 12, "Hercules and the Captive Women", "1961", [], "Sep 12, 1992", "412", "0054851"),
    Movie(4, 13, "Manhunt in Space", "1954", ["General Hospital, Part 1 of 3"], "Sep 19, 1992", "413", "0047211"),
    Movie(4, 14, "Tormented", "1960", [], "Sep 26, 1992", "414", "0054393"),
    Movie(4, 15, "The Beatniks", "1960", ["General Hospital, Part 2 of 3"], "Nov 25, 1992", "415", "0053640"),
    # Movie(4, 16, "Fire Maidens of Outer Space", "1956", [], "Nov 26, 1992", "416", "0046977"),
    Movie(4, 17, "Crash of Moons", "1954", ["General Hospital, Part 3 of 3"], "Nov 28, 1992", "417", "0045655"),
    # Movie(4, 18, "Attack of the Eye Creatures", "1965", [], "Dec 5, 1992", "418", "0059161"),
    Movie(4, 19, "The Rebel Set", "1959", ["Johnny at the Fair"], "Dec 12, 1992", "419", "0053213"),
    Movie(4, 20, "The Human Duplicators", "1965", [], "Dec 26, 1992", "420", "0059290"),
    Movie(4, 21, "Monster A-Go Go", "1965", ["Circus on Ice"], "Jan 9, 1993", "421", "0059464"),
    Movie(4, 22, "The Day the Earth Froze", "1959", ["Here Comes the Circus"], "Jan 16, 1993", "422", "0053240"),
    Movie(4, 23, "Bride of the Monster", "1955", ["Hired!, Part 1 of 2"], "Jan 23, 1993", "423", "0047898"),
    Movie(4, 24, "Manos: The Hands of Fate", "1966", ["Hired!, Part 2 of 2"], "Jan 30, 1993", "424", "0060666"),
    Movie(5, 1, "Warrior of the Lost World", "1983", [], "Jul 24, 1993", "501", "0088380"),
    Movie(5, 2, "Hercules", "1958", [], "Jul 17, 1993", "502", "0050381"),
    Movie(5, 3, "Swamp Diamonds", "1956", ["What to Do on a Date"], "Jul 31, 1993", "503", "0048682"),
    Movie(5, 4, "Secret Agent Super Dragon", "1966", [], "Aug 7, 1993", "504", "0060956"),
    Movie(5, 5, "The Magic Voyage of Sinbad", "1952", [], "Aug 14, 1993", "505", "0046264"),
    Movie(5, 6, "Eegah", "1962", [], "Aug 28, 1993", "506", "0055946"),
    Movie(5, 7, "I Accuse My Parents", "1944", ["The Truck Farmer"], "Sep 4, 1993", "507", "0037798"),
    Movie(5, 8, "Operation Double 007", "1967", [], "Sep 11, 1993", "508", "0062078"),
    Movie(5, 9, "The Girl in Lovers Lane", "1960", [], "Sep 18, 1993", "509", "0052849"),
    Movie(5, 10, "The Painted Hills", "1951", ["Body Care and Grooming"], "Sep 26, 1993", "510", "0043895"),
    Movie(5, 11, "Gunslinger", "1956", [], "Oct 9, 1993", "511", "0049287"),
    Movie(5, 12, "Mitchell", "1975", [], "Oct 23, 1993", "512", "0073396"),
    Movie(5, 13, "The Brain That Wouldn't Die", "1959", [], "Oct 30, 1993", "513", "0052646"),
    Movie(5, 14, "Teen-Age Strangler", "1964", ["Is This Love?"], "Nov 7, 1993", "514", "0059786"),
    Movie(5, 15, "The Wild Wild World of Batwoman", "1966", ["Cheating"], "Nov 13, 1993", "515", "0061191"),
    Movie(5, 16, "Alien from L.A.", "1987", [], "Nov 20, 1993", "516", "0092532"),
    Movie(5, 17, "Beginning of the End", "1957", [], "Nov 25, 1993", "517", "0050177"),
    Movie(5, 18, "The Atomic Brain", "1963", ["What about Juvenile Delinquency?"], "Dec 4, 1993", "518", "0057859"),
    Movie(5, 19, "Outlaw (of Gor)", "1989", [], "Dec 11, 1993", "519", "0098048"),
    Movie(5, 20, "Radar Secret Service", "1950", ["Last Clear Chance"], "Dec 18, 1993", "520", "0042874"),
    Movie(5, 21, "Santa Claus", "1959", [], "Dec 24, 1993", "521", "0053241"),
    # Movie(5, 22, "Teen-Age Crime Wave", "1955", [], "Jan 15, 1994", "522", "0048701"),
    Movie(5, 23, "Village of the Giants", "1965", [], "Jan 22, 1994", "523", "0059878"),
    # Movie(5, 24, "12 to the Moon", "1965", ["Design for Dreaming"], "Feb 5, 1994", "524", "0054415"),
    # Movie(6, 1, "Girls Town", "1959", [], "Jul 16, 1994", "601", "0052850"),
    Movie(6, 2, "Invasion USA", "1952", ["A Date with Your Family"], "Jul 23, 1994", "602", "0044750"),
    Movie(6, 3, "The Dead Talk Back", "1957", ["The Selling Wizard"], "Jul 30, 1994", "603", "0106682"),
    Movie(6, 4, "Zombie Nightmare", "1986", [], "Nov 24, 1994", "604", "0092297"),
    # Movie(6, 5, "Colossus and the Headhunters", "1960", [], "Aug 20, 1994", "605", "0056207"),
    Movie(6, 6, "The Creeping Terror", "1964", [], "Sep 17, 1994", "606", "0057970"),
    Movie(6, 7, "Bloodlust!", "1961", ["Uncle Jim's Dairy Farm"], "Sep 3, 1994", "607", "0054691"),
    Movie(6, 8, "Code Name: Diamond Head", "1977", ["A Day at the Fair"], "Oct 1, 1994", "608", "0075862"),
    Movie(6, 9, "The Skydivers", "1963", ["Why Study Industrial Arts?"], "Aug 27, 1994", "609", "0057507"),
    # Young Man's Fancy IMDb: 0280218
    Movie(6, 10, "The Violent Years", "1956", ["Young Man's Fancy"], "Oct 8, 1994", "610", "0049922"),
    Movie(6, 11, "Last of the Wild Horses", "1948", [], "Oct 15, 1994", "611", "0040530"),
    Movie(6, 12, "The Starfighters", "1964", [], "Oct 29, 1994", "612", "0058615"),
    Movie(6, 13, "The Sinister Urge", "1960", ["Keeping Clean and Neat"], "Nov 5, 1994", "613", "0055452"),
    # Movie(6, 14, "San Francisco International", "1970", [], "Nov 19, 1994", "614", "0066326"),
    # Movie(6, 15, "Kitten with a Whip", "1964", [], "Nov 23, 1994", "615", "0058267"),
    Movie(6, 16, "Racket Girls", "1951", ["Are You Ready for Marriage?"], "Nov 26, 1994", "616", "0043954"),
    Movie(6, 17, "The Sword and the Dragon", "1956", [], "Dec 3, 1994", "617", "0049358"),
    Movie(6, 18, "High School Big Shot", "1959", ["Out of This World"], "Dec 10, 1994", "618", "0052891"),
    Movie(6, 19, "Red Zone Cuba", "1966", ["Speech: Platform, Posture, and Appearance"], "Dec 17, 1994", "619", "0060753"),
    Movie(6, 20, "Danger!! Death Ray", "1967", [], "Jan 7, 1995", "620", "0062035"),
    Movie(6, 21, "The Beast of Yucca Flats", "1961", ["Money Talks!", "Progress Island USA"], "Jan 21, 1995", "621", "0054673"),
    Movie(6, 22, "Angels Revenge", "1979", [], "Mar 11, 1995", "622", "0078778"),
    Movie(6, 23, "The Amazing Transparent Man", "1960", ["The Days of Our Years"], "Mar 18, 1995", "623", "0053593"),
    Movie(6, 24, "Samson vs. the Vampire Women", "1961", [], "Mar 25, 1995", "624", "0055408"),

    Movie(7, 1, "Night of the Blood Beast", "1958", ["Once Upon a Honeymoon"], "Feb 3, 1996", "701", "0051993"),
    Movie(7, 2, "The Brute Man", "1946", ["The Chicken of Tomorrow"], "Feb 10, 1996", "702", "0038387"),
    Movie(7, 3, "Deathstalker and the Warriors from Hell", "1988", [], "Feb 17, 1996", "703", "0097174"),
    # Movie(7, 4, "The Incredible Melting Man", "1977", [], "Feb 24, 1996", "704", "0076191"),
    Movie(7, 5, "Escape 2000", "1983", [], "Mar 2, 1996", "705", "0089104"),
    Movie(7, 6, "Laserblast", "1978", [], "May 18, 1996", "706", "0077834"),

    # Movie(8, 1, "Revenge of the Creature", "1955", [], "Feb 1, 1997", "801", "0048554"),
    # Movie(8, 2, "The Leech Woman", "1960", [], "Feb 8, 1997", "802", "0054020"),
    # Movie(8, 3, "The Mole People", "1956", [], "Feb 15, 1997", "803", "0049516"),
    # Movie(8, 4, "The Deadly Mantis", "1957", [], "Feb 22, 1997", "804", "0050294"),
    # Movie(8, 5, "The Thing That Couldn't Die", "1958", [], "Mar 1, 1997", "805", "0052289"),
    Movie(8, 6, "The Undead", "1956", [], "Mar 8, 1997", "806", "0051128"),
    # Movie(8, 7, "Terror from the Year 5000", "1958", [], "Mar 15, 1997", "807", "0052286"),
    Movie(8, 8, "The She-Creature", "1956", [], "Apr 5, 1997", "808", "0050957"),
    # Movie(8, 9, "I Was a Teenage Werewolf", "1957", [], "Apr 19, 1997", "809", "0050530"),
    Movie(8, 10, "The Giant Spider Invasion", "1975", [], "May 31, 1997", "810", "0073043"),
    Movie(8, 11, "Parts: The Clonus Horror", "1979", [], "Jun 7, 1997", "811", "0078062"),
    Movie(8, 12, "The Incredibly Strange Creatures Who Stopped Living and Became Mixed-Up Zombies!!?", "1964", [],
          "Jun 14, 1997", "812", "0057181"),
    Movie(8, 13, "Jack Frost", "1966", [], "Jul 12, 1997", "813", "0058374"),
    # Movie(8, 14, "Riding with Death", "1976", [], "Jul 19, 1997", "814", "0075142"),
    # Movie(8, 15, "Agent for H.A.R.M.", "1966", [], "Aug 2, 1997", "815", "0060074"),
    Movie(8, 16, "Prince of Space", "1959", [], "Aug 16, 1997", "816", "0053464"),
    Movie(8, 17, "The Horror of Party Beach", "1964", [], "Sep 6, 1997", "817", "0058208"),
    Movie(8, 18, "Devil Doll", "1963", [], "Oct 4, 1997", "818", "0058007"),
    Movie(8, 19, "Invasion of the Neptune Men", "1961", [], "Oct 11, 1997", "819", "0055562"),
    Movie(8, 20, "Space Mutiny", "1988", [], "Nov 8, 1997", "820", "0096149"),
    Movie(8, 21, "Time Chasers", "1994", [], "Nov 22, 1997", "821", "0145529"),
    Movie(8, 22, "Overdrawn at the Memory Bank", "1983", [], "Dec 6, 1997", "822", "0089759"),

    # Movie(9, 1, "The Projected Man", "1966", [], "Mar 14, 1998", "901", "0062159"),
    Movie(9, 2, "The Phantom Planet", "1961", [], "Mar 21, 1998", "902", "0055294"),
    Movie(9, 3, "The Pumaman", "1980", [], "Apr 4, 1998", "903", "0081693"),
    Movie(9, 4, "Werewolf", "1996", [], "Apr 18, 1998", "904", "0118137"),
    # Movie(9, 5, "The Deadly Bees", "1967", [], "May 9, 1998", "905", "0061557"),
    # Movie(9, 6, "The Space Children", "1958", ["Century 21 Calling"], "Jun 13, 1998", "906", "0052227"),
    Movie(9, 7, "Hobgoblins", "1988", [], "Jun 27, 1998", "907", "0089280"),
    Movie(9, 8, "The Touch of Satan", "1971", [], "Jul 11, 1998", "908", "0066476"),
    Movie(9, 9, "Gorgo", "1961", [], "Jul 18, 1998", "909", "0054938"),
    Movie(9, 10, "The Final Sacrifice", "1990", [], "Jul 25, 1998", "910", "0131550"),
    Movie(9, 11, "Devil Fish", "1984", [], "Aug 15, 1998", "911", "0088100"),
    Movie(9, 12, "The Screaming Skull", "1958", ["Robot Rumpus"], "Aug 29, 1998", "912", "0052169"),
    Movie(9, 13, "Quest of the Delta Knights", "1993", [], "Sep 26, 1998", "913", "0107910"),

    # Movie(10, 1, "Soultaker", "1990", [], "Apr 11, 1999", "1001", "0100665"),
    Movie(10, 2, "Girl in Gold Boots", "1968", [], "Apr 18, 1999", "1002", "0174685"),
    Movie(10, 3, "Merlin's Shop of Mystical Wonders", "1995", [], "Sep 12, 1999", "1003", "0174917"),
    Movie(10, 4, "Future War", "1997", [], "Apr 25, 1999", "1004", "0113135"),
    Movie(10, 5, "Blood Waters of Dr. Z (aka ZaAt)", "1972", [], "May 2, 1999", "1005", "0072666"),
    Movie(10, 6, "Boggy Creek II: and The Legend Continues...", "1983", [], "May 9, 1999", "1006", "0088772"),
    Movie(10, 7, "Track of the Moon Beast", "1976", [], "Jun 13, 1999", "1007", "0075343"),
    Movie(10, 8, "Final Justice", "1985", [], "Jun 20, 1999", "1008", "0087258"),
    Movie(10, 9, "Hamlet", "1961", [], "Jun 27, 1999", "1009", "0053888"),
    Movie(10, 10, "It Lives by Night", "1974", [], "Jul 18, 1999", "1010", "0071198"),
    Movie(10, 11, "Horrors of Spider Island", "1960", [], "Jul 25, 1999", "1011", "0054333"),
    # Movie(10, 12, "Squirm", "1976", ["A Case of Spring Fever"], "Aug 1, 1999", "1012", "0075261"),
    # Movie(10, 13, "Diabolik", "1968", [], "Aug 8, 1999", "1013", "0062861"),

    # Movie(11, 1, "Reptilicus", "1961", [], "Apr 14, 2017", "1101", "0056405"),
    # Movie(11, 2, "Cry Wilderness", "1987", [], "Apr 14, 2017", "1102", "0126848"),
    # Movie(11, 3, "The Time Travelers", "1694", [], "Apr 14, 2017", "1103", "0058659"),
    # Movie(11, 4, "Avalanche", "1978", [], "Apr 14, 2017", "1104", "0077189"),
    # Movie(11, 5, "The Beast of Hollow Mountain", "1956", [], "Apr 14, 2017", "1105", "0048992"),
    # Movie(11, 6, "Starcrash", "1978", [], "Apr 14, 2017", "1106", "0079946"),
    # Movie(11, 7, "The Land that Time Forgot", "1975", [], "Apr 14, 2017", "1107", "0073260"),
    # Movie(11, 8, "The Loves of Hercules", "1960", [], "Apr 14, 2017", "1108", "0053598"),
    # Movie(11, 9, "Yongary, Monster from the Deep", "1967", [], "", "1109", "0061549"),
    # Movie(11, 10, "Wizards of the Lost Kingdom", "1985", [], "Apr 14, 2017", "1110", "0090333"),
    # Movie(11, 11, "Wizards of the Lost Kingdom II", "1989", [], "Apr 14, 2017", "1111", "0090334"),
    # Movie(11, 12, "Carnival Magic", "1981", [], "Apr 14, 2017", "1112", "0207374"),
    # Movie(11, 13, "The Christmas that Almost Wasn't", "1966", [], "Apr 14, 2017", "1113", "0059032"),
    # Movie(11, 14, "At the Earth's Core", "1976", [], "Apr 14, 2017", "1114", "0074157"),

    # Movie(12, 1, "Mac and Me", "1988", [], "Nov 22, 2018", "1201", "0095560"),
    # Movie(12, 2, "Atlantic Rim", "2013", [], "Nov 22, 2018", "1202", "2740710"),
    # Movie(12, 3, "Lords of the Deep", "1980", [], "Nov 22, 2018", "1203", "0097781"),
    # Movie(12, 4, "The Day Time Ended", "1980", [], "Nov 22, 2018", "1204", "0080596"),
    # Movie(12, 5, "Killer Fish", "1979", [], "Nov 22, 2018", "1205", "0077800"),
    # Movie(12, 6, "Ator, The Fighting Eagle", "1982", [], "Nov 22, 2018", "1206", "0085183"),

    Movie(13, 1, "Santo in the Treasure of Dracula", "1969", [], "May 6, 2022", "1301", "0208504"),
    Movie(13, 2, "Robot Wars", "1993", [], "May 7, 2022", "1302", "0107979"),
    Movie(13, 3, "Beyond Atlantis", "1973", [], "May 8, 2022", "1303", "0069783"),
    Movie(13, 4, "Munchie", "1992", [], "May 27, 2022", "1304", "0104938"),
    Movie(13, 5, "Doctor Mordrid", "1992", [], "Jun 10, 2022", "1305", "0104115"),
    Movie(13, 6, "Demon Squad", "2019", [], "Jun 24, 2022", "1306", "4219706"),
    Movie(13, 7, "Gamera vs Jiger", "1970", [], "Jul 22, 2022", "1307", "0065755"),
    Movie(13, 8, "The Batwoman", "1968", [], "Aug 19, 2022", "1308", "0235608"),
    Movie(13, 9, "The Million Eyes of Sumuru", "1967", [], "Sep 2, 2022", "1309", "0061976"),
    Movie(13, 10, "H.G. Wells' The Shape of Things to Come", "1979", [], "Sep 30, 2022", "1310", "0079894"),
    Movie(13, 11, "The Mask", "1961", [], "Oct 28, 2022", "1311", "0055151"),
    Movie(13, 12, "The Bubble", "1966", [], "Nov 11, 2022", "1312", "0060396"),
    Movie(13, 13, "The Christmas Dragon", "2014", [], "Dec 16, 2022", "1313", "3918686"),

    Movie(13, 9, "The Million Eyes of Sumuru Livestream", "1967", [], "Sep 2, 2022", "1309", "0061976"),
    Movie(13, 6, "Demon Squad Livestream", "2019", [], "Jun 24, 2022", "1306", "4219706"),
    Movie(13, 11, "The Mask Livestream", "1961", [], "Oct 28, 2022", "1311", "0055151"),

    Movie(0, 1, "MST3K Shorts: Pipeline to the Clouds", "1951", [], "May 11, 2022", "SHORT-PTHC", "18951812"),
    Movie(0, 1, "MST3K Shorts: Let's Make a Meal in 20 Minutes!", "1950", [], "May 12, 2022", "SHORT-LMM20M", "0332203"),
    Movie(0, 1, "MST3K Shorts: Court Case", "", [], "May 13, 2022", "SHORT-COURT", ""),
    Movie(0, 1, "MST3K Shorts: Sleep for Health", "1950", [], "Jul 8, 2022", "SHORT-SLEEP", "8876486"),
    Movie(0, 1, "MST3K Shorts: The Wonder of Reproduction", "", [], "Aug 5, 2022", "SHORT-WOR", ""),
    Movie(0, 1, "MST3K Shorts: Cavalcade", "1960", [], "Sep 16, 2022", "SHORT-CAVAL", ""),
    Movie(0, 1, "MST3K Shorts: Balance Beam for Girls", "1971", [], "Oct 14, 2022", "SHORT-BBFG", ""),
    Movie(0, 1, "MST3K Shorts: Season 13's 13 Shorts", "", [], "Jul 2, 2023", "SHORT-S13SHORTS", ""),
    Movie(0, 1, "MST3K Shorts: Bicycling Visual Skills", "", [], "Jul 2, 2023", "SHORT-BVS", ""),
    Movie(0, 1, "MST3K Shorts: The Bicycle Driver", "", [], "Jul 2, 2023", "SHORT-BICYDRI", ""),
    Movie(0, 1, "MST3K Shorts: Let's Keep Food Safe to Eat", "", [], "Jul 2, 2023", "SHORT-LKFSE", ""),
    Movie(0, 1, "MST3K Shorts: Better Breakfast USA", "", [], "Jul 2, 2023", "SHORT-BBUSA", ""),
    Movie(0, 1, "MST3K Shorts: Doing Things for Ourselves in School", "1963", [], "Feb 10, 2023", "SHORT: DOSCHL", "9699730"),

    # Turkey Day Specials
    Movie(0, 1, "Turkey Day 91 Promos", "1991", [], "Nov 28, 1991", "TD91-PR"),
    Movie(0, 1, "Turkey Day 91 Segment Ring of Terror", "1991", [], "Nov 28, 1991", "TD91-01"),
    Movie(0, 1, "Turkey Day 91 Segment Cave Dwellers", "1991", [], "Nov 28, 1991", "TD91-02"),
    Movie(0, 1, "Turkey Day 91 Segment Jungle Goddess", "1991", [], "Nov 28, 1991", "TD91-03"),
    Movie(0, 1, "Turkey Day 91 Segment The Sidehackers", "1991", [], "Nov 28, 1991", "TD91-04"),
    Movie(0, 1, "Turkey Day 91 Segment Rocketship X-M", "1991", [], "Nov 28, 1991", "TD91-05"),
    Movie(0, 1, "Turkey Day 91 Segment Rocket Attack USA", "1991", [], "Nov 28, 1991", "TD91-06"),
    Movie(0, 1, "Turkey Day 91 Segment Time of the Apes", "1991", [], "Nov 28, 1991", "TD91-07"),
    Movie(0, 1, "Turkey Day 91 Segment Wild Rebels", "1991", [], "Nov 28, 1991", "TD91-08"),
    Movie(0, 1, "Turkey Day 91 Segment Amazing Colossal Man", "1991", [], "Nov 28, 1991", "TD91-09"),
    Movie(0, 1, "Turkey Day 91 Segment Godzilla vs. The Sea Monster", "1991", [], "Nov 28, 1991", "TD91-10"),
    Movie(0, 1, "Turkey Day 91 Segment Pod People", "1991", [], "Nov 28, 1991", "TD91-11"),
    Movie(0, 1, "Turkey Day 91 Segment Fugitive Alien", "1991", [], "Nov 28, 1991", "TD91-12"),
    Movie(0, 1, "Turkey Day 91 Segment Catalina Caper", "1991", [], "Nov 28, 1991", "TD91-13"),
    Movie(0, 1, "Turkey Day 91 Segment Daddy O", "1991", [], "Nov 28, 1991", "TD91-14"),
    Movie(0, 1, "Turkey Day 91 Segment It Conqured the World", "1991", [], "Nov 28, 1991", "TD91-15"),
    Movie(0, 1, "Turkey Day 91 Segment Final", "1991", [], "Nov 28, 1991", "TD91-16"),

    Movie(0, 1, "Turkey Day 92 Promos", "1992", [], "Nov 26, 1991", "TD92-PR"),
    Movie(0, 1, "Turkey Day 92 Segment The Beatniks", "1992", [], "Nov 26, 1991", "TD92-01"),
    Movie(0, 1, "Turkey Day 92 Segment Master Ninja I", "1992", [], "Nov 26, 1991", "TD92-02"),
    Movie(0, 1, "Turkey Day 92 Segment Space Travelers", "1992", [], "Nov 26, 1991", "TD92-03"),
    Movie(0, 1, "Turkey Day 92 Segment Lost Continent", "1992", [], "Nov 26, 1991", "TD92-04"),
    Movie(0, 1, "Turkey Day 92 Segment City Limits", "1992", [], "Nov 26, 1991", "TD92-05"),
    Movie(0, 1, "Turkey Day 92 Segment Viking Women", "1992", [], "Nov 26, 1991", "TD92-06"),
    Movie(0, 1, "Turkey Day 92 Segment The Giant Gila Monster", "1992", [], "Nov 26, 1991", "TD92-07"),
    Movie(0, 1, "Turkey Day 92 Segment King Dinosaur", "1992", [], "Nov 26, 1991", "TD92-08"),
    Movie(0, 1, "Turkey Day 92 Segment Santa Claus Conquers", "1992", [], "Nov 26, 1991", "TD92-09"),
    Movie(0, 1, "Turkey Day 92 Segment The Magic Sword", "1992", [], "Nov 26, 1991", "TD92-10"),
    Movie(0, 1, "Turkey Day 92 Segment Teenagers from Outer Space", "1992", [], "Nov 26, 1991", "TD92-11"),
    Movie(0, 1, "Turkey Day 92 Segment Hercules Unchained", "1992", [], "Nov 26, 1991", "TD92-12"),
    Movie(0, 1, "Turkey Day 92 Segment The Unearthly", "1992", [], "Nov 26, 1991", "TD92-13"),
    Movie(0, 1, "Turkey Day 92 Segment Gamera vs Guiron", "1992", [], "Nov 26, 1991", "TD92-14"),
    Movie(0, 1, "Turkey Day 92 Segment Fire Maidens of Outer Space", "1992", [], "Nov 26, 1991", "TD92-15"),
    Movie(0, 1, "Turkey Day 92 Segment Final", "1992", [], "Nov 26, 1991", "TD92-16"),

    Movie(0, 1, "Turkey Day 95 Promos", "1995", [], "Nov 23, 1995", "TD95-PR"),
    # 1995
    Movie(0, 1, "Turkey Day 1995, Part 1 - Crawling Hand", "1995", [], "Nov 23, 1995", "TD95-1"),
    Movie(0, 1, "Turkey Day 1995, Part 2 - Manos", "1995", [], "Nov 23, 1995", "TD95-2"),
    Movie(0, 1, "Turkey Day 1995, Part 3 - Mitchell", "1995", [], "Nov 23, 1995", "TD95-3"),
    Movie(0, 1, "Turkey Day 1995, Part 4 - Outlaw", "1995", [], "Nov 23, 1995", "TD95-4"),
    Movie(0, 1, "Turkey Day 1995, Part 5 - Skydivers", "1995", [], "Nov 23, 1995", "TD95-5"),
    Movie(0, 1, "Turkey Day 1995, Part 6 - Starfighters", "1995", [], "Nov 23, 1995", "TD95-6"),
    Movie(0, 1, "Turkey Day 1995, Part 7 - Final", "1995", [], "Nov 23, 1995", "TD95-7"),
    Movie(7, 1, "Night of the Blood Beast (Turkey Day)", "1958", ["Once Upon a Honeymoon"], "Nov 23, 1995", "701T", "0051993"),

    Movie(0, 1, "Turkey Day 1995, Part 1 - Crawling Hand", "1995", [], "Nov 23, 1995", "TD95-1"),

    # Specials
    Movie(0, 1, "Poopie!", "1995", [], "", "POOP1"),
    Movie(0, 1, "Poopie! II", "1997", [], "", "POOP2"),
    Movie(0, 1, "Poopie Parade of Values", "1995", [], "Nov 23, 1995", "POOPPOV"),
    Movie(0, 1, "MST3K Little Gold Statue Preview 1995", "1995", [], "Mar 22, 1995", "LGSP95"),
    Movie(0, 1, "MST3K Summer Blockbuster Review 1997", "1997", [], "Sep 2, 1997", "SBR97"),
    Movie(0, 1, "MST3K Summer Blockbuster Review 1998", "1998", [], "Sep 4, 1998", "SBR98"),
    Movie(0, 1, "MST3K Academy of Robots' Choice Awards Special", "1998", [], "Mar 19, 1998", "AORCAS"),

    # Movie(0, 0, "Backlot: The History of MST3K, Part 1", "", [], "", "BL13"),
    # Movie(0, 0, "Backlot: The History of MST3K, Part 2", "", [], "", "BL14"),
    # Movie(0, 0, "Backlot: The History of MST3K, Part 3", "", [], "", "BL15"),
    Movie(0, 0, "Backlot: History", "", [], "", "BL13"),
    Movie(0, 0, "Backlot: History 2", "", [], "", "BL14"),
    Movie(0, 0, "Backlot: History 3", "", [], "", "BL15"),

    Movie(0, 1, "April Fools'", "2024", [], "Apr 1, 2024", "APRILFOOLS2024"),

    Movie(0, 0, "101 Intro By Joel", "2010", [], "", "INTRO101"),
    Movie(0, 0, "106 Doc", "2018", [], "", "DOC106"),
    Movie(0, 0, "107 Intro By Josh", "2010", [], "", "INTRO106"),
    Movie(0, 0, "107 Doc", "2010", [], "", "DOC107"),
    Movie(0, 0, "108 Interview", "2013", [], "", "INTV108"),
    Movie(0, 0, "110 Intro By Joel", "2012", [], "", "INTRO110"),
    Movie(0, 0, "111 Interview", "2013", [], "", "INTV111"),
    Movie(0, 0, "112 Intro By Joel", "2014", [], "", "INTRO112"),
    Movie(0, 0, "112 Mamie Interview", "2014", [], "", "INTV112"),
    Movie(0, 0, "113 Doc", "2014", [], "", "DOC113"),
    Movie(0, 0, "104 Interview", "2006", [], "", "INTV104"),
    Movie(0, 0, "202 BTS", "1990", [], "", "BTS202"),
    Movie(0, 0, "202 Interview", "2016", [], "", "INTV202"),
    Movie(0, 0, "204 Doc", "2016", [], "", "DOC204"),
    Movie(0, 0, "206 Doc", "2019", [], "", "DOC206"),
    Movie(0, 0, "207 Doc", "2019", [], "", "DOC206"),
    Movie(0, 0, "208 Intro By Frank", "2010", [], "", "INTRO208"),
    Movie(0, 0, "302 Doc", "2011", [], "", "DOC302"),
    Movie(0, 0, "304 Doc", "", [], "", "DOC304"),
    Movie(0, 0, "305 Doc", "", [], "", "DOC305"),
    Movie(0, 0, "306 Intro", "", [], "", "INTRO306"),
    Movie(0, 0, "307 Doc", "", [], "", "DOC307"),
    Movie(0, 0, "308 Interview", "", [], "", "INTV308"),
    Movie(0, 0, "310 Intro", "", [], "", "INTRO310"),
    Movie(0, 0, "313 Doc", "", [], "", "DOC313"),
    Movie(0, 0, "314 Intro", "", [], "", "INTRO314"),
    Movie(0, 0, "315 Doc", "", [], "", "DOC315"),
    Movie(0, 0, "317 Intro By Frank", "", [], "", "INTRO317"),
    Movie(0, 0, "318 Sandy Doc", "", [], "", "DOC318"),
    Movie(0, 0, "319 Intro By Frank", "", [], "", "INTRO319"),
    Movie(0, 0, "320 BTS", "", [], "", "BTS320"),
    Movie(0, 0, "321 Intro By Joel", "", [], "", "INTRO321"),
    Movie(0, 0, "322 Interview", "", [], "", "INTV322"),
    Movie(0, 0, "323 Intro By Frank", "", [], "", "INTRO323"),
    Movie(0, 0, "402 Interview", "", [], "", "INTV402"),
    Movie(0, 0, "402 Replacement", "", [], "", "REPL402"),
    Movie(0, 0, "403 Interview", "", [], "", "INTV402"),
    Movie(0, 0, "405 Doc", "", [], "", "DOC405"),
    Movie(0, 0, "409 Doc", "", [], "", "DOC409"),
    Movie(0, 0, "411 Interview", "", [], "", "INTV411"),
    Movie(0, 0, "412 Intro By Joel", "", [], "", "INTRO412"),
    Movie(0, 0, "414 Interview", "", [], "", "INTV414"),
    Movie(0, 0, "419 Doc", "", [], "", "DOC419"),
    Movie(0, 0, "419 Interview", "", [], "", "INTV419"),
    Movie(0, 0, "421 Interview", "", [], "", "INTV421"),
    Movie(0, 0, "423 Doc", "", [], "", "DOC423"),
    Movie(0, 0, "423 Invention Exchange", "", [], "", "INVEXCH423"),
    Movie(0, 0, "424 Group Doc", "", [], "", "DOC424"),
    Movie(0, 0, "424 Hotel Torgo Doc", "", [], "", "DOC424TORGO"),
    Movie(0, 0, "424 Jam Doc", "", [], "", "DOC424JAM"),
    Movie(0, 0, "424 Joel On Jam", "", [], "", "JAM424"),
    Movie(0, 0, "501 Doc", "", [], "", "DOC501"),
    Movie(0, 0, "501 Interview", "", [], "", "INTV501"),
    Movie(0, 0, "502 Intro By Frank", "", [], "", "INTRO502"),
    Movie(0, 0, "502 Doc", "", [], "", "DOC502"),
    Movie(0, 0, "505 Intro By Trace", "", [], "", "INTRO505"),
    Movie(0, 0, "506 Intro By Joel", "", [], "", "INTRO506"),
    Movie(0, 0, "507 Intro By Joel", "", [], "", "INTRO507"),
    Movie(0, 0, "507 Doc", "", [], "", "DOC507"),
    Movie(0, 0, "508 Intro By Joel", "", [], "", "INTRO508"),
    Movie(0, 0, "512 Joel Final Ride", "", [], "", "FINAL512"),
    Movie(0, 0, "513 Interview", "", [], "", "INTV513"),
    Movie(0, 0, "516 Interview", "", [], "", "INTV516"),
    Movie(0, 0, "518 BTS", "", [], "", "BTS518"),
    Movie(0, 0, "520 Intro By Frank", "", [], "", "INTRO520"),
    Movie(0, 0, "523 Interview", "", [], "", "INTV523"),
    Movie(0, 0, "602 Doc", "", [], "", "DOC602"),
    Movie(0, 0, "603 Interview", "", [], "", "INTV603"),
    Movie(0, 0, "604 Doc", "", [], "", "DOC604"),
    Movie(0, 0, "608 Doc", "", [], "", "DOC608"),
    Movie(0, 0, "610 Interview", "", [], "", "INTV610"),
    Movie(0, 0, "610 Other Interview", "", [], "", "INTV610-2"),
    Movie(0, 0, "612 Doc", "", [], "", "DOC612"),
    Movie(0, 0, "613 Intro", "", [], "", "INTRO613"),
    Movie(0, 0, "613 Doc", "", [], "", "DOC613"),
    Movie(0, 0, "621 Doc", "", [], "", "DOC621"),
    Movie(0, 0, "621 Interview", "", [], "", "INTV621"),
    Movie(0, 0, "623 Doc", "", [], "", "DOC623"),
    Movie(0, 0, "624 Doc", "", [], "", "DOC634"),
    Movie(0, 0, "702 Intro By Mary Jo", "", [], "", "INTRO702"),
    Movie(0, 0, "702 Doc", "", [], "", "DOC702"),
    Movie(0, 0, "703 Doc", "", [], "", "DOC703"),
    Movie(0, 0, "705 Intro By Mary Jo", "", [], "", "INTRO705"),
    Movie(0, 0, "705 Doc", "", [], "", "DOC705"),
    Movie(0, 0, "810 Interview", "", [], "", "INTV810"),
    Movie(0, 0, "811 Interview", "", [], "", "INTV811"),
    Movie(0, 0, "813 Intro By Kevin", "", [], "", "INTRO813"),
    Movie(0, 0, "817 Intro By Mary Jo", "", [], "", "INTRO817"),
    Movie(0, 0, "817 Doc", "", [], "", "DOC817"),
    Movie(0, 0, "818 Doc", "", [], "", "DOC818"),
    Movie(0, 0, "819 Intro By Mary Jo", "", [], "", "INTRO819"),
    Movie(0, 0, "819 Doc", "", [], "", "DOC819"),
    Movie(0, 0, "820 Intro By Mike", "", [], "", "INTRO820"),
    Movie(0, 0, "821 Intro By Mike", "", [], "", "INTRO821"),
    Movie(0, 0, "822 Intro By Mike", "", [], "", "INTRO822"),
    Movie(0, 0, "903 Interview", "", [], "", "INTV903"),
    Movie(0, 0, "907 Interview", "", [], "", "INTV907"),
    Movie(0, 0, "908 Intro By Mike", "", [], "", "INTRO908"),
    Movie(0, 0, "909 Intro", "", [], "", "INTRO909"),
    Movie(0, 0, "910 Interview", "", [], "", "INTV910"),
    Movie(0, 0, "912 Gumby Doc", "", [], "", "DOC912"),
    Movie(0, 0, "912 Interview", "", [], "", "INTV912"),
    Movie(0, 0, "1002 Intro By Mike", "", [], "", "INTRO1002"),
    Movie(0, 0, "1003 Intro By Mike", "", [], "", "INTRO1003"),
    Movie(0, 0, "1006 Intro By Mike", "", [], "", "INTRO1006"),
    Movie(0, 0, "1007 Interview", "", [], "", "INTV1007"),
    Movie(0, 0, "1008 Interview", "", [], "", "INTV1008"),
    Movie(0, 0, "1009 Intro By Mike", "", [], "", "INTRO1009"),
    Movie(0, 0, "Nanites Doc", "", [], "", "DOCNAN"),
    Movie(0, 0, "Crow Vs Crow Doc", "", [], "", "DOCCROWVS"),
    Movie(0, 0, "Servo Vs Servo Doc", "", [], "", "DOCSERVOVS"),
    Movie(0, 0, "MST3K 2008 CON", "", [], "", "CON2008"),
    Movie(0, 0, "MST3K 2009 CON", "", [], "", "CON2009"),
    Movie(0, 0, "MST3K UK Doc", "", [], "", "DOCUK"),
    Movie(0, 0, "Joel On Mike", "", [], "", "JOELONMIKE"),
    Movie(0, 0, "Kevin Mike Interview", "", [], "", "INTVKEVMIKE"),
    Movie(0, 0, "Life After MST3K Bill", "", [], "", "LIFEBILL"),
    Movie(0, 0, "Life After MST3K Frank", "", [], "", "LIFEFRANK"),
    Movie(0, 0, "Life After MST3K Josh", "", [], "", "LIFEJOSH"),
    Movie(0, 0, "Life After MST3K Kevin", "", [], "", "LIFEKEVIN"),
    Movie(0, 0, "Life After MST3K Mary Jo", "", [], "", "LIFEMJ"),
    Movie(0, 0, "Life After MST3K Mike", "", [], "", "LIFEMIKE"),
    Movie(0, 0, "Life After MST3K Trace", "", [], "", "LIFETRACE"),
    Movie(0, 0, "MST3K Jeff Stonehouse Look Doc", "", [], "", "DOCJEFF"),
    Movie(0, 0, "MST3K Theme Chuck Love Doc", "", [], "", "DOCTHEME"),
    Movie(0, 0, "MST3k Home Game BTS", "", [], "", "BTSGAME"),
    Movie(0, 0, "Film Crew Cutting Floor", "", [], "", "FC-CUT"),
    Movie(0, 0, "MST3K Scrapbook UnScrapped", "", [], "", "SCRAP"),
    Movie(0, 0, "MST3K Playstation", "", [], "", "PSX"),
    Movie(0, 0, "Making of MST3K 1997", "", [], "", "MAKING97"),
    Movie(0, 0, "Radar Men From The Moon Intro By Josh", "", [], "", "INTRORADAR"),
    Movie(0, 0, "MST Hour 301", "", [], "", "MSTH301"),
    Movie(0, 0, "MST Hour 302", "", [], "", "MSTH302"),
    Movie(0, 0, "MST Hour 303", "", [], "", "MSTH303"),
    Movie(0, 0, "MST Hour 306", "", [], "", "MSTH306"),
    Movie(0, 0, "MST Hour 307", "", [], "", "MSTH307"),
    Movie(0, 0, "MST Hour 309", "", [], "", "MSTH309"),
    Movie(0, 0, "MST Hour 310", "", [], "", "MSTH310"),
    Movie(0, 0, "MST Hour 311", "", [], "", "MSTH311"),
    Movie(0, 0, "MST Hour 312", "", [], "", "MSTH312"),
    Movie(0, 0, "MST Hour 313", "", [], "", "MSTH313"),
    Movie(0, 0, "MST Hour 317", "", [], "", "MSTH317"),
    Movie(0, 0, "MST Hour 319", "", [], "", "MSTH319"),
    Movie(0, 0, "MST Hour 320", "", [], "", "MSTH320"),
    Movie(0, 0, "MST Hour 321", "", [], "", "MSTH321"),
    Movie(0, 0, "MST Hour 401", "", [], "", "MSTH401"),
    Movie(0, 0, "MST Hour 402", "", [], "", "MSTH402"),
    Movie(0, 0, "MST Hour 404", "", [], "", "MSTH404"),
    Movie(0, 0, "MST Hour 408", "", [], "", "MSTH408"),
    Movie(0, 0, "MST Hour 410", "", [], "", "MSTH410"),
    Movie(0, 0, "MST Hour 411", "", [], "", "MSTH411"),
    Movie(0, 0, "MST Hour 414", "", [], "", "MSTH414"),
    Movie(0, 0, "MST Hour 415", "", [], "", "MSTH415"),
    Movie(0, 0, "MST Hour 417", "", [], "", "MSTH417"),
    Movie(0, 0, "MST Hour 418", "", [], "", "MSTH418"),
    Movie(0, 0, "MST Hour 420", "", [], "", "MSTH420"),
    Movie(0, 0, "MST Hour 422", "", [], "", "MSTH422"),
    Movie(0, 0, "MST Hour 424", "", [], "", "MSTH424"),
    Movie(0, 0, "MST Hour 504", "", [], "", "MSTH504"),
    Movie(0, 0, "MST Hour 505", "", [], "", "MSTH505"),
    Movie(0, 0, "MST Hour 507", "", [], "", "MSTH507"),
]

current_movie = movies[0]


def test(result: str, expected: str):
    print(result)
    assert expected in result


if __name__ == '__main__':
    update()
    load()

    out = get_schedule(US_EAST, 25)
    print(out)
    print()

    print(datetime.strftime(datetime.now(), "%b"))
    print()
