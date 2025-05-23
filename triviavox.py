import asyncio
import platform
import random
import re
import time
import urllib.error
from enum import Enum
from os import listdir
from os.path import isfile, join

import pygame.image
from aiohttp import ClientConnectorError
from twitchio import Message, Channel, AuthenticationError, Unauthorized
from twitchio.chatter import WhisperChatter
from twitchio.ext import commands, routines
from sty import fg, rs, ef

import botads
import botemoji
import botgems
import botquote
import botscramble
import botsecrets
import bottoken
import bottrivia
import funfactory
import gradient
import scroller
import util_text
from anims.candy_heart_snow import CandyHeartSnow
from anims.clover_snow import CloverSnow
from anims.snow import SnowFlake
from botscramble import SCRAMBLED_WORDS
from character_game import CHARACTERS, CHARACTER_PATH
from colors import *
from constants import *
from fonts import STR_STINGER, TXT_STINGER, FONT_MST3K_LG, TXT_EMOJI, FONT_EMOJI_LG, TXT_CHARACTER, STR_CHARACTER
from movie_names import MOVIE_NAMES
from util_text import wrap_text

# This gets set to True on Windows platforms
IS_DEBUG = False

# CHANNEL_ID = 105623158
# CHANNEL_NAME = "mst3k"
CHANNEL_ID = 476069938
CHANNEL_NAME = "movievox"

FPS = 60
UPDATE_RATE = 1 / (FPS * 2)

WIDTH = 1920
HEIGHT = 1080

W2 = WIDTH // 2
H2 = HEIGHT // 2

pygame.init()
scr = pygame.display.set_mode((WIDTH, HEIGHT))
clk = pygame.time.Clock()

STINGER_PATH = "images/stingers/"

EMJ_NINJA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/ninja_1f977.png'), 0.115).convert_alpha()
EMJ_MELT_FACE = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/melting-face_1fae0.png'), 0.11).convert_alpha()
EMJ_BKNIGHT = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/black-knight-2692.png'), 0.4).convert_alpha()
EMJ_INCREASE = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/increase-font-size-symbol_1f5da.png'), 0.375).convert_alpha()
EMJ_CUBA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-cuba_1f1e8-1f1fa.png'), 0.11).convert_alpha()
EMJ_MALTA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-malta_1f1f2-1f1f9.png'), 0.11).convert_alpha()
EMJ_MEXICO = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-mexico_1f1f2-1f1fd.png'), 0.11).convert_alpha()
EMJ_USA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-united-states_1f1fa-1f1f8.png'), 0.10).convert_alpha()

# Draw the games onto this smaller Surface and blit them to the main screen Surface
alt_screen = pygame.Surface((W2, H2))
is_running = True
dt = 0


class GameType(Enum):
    TRIVIA = "Trivia"
    EMOJI = "Emoji"
    STINGER = "Stinger"
    CHARACTER = "Character"
    SCRAMBLE = "Scramble"


class TriviaVox(commands.Bot):
    def __init__(self, screen, clock, access_token):
        super().__init__(token=access_token, initial_channels=[CHANNEL_NAME], prefix="!",
                         client_secret=botsecrets.CLIENT_SECRET)

        self.access_token = access_token
        self.screen = screen
        self.clock = clock

        self.channel = super().get_channel(CHANNEL_NAME)
        self.is_connecting = False
        self.is_live = True

        self.start_trivia_time = 0
        self.next_ad_at = 0

        self.sub_list = []
        self.personal_trivia = {}

        self.game_type = GameType.TRIVIA
        self.trivia_questions = []
        self.prev_trivia = []

        self.emoji_questions = []
        self.prev_emoji = []

        self.trivia_question = None
        self.preserved_answer = ""
        self.trivia_winners = []
        self.game_end_time = 0

        self.stinger_img = None
        self.stinger_num = 0
        self.prev_stingers = []

        self.character_img = None
        self.prev_characters = []

        self.scramble_word = ""
        self.prev_scrambles = []

        try:
            botquote.update()
        except urllib.error.URLError:
            print("ERROR downloading quotes file; using existing file.")
        self.quotes = botquote.load()

    async def check_if_live(self):
        try:
            streams = await self.fetch_streams(user_ids=[CHANNEL_ID])
            self.is_live = len(streams) > 0
        except ClientConnectorError:
            print("ERROR: Could not reach the stream to test if live. is_live=" + str(self.is_live))

    async def bot_print(self, txt, color=fg.white):
        print(color + txt + rs.fg)
        if not IS_DEBUG and self.channel is not None:
            try:
                await self.channel.send(txt)
            except ConnectionResetError:
                if not self.is_connecting:
                    self.is_connecting = True
                    await self.connect()

    async def get_ads_schedule(self):
        if self.access_token != botsecrets.OAUTH_TOKEN:
            u = await self.channel.user()
            ads = await u.fetch_ad_schedule(self.access_token)
            next_at = int(ads.next_ad_at)
            print("Next ad at:", next_at, botads.convert_int_to_datetime(next_at))
            self.next_ad_at = next_at

    async def event_ready(self):
        self.is_connecting = False
        await self.check_if_live()
        self.channel = super().get_channel(CHANNEL_NAME)

        try:
            bottrivia.update()
        except (AuthenticationError, Unauthorized):
            print("ERROR: Could not download trivia; using existing file.")
        self.trivia_questions = bottrivia.load_as_array()

        try:
            botemoji.update()
        except (AuthenticationError, Unauthorized):
            print("ERROR: Could not download emoji trivia; using existing file.")
        self.emoji_questions = botemoji.load_as_array()

        self.auto_update_time_until.start()
        self.auto_trivia_stop.start()
        self.auto_update_game.start()
        # self.auto_message.start()

        ts = int(datetime.now().timestamp())
        try:
            await self.get_ads_schedule()
            botads.save_ads_time(self.next_ad_at, botads.convert_int_to_time(self.next_ad_at))
        except (AuthenticationError, Unauthorized):
            print("ERROR: Could not get ad schedule from Twitch; using file.")

            times = botads.load_ads_time()
            if len(times) == 2:
                self.next_ad_at = int(times[0])
                while self.next_ad_at < ts:
                    self.next_ad_at += 3600
                ad_date = times[1]
                print("Ad time has been set from file. Next ads at {} (Eastern).".format(ad_date))
            else:
                self.next_ad_at = ts + 3600
                next_time = botads.convert_int_to_time(self.next_ad_at)
                botads.save_ads_time(self.next_ad_at, next_time)
                print("Ad time has been set. Next ads at {} (Eastern).".format(next_time))

        # Don't start trivia unless the minutes are divisible by 5
        delay_sec = 0
        if not IS_DEBUG:
            for i in range(300):
                if (ts + i) % 300 == 0:
                    self.start_trivia_time = ts + i
                    delay_sec = i
                    break
        else:
            delay_sec = 1

        print("TriviaVox ready, channel is live={}".format(self.is_live))

        print("Waiting {} seconds to start trivia.".format(str(delay_sec)))
        await asyncio.sleep(delay_sec)
        self.auto_trivia.start()

    async def event_message(self, message: Message) -> None:
        if message.echo:
            return

        username = message.author.name  # "WhisperUser" doesn't have a display name attribute
        if type(message.author) is not WhisperChatter:
            username = message.author.display_name

        # Check if this is a command to display a quote
        output = ""
        msg = str(message.content).strip()
        if msg[0] == "!" and len(msg) > 1:
            parts = msg[1:].lower().split()
            command = parts[0]

            try:
                specific_num = int(parts[1]) if len(parts) > 1 else 0
            except ValueError:
                specific_num = 0

            if command in self.quotes.keys():
                if specific_num == 0:
                    output = self.quotes[command].random()
                else:
                    if len(self.quotes[command].quotes) >= specific_num:
                        output = self.quotes[command].quotes[specific_num - 1]
                    else:
                        output = self.quotes[command].quote()
            output = botquote.apply_params(output, msg, username, scroller.sched[0]['title'])
            await self.bot_print(output)

        if self.trivia_question is not None:
            guess = util_text.normalize_answers([message.content])[0]
            if guess in self.trivia_question.answers:
                self.trivia_winners.append(username)

                # Only start the timer after the first winner is detected.
                if len(self.trivia_winners) == 1:
                    await asyncio.sleep(10)
                    await self.stop_trivia()

        # Is the user in the middle of a personal trivia game ("!gems redeem")
        if username in self.personal_trivia.keys():
            # If the user ia a subscriber, put their name in the sub_list.
            if message.author.is_subscriber:
                self.sub_list.append(username)
                self.sub_list = list(set(self.sub_list))

            # Now that the user has responded to the personal trivia question, deduct the gems
            botgems.save_gems(username, botgems.get_gems(username) - botgems.GEM_REDEEM)

            q = self.personal_trivia[username]
            preserved_answer = q.answers[0]
            answers = util_text.normalize_answers(q.answers)
            guess = util_text.normalize_answers([message.content])[0]

            if guess in answers:
                await self.bot_print("@{}, correct! You now have {} points."
                                     .format(username, str(bottrivia.get_trivia_points(username) + 1)))
                bottrivia.save_trivia_user_with_points(username, bottrivia.get_trivia_points(username) + 1)
            else:
                await self.bot_print("@{}, sorry, that's incorrect. The answer is: {}"
                                     .format(username, preserved_answer))

            # remove user from personal_trivia
            del self.personal_trivia[username]

        await self.handle_commands(message)

    async def event_command_error(self, ctx: commands.Context, error):
        """Ignore command errors"""
        pass

    async def event_raw_usernotice(self, channel: Channel, tags: dict):
        msg_id = tags['msg-id'].strip().lower()
        if msg_id in ["sub", "resub", "subgift", "submysterygift", "giftpaidupgrade", "rewardgift", "anongiftpaidupgrade"]:
            await self.bot_print("Thank you for supporting the channel, {}!".format(tags["display-name"]), fg.blue)

    @routines.routine(minutes=5)
    async def auto_trivia(self):
        """Run a trivia question every few minutes."""
        """
        await self.check_if_live()
        ts = int(datetime.now().timestamp())

        if self.next_ad_at < ts:
            try:
                await self.get_ads_schedule()
            except (AuthenticationError, Unauthorized):
                print("ERROR loading ad schedule in routine 'auto_trivia'.")
                self.next_ad_at += 3600
                print("Manually setting next ad time to " + str(self.next_ad_at))

            botads.save_ads_time(self.next_ad_at)
        """

        """
        This ad detection stopped working so I am disabling it.
        
        # If ads are running in the next 5 minutes (300 seconds), don't start a game that needs the screen
        if self.is_live and self.next_ad_at - ts > 300:
            self.game_type = random.choice([GameType.TRIVIA, GameType.EMOJI, GameType.STINGER, GameType.CHARACTER])
            # self.game_type = random.choice([GameType.TRIVIA, GameType.EMOJI, GameType.STINGER, GameType.CHARACTER,
            #                                 GameType.SCRAMBLE])
        else:
            print("Not choosing a Stinger/Character game because of the time.")
            self.game_type = random.choice([GameType.TRIVIA, GameType.EMOJI])
        """
        self.game_type = random.choice([GameType.TRIVIA, GameType.EMOJI, GameType.STINGER, GameType.CHARACTER])

        if IS_DEBUG:
            self.game_type = GameType.STINGER

        if self.game_type == GameType.TRIVIA:
            self.trivia_question = random.choice(self.trivia_questions)
            while self.trivia_question in self.prev_trivia:
                self.trivia_question = random.choice(self.trivia_questions)

            self.preserved_answer = self.trivia_question.answers[0]
            self.trivia_question.answers = util_text.normalize_answers(self.trivia_question.answers)
            self.prev_trivia.append(self.trivia_question)
            if len(self.prev_trivia) > 20:
                self.prev_trivia.pop(0)
            # self.trivia_winners.clear()
            # self.game_end_time = time.time() + 60

            await self.bot_print("/me Trivia Time! Q: {}".format(self.trivia_question.question), fg.li_yellow)

        elif self.game_type == GameType.EMOJI:
            self.trivia_question = random.choice(self.emoji_questions)
            while self.trivia_question in self.prev_emoji:
                self.trivia_question = random.choice(self.emoji_questions)

            if IS_DEBUG:
                # self.trivia_question = self.emoji_questions[1]
                # self.trivia_question = self.emoji_questions[36]
                # self.trivia_question = self.emoji_questions[38]
                # self.trivia_question = self.emoji_questions[76]
                # self.trivia_question = self.emoji_questions[90]
                # self.trivia_question = self.emoji_questions[96]
                # self.trivia_question = self.emoji_questions[133]
                # self.trivia_question = self.emoji_questions[89]
                # self.trivia_question = self.emoji_questions[110]
                # self.trivia_question = self.emoji_questions[125]
                pass

            self.preserved_answer = self.trivia_question.answers[0]
            self.trivia_question.answers = util_text.normalize_answers(self.trivia_question.answers)
            self.prev_trivia.append(self.trivia_question)
            if len(self.prev_emoji) > 20:
                self.prev_emoji.pop(0)
            # self.trivia_winners.clear()
            # self.game_end_time = time.time() + 60

            await self.bot_print("/me Emoji Time! Q: {}".format(self.trivia_question.question), fg.li_yellow)

        elif self.game_type == GameType.STINGER:
            stinger_file = choose_stinger()
            stinger_num = stinger_file[:-4]
            while stinger_num in self.prev_stingers:
                stinger_file = choose_stinger()
                stinger_num = stinger_file[:-4]

            answers = MOVIE_NAMES[stinger_num]
            answers.append(str(stinger_num))
            self.trivia_question = bottrivia.Trivia(STR_STINGER, answers)

            self.preserved_answer = self.trivia_question.answers[0]
            self.trivia_question.answers = util_text.normalize_answers(self.trivia_question.answers)
            self.prev_stingers.append(stinger_num)
            if len(self.prev_stingers) > 20:
                self.prev_stingers.pop(0)
            # self.trivia_winners.clear()
            # self.game_end_time = time.time() + 60

            await self.bot_print("/me Name the stinger seen on screen.", fg.yellow)
            self.stinger_img = load_scaled_image(STINGER_PATH + stinger_file)

        elif self.game_type == GameType.CHARACTER:
            character = random.choice(CHARACTERS)
            while character in self.prev_characters:
                character = random.choice(CHARACTERS)

            answers = character.names
            self.trivia_question = bottrivia.Trivia(STR_CHARACTER, answers)

            self.preserved_answer = self.trivia_question.answers[0]
            self.trivia_question.answers = util_text.normalize_answers(self.trivia_question.answers)
            self.prev_characters.append(character)
            if len(self.prev_characters) > 20:
                self.prev_characters.pop(0)
            # self.trivia_winners.clear()
            # self.game_end_time = time.time() + 60

            await self.bot_print("/me Name the character seen on screen.", fg.yellow)
            self.character_img = load_scaled_image(CHARACTER_PATH + character.img_file)

        elif self.game_type == GameType.SCRAMBLE:
            scramble_word = random.choice(SCRAMBLED_WORDS)
            while scramble_word in self.prev_scrambles:
                scramble_word = random.choice(SCRAMBLED_WORDS)

            self.trivia_question = bottrivia.Trivia(botscramble.scramble(scramble_word), [scramble_word])
            self.preserved_answer = self.trivia_question.answers[0]
            self.trivia_question.answers = util_text.normalize_answers(self.trivia_question.answers)
            self.prev_scrambles.append(scramble_word)
            if len(self.prev_scrambles) > 20:
                self.prev_scrambles.pop(0)
            # self.trivia_winners.clear()
            # self.game_end_time = time.time() + 60

            await self.bot_print("/me Unscramble the character name on screen.")

        self.trivia_winners.clear()
        self.game_end_time = time.time() + 60
        print(fg.cyan + str(self.trivia_question.answers) + rs.fg)

    @routines.routine(seconds=15)
    async def auto_update_time_until(self):
        now = datetime.now()
        next_start = datetime.strptime(scroller.sched[1]['datetime_est'], "%a, %b %d %I:%M%p %Y")
        delta_secs = (next_start - now).total_seconds()

        hours = int(delta_secs // 3600)
        minutes = int((delta_secs % 3600) // 60)
        seconds = delta_secs % 60

        minutes += 1 if seconds > 29 else 0  # Round up the minutes

        scroller.time_until = "in {}h {}m".format(str(hours), str(minutes))
        if hours == 0 and minutes == 0:
            scroller.time_until = "in <1m".format(str(minutes))
        elif hours == 0:
            scroller.time_until = "in {}m".format(str(minutes))

    @routines.routine(seconds=2)
    async def auto_trivia_stop(self):
        """Check if it's time to stop the game."""
        if self.trivia_question is not None and time.time() >= self.game_end_time and len(self.trivia_winners) == 0:
            output = "/me No trivia winner. Q: {} A: {}".format(
                self.trivia_question.question, self.preserved_answer)
            await self.bot_print(output)
            self.trivia_question = None

    @routines.routine(seconds=UPDATE_RATE)
    async def auto_update_game(self):
        self.game_loop()

    @routines.routine(minutes=20)
    async def auto_message(self):
        # output = ("MST3K trivia every 5 minutes. "
        #           "Watch on 'Source' mode to reduce latency between screen and chat (!latency for more).")
        # output = ("Ads have been reduce as much as possible to 30 seconds every hour (the lowest amount allowed "
        #           "by Twitch). Thank you for your patience while I tested channel ads. I feel it's better to "
        #           "minimize ads to increase enjoyment rather than trying to monetize this channel. "
        #           "Thank you for all your support with subs and bits!")
        output = """Ads have been reduced to the lowest allowed by Twitch, 30 seconds/hour.
                    I feel this is the best way to maximize enjoyment of the channel.                
                    Thank you for your patience and support!"""
        await self.bot_print(output)

    async def stop_trivia(self):
        """Stop the trivia game, display the winners, update winners' points"""
        if self.trivia_question is not None:
            self.trivia_question = None

            # Remove any duplicate winners then sort the names (case-insensitive)
            winners = list(set(self.trivia_winners))
            winners.sort(key=str.casefold)

            # Look up the points for each winner
            name_and_points = []
            for name in winners:
                name_and_points.append(name + " (" + str(bottrivia.get_trivia_points(name) + 1) + ")")

            # Format the list of winners
            output = bottrivia.format_round_winners(name_and_points)
            await self.bot_print(output)

            # Check for special achievements
            for n_p in name_and_points:
                parts = n_p.rstrip(")").split(" (")
                name = parts[0]
                points = parts[1]
                # print(name, points)
                if int(points) % 100 == 0:
                    await self.bot_print("Special congrats to {} on reaching {} points!".format(name, str(points)))

            # Save the new number of points for the winners
            bottrivia.save_trivia_winners(winners)
            botgems.save_winners(winners, self.sub_list)
            self.trivia_winners.clear()

    @commands.command(name="ads", aliases=['Ads', 'ADS'])
    async def cmd_ads(self, ctx: commands.Context):
        privs = ctx.author.is_broadcaster or ctx.author.is_mod  # or ctx.author.is_vip or ctx.author.is_subscriber

        if privs:
            self.next_ad_at = int(datetime.now().timestamp() + 3600)
            ad_date = datetime.strftime(datetime.fromtimestamp(self.next_ad_at), "%I:%M:%S %p")
            botads.save_ads_time(self.next_ad_at, ad_date)
            await self.bot_print("Ad time has been set. Next ads at {} (Eastern).".format(ad_date))

        else:
            await self.bot_print("Sorry, you do not have permission to run this command.")

    @commands.command(name="credits")
    async def cmd_credits(self, ctx: commands.Context):
        """Show MovieVox/TriviaVox credits"""

        await self.bot_print("MovieVox by LeftFourDave. Built using Python, Pygame, and TwitchIO. https://ko-fi.com/leftfourdave")

    @commands.command(name="gems", aliases=['Gems', 'GEMS'])
    async def cmd_gems(self, ctx: commands.Context):
        username = ctx.author.name
        if ctx.author.display_name:
            username = ctx.author.display_name
        gems = int(botgems.get_gems(username))
        parts = ctx.message.content.strip().split(" ")
        if len(parts) > 1:
            if parts[1].lower().strip() == "redeem":
                now_mins = int(datetime.strftime(datetime.now(), "%M"))
                if self.trivia_question is not None:
                    await self.bot_print("{}, please wait until trivia is over before redeeming.".format(username))
                elif (now_mins + 1) % 5 == 0:
                    await self.bot_print("{}, it's too close to trivia time. Please wait another minute before redeeming.".format(username))
                elif gems >= botgems.GEM_REDEEM:
                    # Run a trivia question for the user
                    trivia_q = random.choice(self.trivia_questions)
                    self.personal_trivia[username] = trivia_q
                    await self.bot_print(trivia_q.question)
            else:
                await self.bot_print("Usage: !gems [redeem] (need {}{} to redeem)"
                                     .format(str(botgems.GEM_REDEEM), botgems.GEM))
        else:
            await self.bot_print("@{}, you have {}{}.".format(username, str(gems), botgems.GEM))

    @commands.command(name="latency", aliases=['Latency', 'LATENCY'])
    async def cmd_latency(self, ctx: commands.Context):
        """Show a message about Twitch latency"""

        output = ("Make sure you are watching on Source mode to have the least amount "
                  "of latency between what is on screen and what is in chat. Click the gear on the "
                  "video and under Settings, choose 'Source'. Also, under the 'Advanced' setting make sure 'Low Latency' is on.")
        await self.bot_print(output)

    @commands.command(name="rank", aliases=['Rank', 'RANK', 'points', 'Points', 'POINTS', "triviarank", "triviapoints"])
    async def cmd_rank(self, ctx: commands.Context):
        """Show all trivia player's points and rank"""
        name = ctx.author.name.lower()
        parts = ctx.message.content.split(" ")
        if len(parts) > 1:
            name = parts[1].lower()

        points = bottrivia.get_trivia_points(name)
        rank = bottrivia.rank(name)
        num_users = len(bottrivia.load_sorted_list())
        point_word = "point" if points == 1 else "points"
        output = "{} has {} trivia {} and is rank {} of {}.".format(name, points, point_word, rank, num_users)
        await self.bot_print(output)

    @commands.command(name="top", aliases=['Top', 'TOP', 'triviatop'])
    async def cmd_top(self, ctx: commands.Context):
        """Show the trivia players with the highest scores"""
        parts = ctx.message.content.split()
        if len(parts) > 1:
            await self.bot_print(bottrivia.format_winners(bottrivia.top(parts[1])))
        else:
            await self.bot_print(bottrivia.format_winners(bottrivia.top()))

    def fix_emoji(self):
        # Cover missing emoji with images of the emoji
        if "🥷🥷" in self.trivia_question.question:
            alt_screen.blit(EMJ_NINJA, (470, 263))
            alt_screen.blit(EMJ_NINJA, (510, 263))
        elif "🥷" in self.trivia_question.question:
            alt_screen.blit(EMJ_NINJA, (488, 263))
        if "🫠" in self.trivia_question.question:
            alt_screen.blit(EMJ_MELT_FACE, (459, 270))
        if "♞" in self.trivia_question.question:
            alt_screen.blit(EMJ_BKNIGHT, (510, 270))
            alt_screen.blit(EMJ_BKNIGHT, (550, 270))
        if "🗚" in self.trivia_question.question:
            alt_screen.blit(EMJ_INCREASE, (488, 270))
        if "🇨🇺" in self.trivia_question.question:
            alt_screen.blit(EMJ_CUBA, (530, 270))
        if "🇲🇽" in self.trivia_question.question:
            alt_screen.blit(EMJ_MEXICO, (463, 270))
        if "🇲🇹" in self.trivia_question.question:
            alt_screen.blit(EMJ_MALTA, (522, 270))
        if "🇺🇸" in self.trivia_question.question:
            alt_screen.blit(EMJ_USA, (500, 270))

    def draw_screen(self):
        if self.trivia_question is not None:
            gradient.rect_gradient_h(alt_screen, DK_GRAY, BLACK, pygame.Rect(0, 0, W2, H2))

            if self.game_type == GameType.STINGER:
                alt_screen.blit(TXT_STINGER, ((W2 - TXT_STINGER.get_width()) // 2, 10))
                alt_screen.blit(self.stinger_img, ((W2 - self.stinger_img.get_width()) // 2,
                                                   (H2 - self.stinger_img.get_height()) // 2))

            elif self.game_type == GameType.TRIVIA:
                ques = wrap_text(self.trivia_question.question).strip().split("\n")
                text_height = (H2 - (36 * len(ques))) // 2
                for i, q in enumerate(ques):
                    txt = FONT_MST3K_LG.render(q, True, YELLOW)
                    alt_screen.blit(txt, (50, text_height + (36 * i)))

            elif self.game_type == GameType.EMOJI:
                alt_screen.blit(TXT_EMOJI, ((W2 - TXT_EMOJI.get_width()) // 2, H2 // 2 - 70))
                ques = re.sub("[🥷🫠♞🗚🇲🇽🇺🇸🇨🇺🇲🇹]", "   ", self.trivia_question.question.split(":")[1])
                txt = FONT_EMOJI_LG.render(ques, True, WHITE)
                alt_screen.blit(txt, ((W2 - txt.get_width()) // 2, H2 // 2))
                self.fix_emoji()

            elif self.game_type == GameType.CHARACTER:
                alt_screen.blit(TXT_CHARACTER, ((W2 - TXT_CHARACTER.get_width()) // 2, 10))
                alt_screen.blit(self.character_img, ((W2 - self.character_img.get_width()) // 2,
                                                     (H2 - self.character_img.get_height()) // 2))

            elif self.game_type == GameType.SCRAMBLE:
                alt_screen.blit(botscramble.draw(alt_screen, self.trivia_question.question), (0, 0))

        # Blit the internal alt_screen (Surface) on the main screen
        self.screen.blit(alt_screen, (WIDTH // 2, 0))

    def game_loop(self):
        global is_running, dt

        if is_running:
            self.screen.fill(BLACK)
            self.draw_screen()

            scroller.draw_image(self.screen)
            scroller.draw_year(self.screen)
            if self.trivia_question is None:
                scroller.draw_summary(self.screen)
            scroller.draw_urls(self.screen)

            # animate fun objects
            if len(scroller.fun_objs) > 0:
                for o in scroller.fun_objs:
                    o.animate()

            # Snowy movies: 321=Santa vs Martians, 422=Day Earth Froze, 521=Santa Claus,
            # 813=Jack Frost, 1104=Avalanche, 1113=Xmas That Almost Wasn't
            now_mm = int(datetime.strftime(datetime.now(), "%M"))
            if now_mm in [0, 1, 15, 16, 30, 31, 45, 46]:
                if len(scroller.snow_flakes) == 0:
                    for _ in range(scroller.NUM_SNOWFLAKES):
                        if scroller.sched[0]['epnum'] in ['321', '422', '521', '813', '1104', '1113']:
                            scroller.snow_flakes.append(SnowFlake(self.screen))
                        elif DATE_YYYY == VALENTINES_DAY:
                            scroller.snow_flakes.append(CandyHeartSnow(self.screen))
                        elif DATE_YYYY == ST_PATRICKS_DAY:
                            scroller.snow_flakes.append(CloverSnow(self.screen))

                elif scroller.sched[0]['epnum'] == '501':
                    if len(scroller.snow_flakes) == 0:
                        for _ in range(scroller.NUM_SNOWFLAKES):
                            scroller.snow_flakes.append(CandyHeartSnow(self.screen))
                    scroller.snow(self.screen)

                scroller.snow(self.screen)
            else:
                scroller.snow_flakes.clear()

            scroller.move_schedule(self.screen)
            scroller.draw_schedule_header(self.screen)
            scroller.draw_vertical_separators(self.screen)
            scroller.draw_clock(self.screen)

            if int(scroller.timer_tick) % 60 == 0 and not scroller.is_loading_fun:
                scroller.is_loading_fun = True
                scroller.fun_objs = funfactory.get(self.screen, scroller.sched[0]['title'], scroller.sched[0]['epnum'])

            if int(scroller.timer_tick) % 60 == 1 and scroller.is_loading_fun:
                scroller.is_loading_fun = False

            if len(scroller.fun_objs) > 0 and not scroller.is_loading_fun:
                temp_objs = []
                for obj in scroller.fun_objs:
                    if obj.anim_step > 0:
                        temp_objs.append(obj)
                scroller.fun_objs = temp_objs

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

            pygame.display.flip()
            dt = clk.tick(FPS)
            scroller.timer_tick += dt / 1000
            if scroller.timer_tick >= 7200:  # Reset every two hours
                scroller.timer_tick = 0


def choose_stinger() -> str:
    """Choose a stinger image"""
    file_list = [f for f in listdir(STINGER_PATH) if isfile(join(STINGER_PATH, f))]
    return random.choice(file_list)


def load_scaled_image(file_path) -> pygame.Surface:
    """Load the image given at 'file_path' and scale it to height so it fits the screen"""
    img = pygame.image.load(file_path)
    if img.get_width() < 1600:
        new_w = 580 / img.get_width()
        new_h = 440 / img.get_height()
    else:
        new_w = 580 / img.get_width()
        new_h = 325 / img.get_height()

    return pygame.transform.smoothscale_by(img, min(new_w, new_h)).convert_alpha()


if __name__ == '__main__':
    if platform.system().lower() == "windows":
        IS_DEBUG = True

    scroller.setup(scr)

    token = botsecrets.OAUTH_TOKEN
    if not IS_DEBUG:
        token = bottoken.refresh_token()

    try:
        bot = TriviaVox(scr, clk, token)
        bot.run()
    except AttributeError:
        print("Could not start bot.")

"""
TODO:
Add color to console output (sty)
Check the date around midnight to see if special colors apply (Valentine's Day, St Patrick's Day, etc)

Troublesome emoji:
[1]    102 - Robot vs Aztec Mummy (Mexico flag) [1]            🤖🆚🇲🇽⚰️🧟‍♂️
[36]   322 - Master Ninja I (ninja) [36]                       👨‍🏫🥷
[38]   324 - Master Ninja II (ninja twice) [38]                👨‍🏫🥷🥷
[76]   602 - Invasion USA (USA flag) [76]                      ⚔️➡️🇺🇸🗽
[90]   619 - Red Zone Cuba (Cuba flag) [90]                    🟥🚧🇨🇺
[96]   704 - Incredible Melting Man (melting face) [96]        😲🫠👨
[133] 1008 - Final Justice (Malta flag) [133]                  ⏮️⚖️🇲🇹

# Test these:
[53]  👨➕🤖=♾️👨 420 - Human Duplicators (verify the equal sign)    
[82]  ⚔️📅❌12
[89]  📈🏫🗚💉
[110] ⚔️➡️♆👨👨
[125] 📜🔺♞♞
[142] 👀✖️500,000

# Longest emoji question:
[11] Untamed Youth: 👮🏊‍♀️🏊‍♀️⏩👩‍⚖️⚖️⏩🌾🌾🚜⏩🎥💃🏼🎵📺👱‍♀️
"""
