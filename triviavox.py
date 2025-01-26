import asyncio
from datetime import datetime
import platform
import random
import re
import time
from enum import Enum
from os import listdir
from os.path import isfile, join

from twitchio import Message, Channel
from twitchio.ext import commands, routines

import botemoji
import botsecrets
import bottrivia
import funfactory
import gradient
import scroller
from anims.candy_heart_snow import CandyHeartSnow
from anims.clover_snow import CloverSnow
from anims.snow import SnowFlake
from colors import *
from constants import *
from movie_names import MOVIE_NAMES
from util_text import wrap_text

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

# Draw the games onto this smaller Surface and blit them to the main screen Surface
alt_screen = pygame.Surface((W2, H2))

STINGER_PATH = "images/stingers"

FONT_MD = pygame.font.Font("fonts/Inter.ttf", 16)
FONT_LG = pygame.font.Font("fonts/Inter.ttf", 30)
FONT_XL = pygame.font.Font("fonts/Inter.ttf", 48)

# Font used in Overdrawn at the Memory Bank
FONT_FINGAL_MD = pygame.font.Font("fonts/HandelGo.ttf", 16)
FONT_FINGAL_LG = pygame.font.Font("fonts/HandelGo.ttf", 30)
FONT_FINGAL_XL = pygame.font.Font("fonts/HandelGo.ttf", 48)

# Font used in modern MST3K stuff
FONT_MST3K_MD = pygame.font.Font("fonts/SimianText_Orangutan.otf", 20)
FONT_MST3K_LG = pygame.font.Font("fonts/SimianText_Orangutan.otf", 36)
FONT_MST3K_XL = pygame.font.Font("fonts/SimianText_Orangutan.otf", 52)

# Font used to render emoji
FONT_EMOJI_LG = pygame.font.Font("fonts/seguiemj.ttf", 44)

STR_STINGER = "Name the MST3K movie this stinger is from:"
TXT_STINGER = FONT_MST3K_LG.render(STR_STINGER, True, YELLOW)

STR_EMOJI = "Name the MST3K movie described by these emoji:"
TXT_EMOJI = FONT_MST3K_LG.render(STR_EMOJI, True, YELLOW)

is_running = True
dt = 0


class GameType(Enum):
    TRIVIA = "Trivia"
    EMOJI = "Emoji"
    STINGER = "Stinger"


class TriviaVox(commands.Bot):
    def __init__(self, screen, clock):
        super().__init__(token=botsecrets.OAUTH_TOKEN, initial_channels=[CHANNEL_NAME], prefix="!")
        # if IS_DEBUG:
        #     super().__init__(token=botsecrets.OAUTH_TOKEN, initial_channels=[CHANNEL_NAME], prefix="!")
        # else:
        #     super().__init__(token=botsecrets.ACCESS_TOKEN, initial_channels=[CHANNEL_NAME], prefix="!")
        self.screen = screen
        self.clock = clock

        self.channel = super().get_channel(CHANNEL_NAME)
        self.is_connecting = True
        self.is_live = True
        self.next_ad_at = 0
        self.start_trivia_time = 0

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

    async def check_if_live(self):
        streams = await self.fetch_streams(user_ids=[CHANNEL_ID])
        self.is_live = len(streams) > 0

    async def bot_print(self, txt):
        print(txt)
        if not IS_DEBUG and self.channel is not None:
            await self.channel.send(txt)

    async def event_ready(self):
        await self.check_if_live()

        self.channel = super().get_channel(CHANNEL_NAME)

        bottrivia.update()
        self.trivia_questions = bottrivia.load_as_array()

        botemoji.update()
        self.emoji_questions = botemoji.load_as_array()

        # 7:45pm is 1737852300
        # 7:50pm is 1737852600
        # 7:55pm is 1737852900
        # 8:00pm is 1737853200
        # 8:15pm is 1737854100
        # 8:20pm is 1737854400 / 300 = 5,792,848
        # 8:30pm is 1737855000 / 300 = 5,792,850
        ts = int(datetime.now().timestamp())
        for i in range(300):
            if (ts + i) % 300 == 0:
                self.start_trivia_time = ts + i
                break
        print("Start trivia at " + str(self.start_trivia_time))
        print(datetime.fromtimestamp(self.start_trivia_time))

        # self.auto_ad_update.start()
        # self.auto_trivia_scheduler.start()
        self.auto_trivia.start()
        self.auto_trivia_stop.start()
        self.auto_message.start()
        self.auto_update_game.start()

        print("TriviaVox ready, channel is live={}".format(self.is_live))

    async def event_message(self, message: Message) -> None:
        if message.echo:
            return

        if self.trivia_question is not None:
            guess = normalize_answers([message.content])[0]
            if guess in self.trivia_question.answers:
                self.trivia_winners.append(message.author.display_name)

                # Only start the timer after the first winner is detected.
                if len(self.trivia_winners) == 1:
                    await asyncio.sleep(12)
                    await self.stop_trivia()

        await self.handle_commands(message)

    async def event_command_error(self, ctx: commands.Context, error):
        """Ignore command errors"""
        pass

    async def event_raw_usernotice(self, channel: Channel, tags: dict):
        msg_id = tags['msg-id'].strip().lower()
        if msg_id in ["sub", "resub", "subgift", "submysterygift", "giftpaidupgrade", "rewardgift", "anongiftpaidupgrade"]:
            await self.bot_print("Thank you for supporting the channel, {}!".format(tags["display-name"]))

    @routines.routine(minutes=10)
    async def auto_ad_update(self):
        if not IS_DEBUG:
            user = await self.channel.user()
            ad_sched = await user.fetch_ad_schedule(botsecrets.ACCESS_TOKEN)
            ad_date = datetime.fromtimestamp(ad_sched.next_ad_at)
            print("Ads scheduled to run at {}".format(ad_date))
            self.next_ad_at = ad_sched.next_ad_at

    @routines.routine(seconds=1)
    async def auto_trivia_scheduler(self):
        if int(datetime.now().timestamp()) == self.start_trivia_time:
            self.auto_trivia.start()
            self.auto_trivia_scheduler.stop()

    @routines.routine(minutes=5)
    async def auto_trivia(self):
        """Run a trivia question every few minutes."""
        print("Starting trivia now")
        # Choose a game type
        await self.check_if_live()
        ts = int(datetime.now().timestamp())

        # If ads are running in the next 5 minutes (300 seconds), don't start a Stinger game
        # if self.is_live and self.next_ad_at - ts > 300:
        if self.is_live:
            self.game_type = random.choice([GameType.TRIVIA, GameType.EMOJI, GameType.STINGER])
        else:
            print("Not choosing a Stinger because of the time.")
            self.game_type = random.choice([GameType.TRIVIA, GameType.EMOJI])

        if self.game_type == GameType.TRIVIA:
            self.trivia_question = random.choice(self.trivia_questions)
            while self.trivia_question in self.prev_trivia:
                self.trivia_question = random.choice(self.trivia_questions)

            self.preserved_answer = self.trivia_question.answers[0]
            self.trivia_question.answers = normalize_answers(self.trivia_question.answers)
            self.prev_trivia.append(self.trivia_question)
            if len(self.prev_trivia) > 20:
                self.prev_trivia.pop(0)
            self.trivia_winners.clear()
            self.game_end_time = time.time() + 60

            await self.bot_print("/me Trivia Time! Q: {}".format(self.trivia_question.question))

        elif self.game_type == GameType.EMOJI:
            self.trivia_question = random.choice(self.emoji_questions)
            while self.trivia_question in self.prev_emoji:
                self.trivia_question = random.choice(self.emoji_questions)

            self.preserved_answer = self.trivia_question.answers[0]
            self.trivia_question.answers = normalize_answers(self.trivia_question.answers)
            self.prev_trivia.append(self.trivia_question)
            if len(self.prev_emoji) > 20:
                self.prev_emoji.pop(0)
            self.trivia_winners.clear()
            self.game_end_time = time.time() + 60

            await self.bot_print("/me Emoji Time! Q: {}".format(self.trivia_question.question))

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
            self.trivia_question.answers = normalize_answers(self.trivia_question.answers)
            self.prev_stingers.append(stinger_num)
            if len(self.prev_stingers) > 20:
                self.prev_stingers.pop(0)
            self.trivia_winners.clear()
            self.game_end_time = time.time() + 60

            await self.bot_print("/me Name the stinger seen on screen.")
            self.stinger_img = load_stinger_image(STINGER_PATH + '/' + stinger_file)

        print(self.trivia_question.answers)

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

    @routines.routine(minutes=15)
    async def auto_message(self):
        output = ("MST3K trivia every 5 minutes. " 
                  "Watch on 'Source' mode to reduce latency between screen and chat (!latency for more).")
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
            self.trivia_winners.clear()

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
                txt = FONT_EMOJI_LG.render(self.trivia_question.question.split(":")[1], True,
                                           pick_color(self.trivia_question.question))
                alt_screen.blit(txt, ((W2 - txt.get_width()) // 2, H2 // 2))

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
            scroller.draw_gizmoplex(self.screen)

            scroller.fun()
            # Snowy movies: 321=Santa vs Martians, 422=Day Earth Froze, 521=Santa Claus,
            # 813=Jack Frost, 1104=Avalanche, 1113=Xmas That Almost Wasn't
            now_mm = int(datetime.strftime(datetime.now(), "%M"))
            if 0 < now_mm < 2 or 15 < now_mm < 17 or 30 < now_mm < 36 or 45 < now_mm < 47:
                if scroller.sched[0]['epnum'] in ['321', '422', '521', '813', '1104', '1113']:
                    if len(scroller.snow_flakes) == 0:
                        for _ in range(scroller.NUM_SNOWFLAKES):
                            if DATE_YYYY == VALENTINES_DAY:
                                scroller.snow_flakes.append(CandyHeartSnow(self.screen))
                            elif DATE_YYYY == ST_PATRICKS_DAY:
                                scroller.snow_flakes.append(CloverSnow(self.screen))
                            else:
                                scroller.snow_flakes.append(SnowFlake(self.screen))
                    scroller.snow(self.screen)

                elif scroller.sched[0]['epnum'] == '501':
                    if len(scroller.snow_flakes) == 0:
                        for _ in range(scroller.NUM_SNOWFLAKES):
                            scroller.snow_flakes.append(CandyHeartSnow(self.screen))
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


def pick_color(question):
    color = WHITE
    if "🥷" in question:  # ninja
        color = BLACK
    elif "🫠" in question:  # melting face
        color = BLACK
    elif "♞" in question:
        color = DK_GRAY
    elif "🗚" in question:
        color = BLACK
    elif "🇨🇺" in question:
        color = BLACK
    elif "🇲🇽" in question:
        color = BLACK
    elif "🇲🇹" in question:
        color = BLACK
    elif "🇺🇸" in question:
        color = BLACK
    return color


def choose_stinger() -> str:
    """Choose a stinger image"""
    file_list = [f for f in listdir(STINGER_PATH) if isfile(join(STINGER_PATH, f))]
    return random.choice(file_list)


def load_stinger_image(file_path) -> pygame.Surface:
    img = pygame.image.load(file_path)

    # scale the image
    if img.get_width() < 1600:
        new_w = 580 / img.get_width()
        new_h = 440 / img.get_height()
    else:
        new_w = 580 / img.get_width()
        new_h = 325 / img.get_height()

    return pygame.transform.smoothscale_by(img, min(new_w, new_h)).convert()


def normalize_answers(answer_list):
    """Normalize the list of answers to help matching"""

    new_ans = []
    for ans in answer_list:
        # Convert to lower case and keep only alphanumerics and spaces
        a = re.sub(r"[^ a-zA-Z0-9]", "", ans.lower())

        # Remove articles (a, an, the)
        a = re.sub(r"\ba\b", "", a)
        a = re.sub(r"\ban\b", "", a)
        a = re.sub(r"\bthe\b", "", a)

        # Normalize "vs"
        a = re.sub(r"\bversus\b", "", a)
        a = re.sub(r"\bvs\b", "", a)
        a = re.sub(r"\bv\b", "", a)

        # Reduce multiple spaces to a single space
        a = re.sub(r"\s\s+", " ", a)
        new_ans.append(a.strip())
    return new_ans


if __name__ == '__main__':
    if platform.system().lower() == "windows":
        IS_DEBUG = True

    scr = pygame.display.set_mode((WIDTH, HEIGHT))
    clk = pygame.time.Clock()

    # Images used to fix missing emoji and flags (they need to be loaded after setting the screen mode)
    EMJ_NINJA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/ninja_1f977.png'), 0.115).convert_alpha()
    EMJ_MELT_FACE = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/melting-face_1fae0.png'), 0.11).convert_alpha()
    EMJ_BKNIGHT = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/black-knight-2692.png'), 0.4).convert_alpha()
    EMJ_INCREASE = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/increase-font-size-symbol_1f5da.png'), 0.375).convert_alpha()

    EMJ_CUBA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-cuba_1f1e8-1f1fa.png'), 0.11).convert_alpha()
    EMJ_MALTA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-malta_1f1f2-1f1f9.png'), 0.11).convert_alpha()
    EMJ_MEXICO = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-mexico_1f1f2-1f1fd.png'), 0.11).convert_alpha()
    EMJ_USA = pygame.transform.smoothscale_by(pygame.image.load('images/emoji/flag-united-states_1f1fa-1f1f8.png'), 0.10).convert_alpha()

    # summaries.refresh()
    scroller.setup(scr)

    bot = TriviaVox(scr, clk)
    bot.run()

"""
TODO:
Can the trivia run at certain minutes of the hour?
:00, :05, :10, ..., :45, :50, :55

Troublesome emoji:
[1]    102 - Robot vs Aztec Mummy (Mexico flag) [1]            🤖🆚🇲🇽⚰️🧟‍♂️
[36]   322 - Master Ninja I (ninja) [36]                       👨‍🏫🥷
[38]   324 - Master Ninja II (ninja twice) [38]                👨‍🏫🥷🥷
[76]   602 - Invasion USA (USA flag) [76]                      ⚔️➡️🇺🇸🗽
[90]   619 - Red Zone Cuba (Cuba flag) [90]                    🟥🚧🇨🇺
[96]   704 - Incredible Melting Man (melting face) [96]        😲🫠👨
[133] 1008 - Final Justice (Malta flag) [133]                 ⏮️⚖️🇲🇹

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
