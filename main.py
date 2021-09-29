import scrambler
from solver import solvers
import os
from keep_alive import keep_alive
import discord
from discord.ext import tasks, commands
import urllib.request
import html2text
import traceback
from log import log
from time import perf_counter
import math
import random
import numpy as np
import cv2
import sys
import requests
import re
import regex
import bot as bot_helper
import time_format
import move
import helper.serialize as serialize
import helper.discord as dh
import permissions
import config.channels
import config.emoji
import config.roles
from animate import make_video
from puzzle_state import PuzzleState
from algorithm import Algorithm
from analyse import analyse
from draw_state import draw_state
from fmc.fmc import FMC
from movesgame.movesgame import MovesGame
from movesgame.tournament import MovesGameTournament
from random_game import RandomGame
from probability import comparison, distributions
from probability.format import format_prob
from leaderboard import update as lb
from leaderboard import commands as lb_commands
from leaderboard import link
from replit import db

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

#_________________________probably for !paint
def apply_brightness_contrast(input_img, brightness=0, contrast=0):
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf

def convertRgbToWeight(rgbArray):
    arrayWithPixelWeight = []
    for i in range(int(rgbArray.size / rgbArray[0].size)):
        for j in range(int(rgbArray[0].size / 3)):
            lum = 255 - (
                int(rgbArray[i][j][0])
                + int(rgbArray[i][j][1])
                + int(rgbArray[i][j][2]) / 3
            )  # Reversed luminosity
            arrayWithPixelWeight.append(lum / 255)  # Map values from range 0-255 to 0-1
    return arrayWithPixelWeight

#____________________________discord started
@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
    log.info(f"Running version {bot_helper.git_info}")

    # check for message to send after a restart/update
    if "restart/channel_id" in db.keys() and "restart/message" in db.keys():
        channel_id = db["restart/channel_id"]
        channel = bot.get_channel(channel_id)
        message = db["restart/message"]
        await channel.send(message)
        del db["restart/channel_id"]
        del db["restart/message"]

    # create fmc
    global daily_fmc, short_fmc
    daily_fmc = FMC(bot, config.channels.daily_fmc, 86400, config.channels.daily_fmc_results, config.roles.fmc, [23*3600], ["One hour remaining!"])
    short_fmc = FMC(bot, config.channels.ten_minute_fmc, 600, warnings=[60*5, 60*9], warning_messages=["5 minutes remaining!", "One minute remaining!"])
    await daily_fmc.start()

    # dict of fmc objects by id
    global fmcs
    fmcs = {x.channel.id : x for x in [daily_fmc, short_fmc]}

    # create movesgame
    global movesgame, movesgame_tournament
    movesgame = MovesGame(bot, config.channels.movesgame)
    movesgame_tournament = MovesGameTournament(bot, config.channels.movesgame_tournament)

    # create random game
    global random_game
    random_game = RandomGame(bot, config.channels.random_game, 181440)
    random_game.start()

@bot.listen()
async def on_message(message):
    if message.author.bot:
        return

    if "pls" in message.content.lower():
        await message.add_reaction("eff:803888415858098217")
    if bot.user in message.mentions:
        await message.channel.send("You are egg, " + message.author.mention)
    if "fuck you" in message.content.lower():
        await message.channel.send("no u, " + message.author.mention)
    if "scrable" in message.content.lower():
        await message.channel.send("Infinity tps, " + message.author.mention + "?")
        await message.add_reaction("0️⃣")
    if "egg" in message.content.lower():
        if random.randint(1, 100) == 1:
            if random.randint(1, 25) == 1:
                await message.channel.send("Eggggggggggggggggggg!")
                await message.add_reaction("🥚")
                for id in config.emoji.eggs:
                    await message.add_reaction(bot.get_emoji(id))
            else:
                await message.channel.send("Egg!")
                await message.add_reaction("🥚")
                for id in config.emoji.eggs[:3]:
                    await message.add_reaction(bot.get_emoji(id))

    # find the first line of the message containing a command
    lines = message.content.split("\n")
    command_lines = [line.strip() for line in lines if line.startswith("!")]
    if len(command_lines) == 0:
        return
    command = command_lines[0]

    log.info(f"found command from user {message.author}")
    log.info(f"command: {command}")

    if command.startswith("!spam"):
        if message.author.guild_permissions.administrator:
            shit = command[6:]
            msg = ""
            for x in range(3000):
                msg += shit + " "
            spam.start(message.channel, msg[:2000])
    elif command.startswith("!fmc"):
        if message.channel.id not in fmcs:
            return
        fmc = fmcs[message.channel.id]
        if not fmc.round.running():
            return
        msg  = f"Current FMC scramble: {fmc.round.get_scramble()}\n"
        msg += f"Optimal solution length: {len(fmc.round.get_solution())}\n"
        msg += "Time remaining: " + time_format.format_long(fmc.round.remaining())
        await message.channel.send(msg)
    elif command.startswith("!submit"):
        if message.channel.id not in fmcs:
            return
        fmc = fmcs[message.channel.id]
        if not fmc.round.running():
            return
        try:
            await message.delete()

            # !submit [solution, optionally spoilered]
            solution_reg = regex.optionally_spoilered(regex.algorithm("solution"))
            reg = re.compile(f"!submit\s+{solution_reg}")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to read solution")

            groups = match.groupdict()

            solution = Algorithm(groups["solution"])
            await fmc.submit(message.author, solution)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!results"):
        # fmc results
        if message.channel.id in fmcs:
            fmc = fmcs[message.channel.id]
            if not fmc.round.running():
                return
            results = fmc.round.results()
            if len(results) == 0:
                msg = "No results yet"
            else:
                msg = ""
                for (id, result) in results.items():
                    user = bot.get_user(id)
                    msg += f"{user.name}: {len(result)}\n"
            await message.channel.send(msg)
        # movesgame results
        elif message.channel.id == movesgame.channel.id:
            results = movesgame.lifetime_results()
            ids = results.keys()

            # sort users by fraction of correct results
            fractions = {}
            for id in ids:
                good = results[id]["correct"]
                bad = results[id]["incorrect"]
                fractions[id] = good/(good+bad)
            sorted_ids = [x[0] for x in sorted(fractions.items(), key=lambda x: -x[1])]

            results_msg = ""
            provisional_msg = ""
            for id in sorted_ids:
                user = bot.get_user(id)
                good = results[id]["correct"]
                bad = results[id]["incorrect"]
                formatted = format(100*good/(good+bad), ".2f") + "%"

                # only show results for people with enough rounds
                if good+bad >= 30:
                    results_msg += f"{user.name}: {good}/{good+bad} = {formatted}\n"
                else:
                    provisional_msg += f"({user.name}: {good}/{good+bad} = {formatted})\n"

            await message.channel.send(results_msg + provisional_msg)
    elif command.startswith("!startfmc"):
        if message.channel.id != short_fmc.channel.id or short_fmc.round.running():
            return
        await short_fmc.start()
    elif command.startswith("!wrupdate"):
        url = os.environ["updateURL"]
        x = requests.get(url).text
        if x == "":
            x = "WRs updated\n" + \
                "WRs: http://slidysim.000webhostapp.com/leaderboard/records.html\n" + \
                "WRs (all): http://slidysim.000webhostapp.com/leaderboard/records_all.html\n" + \
                "WRs (moves): http://slidysim.000webhostapp.com/leaderboard/records_moves.html\n" + \
                "WRs (moves, all): http://slidysim.000webhostapp.com/leaderboard/records_all_moves.html"
        await message.channel.send(x)
    elif command.startswith("!update"):
        await message.channel.send("Wait for it!")
        try:
            lb.update()
            webpage = os.environ["webpage"]
            msg = f"Webpage updated!\n{webpage}"
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!stop"):
        if message.author.guild_permissions.administrator:
            spam.cancel()
    elif command.startswith("!getreal"):
        await message.channel.send("Generating scramble!")

        state = scrambler.getScramble(4)
        solution = solvers[4].solveOne(state)
        scramble = Algorithm("D3 R U2 R D2 R U3 L3") + solution.inverse()

        scrambleState = PuzzleState()
        scrambleState.reset(4, 4)
        scrambleState.apply(scramble)

        img = draw_state(scrambleState)
        msg = str(scrambleState) + "\n" + str(scramble)
        await dh.send_image(img, "scramble.png", msg, message.channel)
    elif command.startswith("!getscramble"):
        contentArray = command.lower().split(" ")
        n = 4
        if len(contentArray)>1:
            n = int(contentArray[1])
        scramble = scrambler.getScramble(n)
        if n == 4:
            img = draw_state(scramble)
            msg = f"Your random 4x4 scramble: \n{scramble}"
            await dh.send_image(img, "scramble.png", msg, message.channel)
        else:
            await message.channel.send(f"Random scramble for {n}x{n} puzzle\n{scramble}")
    elif command.startswith("!getwr"):
        try:
            fp = urllib.request.urlopen(
                "http://slidysim.000webhostapp.com/leaderboard/records_all.html"
            )
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            mystr = html2text.html2text(mystr)
            mystr = mystr.splitlines()
            fp.close()
            wrsize = command[7:] + " "
            matching = [s for s in mystr if wrsize in s]
            if len(matching) == 0:
                await message.channel.send(
                    "Sorry, i can't find anything :(\nTry this: http://bit.ly/wrspage"
                )
            else:
                out = matching[0]
                await message.channel.send(out)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!wrsby"):
        try:
            fp = urllib.request.urlopen(
                "http://slidysim.000webhostapp.com/leaderboard/records_all.html"
            )
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            mystr = html2text.html2text(mystr)
            alltext=mystr
            mystr = mystr.splitlines()
            fp.close()
            username = command[7:]
            matching = [s for s in mystr if username in s]
            my_string = "\n".join(matching)
            if len(matching) == 0:
                await message.channel.send(
                    "Sorry, i can't find anything :(\nTry this: http://bit.ly/wrspage"
                )
            else:
                if len(my_string) > 1950:
                    await dh.send_as_file(my_string, "wrsby.txt", "WR list:", message.channel)
                else:
                    await message.channel.send("```" + my_string + "```")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!analyse3x3"):
        try:
            if len(message.attachments) != 1:
                raise Exception("no attached file found")

            text = await message.attachments[0].read()
            text = text.decode()

            # each solve is given as [scramble (optional)] [solution]
            scr_reg = regex.puzzle_state("scramble")
            sol_reg = regex.algorithm("solution")
            reg = re.compile(f"({scr_reg}\s*)?{sol_reg}")

            # solve each scramble and tally up the results
            results = {}
            opt_total = 0
            user_total = 0
            n = 0
            for match in reg.finditer(text):
                n += 1

                groups = match.groupdict()

                solution = Algorithm(groups["solution"])
                if groups["scramble"] is not None:
                    scramble = PuzzleState(groups["scramble"])
                else:
                    scramble = PuzzleState()
                    scramble.reset(3)
                    scramble.apply(solution.inverse())

                opt_len = len(solvers[3].solveOne(scramble))
                user_len = len(solution)

                opt_total += opt_len
                user_total += user_len

                diff = user_len - opt_len
                if diff not in results:
                    results[diff] = 0
                results[diff] += 1

            # write message
            opt_str = format(opt_total/n, ".3f")
            user_str = format(user_total/n, ".3f")
            diff_str = format((user_total-opt_total)/n, ".3f")

            msg = f"Optimal mean of {n}: {opt_str}\n"
            msg += f"Your mean: {user_str} (+{diff_str})\n"
            msg += "\n".join([f"+{k}: {v}" for (k, v) in sorted(results.items())])

            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!getpb"):
        try:
            size_reg = regex.size("width", "height", "size")
            reg = re.compile(f"!getpb(\s+(?P<user>[A-Za-z0-9]+))?(\s+{size_reg})?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            # if no username parameter is given, look up the message author's linked username
            if groups["user"] is None:
                user = link.get_leaderboard_user(message.author.id)
            else:
                user = groups["user"]

            # if no size given, check if we're in an NxN channel. if not, default to 4x4
            if groups["size"] is None:
                channel_id = message.channel.id
                if channel_id in config.channels.nxn_channels:
                    width = height = config.channels.nxn_channels[channel_id]
                else:
                    width = height = 4
            else:
                width = int(groups["width"])
                if groups["height"] is None:
                    height = width
                else:
                    height = int(groups["height"])

            msg = lb_commands.get_pb(width, height, user)
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!getreq"):
        try:
            size_reg = regex.size("width", "height", "size")
            reg = re.compile(f"!getreq(\s+(?P<tier>[A-Za-z0-9]+))(\s+{size_reg})?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            tier = groups["tier"]

            # if no size given, check if we're in an NxN channel. if not, default to 4x4
            if groups["size"] is None:
                channel_id = message.channel.id
                if channel_id in config.channels.nxn_channels:
                    width = height = config.channels.nxn_channels[channel_id]
                else:
                    width = height = 4
            else:
                width = int(groups["width"])
                if groups["height"] is None:
                    height = width
                else:
                    height = int(groups["height"])

            msg = lb_commands.get_req(width, height, tier)
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!animate"):
        try:
            # !animate [optional scramble] [solution] [optional tps]
            scr_reg = regex.puzzle_state("scramble")
            mov_reg = regex.algorithm("moves")
            tps_reg = regex.positive_integer("tps")
            reg = re.compile(f"!animate\s*{scr_reg}?\s*{mov_reg}\s*{tps_reg}?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            # make sure the algorithm isn't too long
            moves = Algorithm(groups["moves"])
            num_moves = len(moves)
            max_moves = 150
            if num_moves > max_moves:
                raise ValueError(f"number of moves ({num_moves}) must be at most {max_moves}")

            # if no scramble given, use the inverse of the moves
            if groups["scramble"] is None:
                scramble = PuzzleState()
                scramble.reset(4, 4)
                scramble.apply(moves.inverse())
            else:
                scramble = PuzzleState(groups["scramble"])

            # if no tps given, use 8 as a default
            if groups["tps"] is None:
                tps = 8
            else:
                tps = int(groups["tps"])
            time = round(num_moves/tps, 3)

            await message.channel.send("Working on it! It may take some time, please wait")

            msg  = f"{scramble}\n"
            msg += f"{moves} [{num_moves}]\n"
            msg += f"TPS (playback): {tps}\n"
            msg += f"Time (playback): {time}"

            make_video(scramble, moves, tps)
            await dh.send_binary_file("movie.webm", msg, message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!analyse"):
        await message.channel.send("Working on it!")
        try:
            contentArray = command.split(" ")
            solution = Algorithm(contentArray[1])
            analysis = analyse(solution)

            scramble = PuzzleState()
            scramble.reset(4, 4)
            scramble.apply(solution.inverse())
            optSolution = solvers[4].solveOne(scramble)

            msg  = f"Scramble: {scramble}\n"
            msg += f"Your solution [{len(solution)}]: {solution}\n"
            msg += f"Optimal solution [{len(optSolution)}]: {optSolution}\n"
            msg += "Analysis:"

            await dh.send_as_file(analysis, "analysis.txt", msg, message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!draw"):
        try:
            state = PuzzleState(command[6:])
            if state.size() != (4, 4):
                raise ValueError(f"puzzle size {state.size()} must be 4x4")
            img = draw_state(state)
            await dh.send_image(img, "scramble.png", "Your scramble:", message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!getprob"):
        try:
            # !getprob [size: N or WxH] [mean/marathon length: optional] [moves: a-b or e.g. >=m, <m, =m, etc.] [repetitions: optional]
            size_reg = regex.size("width", "height")
            solve_type_reg = "(?P<solve_type>(mo)|x)"
            num_solves_reg = regex.positive_integer("num_solves")
            full_solve_type_reg = "(" + solve_type_reg + num_solves_reg + ")"
            pos_real_reg = regex.positive_real()
            interval_reg = f"((?P<moves_from>{pos_real_reg})-(?P<moves_to>{pos_real_reg}))"
            comparison_reg = f"((?P<comparison>[<>]?=?)(?P<moves>{pos_real_reg}))"
            reps_reg = regex.positive_integer("repetitions")
            reg = re.compile(f"!getprob(\s+{size_reg})(\s+{full_solve_type_reg})?(\s+(?P<range>{interval_reg}|{comparison_reg}))(\s+{reps_reg})?")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            # read the size
            w = int(groups["width"])
            if groups["height"] is None:
                h = w
            else:
                h = int(groups["height"])

            # read solve type and number of solves
            if groups["solve_type"] is None:
                solve_type = "single"
                num_solves = 1
            elif groups["solve_type"] == "mo":
                solve_type = "mean"
                num_solves = int(groups["num_solves"])
            else:
                solve_type = "marathon"
                num_solves = int(groups["num_solves"])

            # limit on the number of solves
            if num_solves > 1000:
                raise ValueError("number of solves must be at most 1000")

            # get the distribution for the number of solves we want
            dist = distributions.get_distribution(w, h).sum_distribution(num_solves)

            # check if range is given by interval or comparison, and calculate probability for one repetition
            multiplier = num_solves if solve_type == "mean" else 1
            if groups["comparison"] is None:
                start = round(multiplier * float(groups["moves_from"]))
                end = round(multiplier * float(groups["moves_to"]))
                prob_one = dist.prob_range(start, end)
            else:
                comp = comparison.from_string(groups["comparison"])
                moves = round(multiplier * float(groups["moves"]))
                prob_one = dist.prob(moves, comp)

            # number of repetitions
            if groups["repetitions"] is None:
                reps = 1
            else:
                reps = int(groups["repetitions"])

            # compute the probability of a scramble appearing at least once
            prob = 1 - (1 - prob_one)**reps

            # we rounded the range of moves, so we should display the rounded range instead of the original.
            # otherwise we would have messages like:
            # "Probability of 4x4 having an optimal solution of 52.1-52.9 moves is 14.80%"
            # even though we rounded 52.1 and 52.9 to 52 and 53.
            # if the endpoints of the rounded range are integers, make them integers, otherwise round to 3dp
            def make_str(a):
                if a % multiplier == 0:
                    return str(a // multiplier)
                return format(a/multiplier, ".3f")

            if groups["comparison"] is None:
                range_str = f"{make_str(start)}-{make_str(end)}"
            else:
                range_str = groups["comparison"] + make_str(moves)

            # write the message
            if solve_type == "single":
                msg = f"Probability of {w}x{h} having an optimal solution of {range_str} moves is {format_prob(prob_one)}\n"
                if reps > 1:
                    msg += f"Probability of at least one scramble out of {reps} within that range is {format_prob(prob)}"
            elif solve_type == "mean":
                msg = f"Probability of {w}x{h} mo{num_solves} having an optimal solution of {range_str} moves is {format_prob(prob_one)}\n"
                if reps > 1:
                    msg += f"Probability of at least one mean out of {reps} within that range is {format_prob(prob)}"
            elif solve_type == "marathon":
                msg = f"Probability of {w}x{h} x{num_solves} having an optimal solution of {range_str} moves is {format_prob(prob_one)}\n"
                if reps > 1:
                    msg += f"Probability of at least one marathon out of {reps} within that range is {format_prob(prob)}"

            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!paint"):
        good = False
        try:
            img_data = requests.get(message.attachments[0].url).content
            good = True
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"Please upload an image file!\n```\n{repr(e)}\n```")
        if good:
            contentArray = command.lower().split(" ")
            size = 50
            if len(contentArray) > 1:
                size = int(contentArray[1])
            with open("image_name.jpg", "wb") as handler:
                handler.write(img_data)
            my_img = cv2.imread("image_name.jpg")
            my_img = cv2.cvtColor(my_img, cv2.COLOR_BGR2GRAY)
            (thresh, my_img) = cv2.threshold(my_img, 100, 255, cv2.THRESH_BINARY)
            cv2.imwrite("image_name.jpg", my_img)
            with open("image_name.jpg", "rb") as f:
                picture = discord.File(f)
                await message.channel.send("Converted image: ", file=picture)
            my_img = cv2.imread("image_name.jpg")
            os.remove("image_name.jpg")
            h, w, a = my_img.shape
            desw = round(size / 2)
            bigger = max(w, h)
            if desw > 128:
                desw = 128
            ratio = 100 * (desw / bigger)
            scale_percent = ratio  # percent of original size
            w = math.ceil(w * scale_percent / 100)
            h = math.ceil(h * scale_percent / 100)
            dim = (w, h)
            bigger = max(w, h)
            puzzleSize = bigger * 2
            resized = cv2.resize(my_img, dim, interpolation=cv2.INTER_AREA)
            my_img = resized
            np.set_printoptions(threshold=sys.maxsize)
            convertedList = convertRgbToWeight(my_img)
            c = 0
            curline = 0
            curid = 0

            colors = np.zeros((h, w), dtype=int)
            for i in range(w * h):
                if convertedList[i] > 0.7:
                    colors[curline, curid] = 1
                curid = curid + 1
                if curid == w:
                    curid = 0
                    curline = curline + 1
            puzzle = np.zeros((puzzleSize, puzzleSize), dtype=int)
            c = 1
            for j in range(puzzleSize):
                for i in range(puzzleSize):
                    puzzle[j, i] = c
                    c = c + 1
            puzzle[puzzleSize - 1, puzzleSize - 1] = 0
            swaps = 0
            for i in range(h):
                for j in range(w):
                    if colors[i, j] == 1:
                        a, b = puzzle[i][j], puzzle[i + w][j]
                        puzzle[i][j], puzzle[i + w][j] = puzzle[i + w][j], puzzle[i][j]
                        if a != 0 and b != 0:
                            swaps = swaps + 1
                        a, b = puzzle[i][j + w], puzzle[i + w][j + w]
                        puzzle[i][j + w], puzzle[i + w][j + w] = (
                            puzzle[i + w][j + w],
                            puzzle[i][j + w],
                        )
                        if a != 0 and b != 0:
                            swaps = swaps + 1
            if (swaps % 2) != 0:
                a, b = (
                    puzzle[puzzleSize - 1][puzzleSize - 3],
                    puzzle[puzzleSize - 1][puzzleSize - 2],
                )
                (
                    puzzle[puzzleSize - 1][puzzleSize - 3],
                    puzzle[puzzleSize - 1][puzzleSize - 2],
                ) = (
                    puzzle[puzzleSize - 1][puzzleSize - 2],
                    puzzle[puzzleSize - 1][puzzleSize - 3],
                )
            mystr = ""
            for x in puzzle:
                for y in x:
                    mystr = mystr + str(y) + " "
                mystr = mystr[:-1]
                mystr = mystr + "/"
            mystr = mystr[:-1]
            s = str(puzzleSize)
            msg = "Your scramble is ({s}x{s} sliding puzzle)\n(download file if its large):"
            await dh.send_as_file(mystr, "scramble.txt", msg, message.channel)
    elif command.startswith("!rev"):
        alg = Algorithm(command[5:])
        alg.invert()
        await message.channel.send(str(alg))
    elif command.startswith("!not"):
        alg = Algorithm(command[5:])
        alg.invert().revert()
        await message.channel.send(str(alg))
    elif command.startswith("!tti"):
        try:
            words = command[5:]
            r = requests.post(
                "https://api.deepai.org/api/text2img",
                data={
                    "text": words,
                },
                headers={"api-key": os.environ["aikey"]},
            )
            r = r.json()
            # print(r)
            img_data = requests.get(r["output_url"]).content
            with open("img_lemon.jpg", "wb") as handler:
                handler.write(img_data)
            with open("img_lemon.jpg", "rb") as f:
                picture = discord.File(f)
                await message.channel.send("Your weird image: ", file=picture)
            os.remove("img_lemon.jpg")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!datecompare"):
        pass
    elif command.startswith("!movesgame"):
        if message.channel.id == movesgame.channel.id:
            await movesgame.start()
    elif command.startswith("!tournament"):
        if message.channel.id == movesgame_tournament.channel.id:
            await movesgame_tournament.run()
    elif command.startswith("!goodm"):
        try:
            scramble = PuzzleState(command[7:])
            size = scramble.size()

            # don't allow daily fmc scramble
            for fmc in fmcs.values():
                if fmc.round.running():
                    fmc_scramble = fmc.round.get_scramble()
                    if scramble == fmc_scramble:
                        name = message.author.name
                        await message.channel.send(f"No cheating, {name}!")
                        return

            if size == (3, 3) or size == (4, 4):
                solver = solvers[size[0]]
                good_moves = [move.to_string(sol.first()) for sol in solver.solveGood(scramble)]
                good_moves_str = ", ".join(good_moves)

                msg  = f"Scramble: {scramble}\n"
                msg += f"Good moves: {good_moves_str}"
                await message.channel.send(msg)
            else:
                raise ValueError(f"puzzle size {scramble.size()} must be 3x3 or 4x4")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!eggsolve"):
        scramble = PuzzleState(command[10:])
        size = scramble.size()

        # don't allow daily fmc scramble
        for fmc in fmcs.values():
            if fmc.round.running():
                fmc_scramble = fmc.round.get_scramble()
                if scramble == fmc_scramble:
                    name = message.author.name
                    await message.channel.send(f"No cheating, {name}!")
                    return

        if size == (3, 3) or size == (4, 4):
            try:
                a = perf_counter()
                solutions = solvers[size[0]].solveAll(scramble)
                b = perf_counter()

                string  = f"Time: {round(b - a, 3)}\n"
                string += f"Number of solutions: {len(solutions)}\n"
                string += f"Length: {len(solutions[0])}\n"
                string += "\n".join([str(s) for s in solutions])

                await dh.send_as_file(string, "solutions.txt", f"Scramble: {scramble}", message.channel)
            except Exception as e:
                traceback.print_exc()
                await message.channel.send(f"```\n{repr(e)}\n```")
        else:
            print(len(scramble))
            await message.channel.send("Your scramble is wrong.")
    elif command.startswith("!solve") or command.startswith("!video"):
        try:
            video = command.startswith("!video")

            scramble = PuzzleState(command[7:])
            size = scramble.size()

            # don't allow daily fmc scramble
            for fmc in fmcs.values():
                if fmc.round.running():
                    fmc_scramble = fmc.round.get_scramble()
                    if scramble == fmc_scramble:
                        name = message.author.name
                        await message.channel.send(f"No cheating, {name}!")
                        return

            if size != (3, 3) and size != (4, 4):
                raise ValueError(f"puzzle size {size} must be 3x3 or 4x4")
            if size == (3, 3) and video:
                raise ValueError(f"puzzle size {size} must be 4x4")

            a = perf_counter()
            solver = solvers[size[0]]
            solution = solver.solveOne(scramble)
            b = perf_counter()

            # solution of solved puzzle = egg
            solution_str = str(solution)
            if solution_str == "":
                solution_str = ":egg:"

            msg  = f"Scramble: {scramble}\n"
            msg += f"Solution [{len(solution)}]: ||{solution_str}||\n"
            msg += f"Time: {round((b - a), 3)}"

            if video:
                msg += "\nPlease wait! I'm making a video for you!"

            await message.channel.send(msg)

            if video:
                make_video(scramble, solution, 8)
                await dh.send_binary_file("movie.webm", "", message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!simplify"):
        try:
            alg = Algorithm(command[10:])
            old_len = len(alg)
            alg.simplify()
            new_len = len(alg)
            await message.channel.send(f"[{old_len} -> {new_len}] {alg}")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!solvable"):
        try:
            pos = PuzzleState(command[10:])
            if pos.solvable():
                msg = "solvable"
            else:
                msg = "unsolvable"
            await message.reply(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!8fmc"):
        try:
            if len(command) == 5:
                n = 100
            else:
                n = int(command[6:])
                n = max(1, min(1000, n))

            data = ""
            l = []
            for i in range(n):
                scramble = scrambler.getScramble(3)
                solution = solvers[3].solveOne(scramble)
                length = len(solution)

                l.append(length)
                data += f"{scramble}\t{length}\n"

            msg  = f"Average: {round(sum(l)/n, 3)}\n"
            msg += f"Longest: {max(l)}\n"
            msg += f"Shortest: {min(l)}"

            await dh.send_as_file(data, "8fmc.txt", msg, message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!rank"):
        try:
            user = command[6:]
            msg = lb_commands.rank(user)
            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command.startswith("!link"):
        if not permissions.is_egg_admin(message.author):
            return
        try:
            reg = re.compile(f"!link\s+(?P<user_id>[0-9]+)\s+(?P<lb_username>[a-zA-Z0-9]+)")
            match = reg.fullmatch(command)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            user_id = int(groups["user_id"])
            lb_username = groups["lb_username"]

            link.link(user_id, lb_username)
            await message.channel.send("Accounts linked")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif command == "!egg":
        with open("misc/egg.txt", "r") as f:
            egg = f.read()
        await message.channel.send("```" + egg + "```")
    elif command.startswith("!help"):
        await message.channel.send("Egg bot commands: https://github.com/benwh1/eggbot/blob/master/README.md")
    elif command.startswith("!git"):
        if permissions.is_egg_admin(message.author):
            await message.channel.send(bot_helper.git_info)
    elif command.startswith("!restart"):
        if permissions.is_egg_admin(message.author):
            await message.channel.send("Restarting...")
            db["restart/channel_id"] = message.channel.id
            db["restart/message"] = "Restarted"
            bot_helper.restart()
    elif command.startswith("!botupdate"):
        if permissions.is_egg_admin(message.author):
            await message.channel.send("Updating...")
            db["restart/channel_id"] = message.channel.id
            db["restart/message"] = "Updated!"
            bot_helper.update()
            bot_helper.restart()
    elif command.startswith("!dbdump"):
        if permissions.is_owner(message.author):
            my_db = {}
            for key in db.keys():
                my_db[key] = db[key]
            await dh.send_as_file(serialize.serialize(my_db), "db.txt", "", message.channel)

@tasks.loop(seconds=1)
async def spam(chan, msg):
    await chan.send(msg)

keep_alive()
bot.run(os.environ["token"])
