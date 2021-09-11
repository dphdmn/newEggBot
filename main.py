import scrambler
from solver import solvers
import os
from keep_alive import keep_alive
from prettytable import PrettyTable
import discord
from discord.ext import tasks
import urllib.request
import html2text
import traceback
import time
from time import perf_counter
import datetime
import math
from decimal import Decimal
import numpy as np
import cv2
import sys
import requests
import glob
import zlib
import re
import asyncio
import bot
import time_format
import move
from animate import make_video
from puzzle_state import PuzzleState
from algorithm import Algorithm
from analyse import analyse
from draw_state import draw_state
from daily_fmc import DailyFMC
from probability import comparison, distributions
from leaderboard import update as lb
from replit import db

client = discord.Client()

async def makeTmpSend(filename, filedata, messagewith, msgchn):
    f = open(filename, "w+")
    f.write(filedata)
    f.close()
    with open(filename, "rb") as f:
        myfile = discord.File(f)
        await msgchn.send(messagewith, file=myfile)
    os.remove(filename)

def readFilenormal(name):
    with open(name, "r") as file:
        mystr = file.read()
    return mystr

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

#_____________for !getpb - get date of the file
def mod_date(path_to_file):
    stat = os.stat(path_to_file)
    return datetime.datetime.fromtimestamp(stat.st_mtime)

#____________________________discord started
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

    #check for message to send after a restart/update
    if "restart/channel_id" in db.keys() and "restart/message" in db.keys():
        channel_id = db["restart/channel_id"]
        channel = client.get_channel(channel_id)
        message = db["restart/message"]
        await channel.send(message)
        del db["restart/channel_id"]
        del db["restart/message"]

    #start daily fmc
    global fmc
    fmc = DailyFMC(client, int(os.environ["daily_fmc_channel"]), int(os.environ["daily_fmc_results_channel"]))
    fmc.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if "pls" in message.content.lower():
        await message.add_reaction("eff:803888415858098217")
    if client.user in message.mentions:
        await message.channel.send("You are egg, " + message.author.mention)
    if "fuck you" in message.content.lower():
        await message.channel.send("no u, " + message.author.mention)
    if message.content.startswith("!spam"):
        if message.author.guild_permissions.administrator:
            shit = message.content[6:]
            msg = ""
            for x in range(3000):
                msg += shit + " "
            spam.start(message.channel, msg[:2000])
    if message.content.startswith("!fmc"):
        if message.channel.id != fmc.channel.id or fmc.status() == 0:
            return
        msg = "Current FMC scramble: " + fmc.scramble().to_string() + "\n"
        msg += "Optimal solution length: " + str(fmc.solution().length()) + "\n"
        msg += "Time remaining: " + time_format.format(fmc.remaining())
        await message.channel.send(msg)
    if message.content.startswith("!submit"):
        if message.channel.id != fmc.channel.id or fmc.status() == 0:
            return
        try:
            await message.delete()
            name = message.author.name
            solution = Algorithm(message.content[8:])
            await fmc.submit(name, solution)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!results"):
        if message.channel.id != fmc.channel.id or fmc.status() == 0:
            return
        results = fmc.results()
        if len(results) == 0:
            msg = "No results yet"
        else:
            msg = ""
            for (name, result) in results.items():
                msg += f"{name}: {result.length()}\n"
        await message.channel.send(msg)
    if message.content.startswith("!wrupdate"):
        url = os.environ["updateURL"]
        x = requests.get(url).text
        if x == "":
            x = "WRs updated\n" + \
                "WRs: http://slidysim.000webhostapp.com/leaderboard/records.html\n" + \
                "WRs (all): http://slidysim.000webhostapp.com/leaderboard/records_all.html\n" + \
                "WRs (moves): http://slidysim.000webhostapp.com/leaderboard/records_moves.html\n" + \
                "WRs (moves, all): http://slidysim.000webhostapp.com/leaderboard/records_all_moves.html"
        await message.channel.send(x)
    if message.content.startswith("!update"):
        await message.channel.send("Wait for it!")
        try:
            lb.update()
            webpage = os.environ["webpage"]
            msg = f"Webpage updated!\n{webpage}"
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!stop"):
        if message.author.guild_permissions.administrator:
            spam.cancel()
    if message.content.startswith("!getreal"):
        await message.channel.send("Generating scramble!")

        state = scrambler.getScramble(4)
        solution = solvers[4].solveOne(state)
        scramble = Algorithm("D3 R U2 R D2 R U3 L3") + solution.inverse()

        scrambleState = PuzzleState()
        scrambleState.reset(4, 4)
        scrambleState.apply(scramble)

        img = draw_state(scrambleState)
        img.save('scramble.png', 'PNG')
        with open("scramble.png", "rb") as f:
            picture = discord.File(f)
            await message.channel.send(scrambleState.to_string() + "\n" + scramble.to_string(), file=picture)
        os.remove("scramble.png")
    if message.content.startswith("!getscramble"):
        contentArray = message.content.lower().split(" ")
        n = 4
        if len(contentArray)>1:
            n = int(contentArray[1])
        scramble = scrambler.getScramble(n)
        if n == 4:
            img = draw_state(scramble)
            img.save('scramble.png', 'PNG')
            with open("scramble.png", "rb") as f:
                picture = discord.File(f)
                await message.channel.send("Your random 4x4 scramble: \n" + scramble.to_string(), file=picture)
            os.remove("scramble.png")
        else:
            await message.channel.send("Random scramble for " + str(n) + "x" + str(n) + " puzzle\n" + scramble.to_string())
    if message.content.startswith("!getwr"):
        try:
            fp = urllib.request.urlopen(
                "http://slidysim.000webhostapp.com/leaderboard/records_all.html"
            )
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            mystr = html2text.html2text(mystr)
            mystr = mystr.splitlines()
            fp.close()
            wrsize = message.content[7:] + " "
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
    if message.content.startswith("!wrsby"):
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
            username = message.content[7:]
            matching = [s for s in mystr if username in s]
            my_string = "\n".join(matching)
            if len(matching) == 0:
                await message.channel.send(
                    "Sorry, i can't find anything :(\nTry this: http://bit.ly/wrspage"
                )
            else:
                if len(my_string) > 1950:
                    f = open("wrsby.txt", "w+")
                    f.write(my_string)
                    f.close()
                    with open("wrsby.txt", "rb") as f:
                        txt = discord.File(f)
                        await message.channel.send("WR list: ", file=txt)
                    os.remove("wrsby.txt")
                else:
                    await message.channel.send("```" + my_string + "```")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!getpb"):
        mystr=db["leaderboard.txt"].lower()
        # print(mystr)
        mystr = mystr.splitlines()
        contentArray = message.content.lower().split(" ")
        # print(contentArray)
        username = contentArray[1]
        matching = [s for s in mystr if username in s]
        my_string = matching[0]
        my_string = my_string.split("\t")

        # print(my_string)
        bad = False
        try:
            for i in range(1, len(my_string)):
                try:
                    number = float(my_string[i])
                    intpart = int(math.floor(number))
                    decimals = round(number - intpart, 3)
                    x = str(datetime.timedelta(seconds=intpart)) + str(decimals)[1:]
                except:
                    x = ""
                if x != "":
                    if int(intpart) > 60:
                        my_string[i] = my_string[i] + " (" + x[2:] + ")"
            puzzle = contentArray[2]
            outputString = "PBs for user **" + my_string[0] + "** at the puzzle "
            if puzzle == "3" or puzzle == "3x3":
                outputString += "3x3\n```"
                outputString += "ao5: " + my_string[1] + "\n"
                outputString += "ao12: " + my_string[2] + "\n"
                outputString += "ao50: " + my_string[3] + "\n"
                outputString += "ao100: " + my_string[4] + "\n"
                outputString += "x10 marathon: " + my_string[5] + "\n"
                outputString += "x42 marathon: " + my_string[6] + "\n```"
            elif puzzle == "4" or puzzle == "4x4":
                outputString += "4x4\n```"
                outputString += "single: " + my_string[7] + "\n"
                outputString += "ao5: " + my_string[8] + "\n"
                outputString += "ao12: " + my_string[9] + "\n"
                outputString += "ao50: " + my_string[10] + "\n"
                outputString += "ao100: " + my_string[11] + "\n"
                outputString += "x10 marathon: " + my_string[12] + "\n"
                outputString += "x42 marathon: " + my_string[13] + "\n"
                outputString += "4x4 - 2x2 relay: " + my_string[14] + "\n```"
            elif puzzle == "5" or puzzle == "5x5":
                outputString += "5x5\n```"
                outputString += "single: " + my_string[15] + "\n"
                outputString += "ao5: " + my_string[16] + "\n"
                outputString += "ao12: " + my_string[17] + "\n"
                outputString += "ao50: " + my_string[18] + "\n"
                outputString += "5x5 - 2x2 relay: " + my_string[19] + "\n```"
            elif puzzle == "6" or puzzle == "6x6":
                outputString += "6x6\n```"
                outputString += "single: " + my_string[20] + "\n"
                outputString += "ao5: " + my_string[21] + "\n"
                outputString += "ao12: " + my_string[22] + "\n"
                outputString += "6x6 - 2x2 relay: " + my_string[23] + "\n```"
            elif puzzle == "7" or puzzle == "7x7":
                outputString += "7x7\n```"
                outputString += "single: " + my_string[24] + "\n"
                outputString += "ao5: " + my_string[25] + "\n"
                outputString += "7x7 - 2x2 relay: " + my_string[26] + "\n```"
            elif puzzle == "8" or puzzle == "8x8":
                outputString += "8x8\n```"
                outputString += "single: " + my_string[27] + "\n"
                outputString += "ao5: " + my_string[28] + "\n```"
            elif puzzle == "9" or puzzle == "9x9":
                outputString += "9x9\n```"
                outputString += "single: " + my_string[29] + "\n```"
            elif puzzle == "10" or puzzle == "10x10":
                outputString += "10x10\n```"
                outputString += "single: " + my_string[30] + "\n```"
            else:
                await message.channel.send(
                    "Can't find this puzzle, make sure it's from 3x3 to 10x10.\nFor other pbs check leaderboard in slidysim."
                )
                bad = True
            if not bad:
                dif = "\nTime since last !update: " + str(int((datetime.datetime.now().timestamp() - (db["lastupdate"]))/60)) + " minutes"
                await message.channel.send(outputString + dif)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"Please specify the puzzle size, for example: !getpb dphdmn 4x4\n```\n{repr(e)}\n```")
    if message.content.startswith("!animate"):
        try:
            # !animate [optional scramble] [solution] [optional tps]
            regex = re.compile("!animate\s*(?P<scramble>[0-9][0-9 /]*[0-9])?\s*(?P<moves>([ULDR][0-9]* *)*[ULDR][0-9]*)\s*(?P<tps>[0-9]{1,})?")
            match = regex.fullmatch(message.content)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            moves = Algorithm(groups["moves"])

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

            await message.channel.send("Working on it! It may take some time, please wait")

            make_video(scramble, moves, tps)

            msg = scramble.to_string() + "\n"
            msg += moves.to_string() + " (" + str(moves.length()) + " moves)\n"
            msg += "TPS (playback): " + str(tps) + "\n"
            msg += "Time (playback): " + str(round(moves.length()/tps, 3))

            with open("movie.webm", "rb") as f:
                picture = discord.File(f)
                await message.channel.send(msg, file=picture)
            os.remove("movie.webm")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!analyse"):
        await message.channel.send("Working on it!")
        try:
            contentArray = message.content.split(" ")
            solution = Algorithm(contentArray[1])
            analysis = analyse(solution)

            scramble = PuzzleState()
            scramble.reset(4, 4)
            scramble.apply(solution.inverse())
            optSolution = solvers[4].solveOne(scramble)

            msg = f"Scramble: {scramble.to_string()}\n"
            msg += f"Your solution [{solution.length()}]: {solution.to_string()}\n"
            msg += f"Optimal solution [{optSolution.length()}]: {optSolution.to_string()}\n"
            msg += "Analysis:"

            await makeTmpSend("analysis.txt", analysis, msg, message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!draw"):
        try:
            state = PuzzleState(message.content[6:])
            if state.size() != (4, 4):
                raise ValueError(f"puzzle size {state.size()} must be 4x4")
            img = draw_state(state)
            img.save('scramble.png', 'PNG')
            with open("scramble.png", "rb") as f:
                picture = discord.File(f)
                await message.channel.send("Your scramble: ", file=picture)
            os.remove("scramble.png")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!getreq"):
        mystr = db["tiers.txt"].lower()
        # print(mystr)
        mystr = mystr.splitlines()
        contentArray = message.content.lower().split(" ")
        # print(contentArray)
        username = contentArray[1]
        matching = [s for s in mystr if username in s]
        my_string = matching[0]
        my_string = my_string.split("\t")
        # print(my_string)

        bad = False
        try:
            puzzle = contentArray[2]
            outputString = (
                "Requirement for tier **" + my_string[0] + "** at the puzzle "
            )
            for i in range(1, len(my_string)):
                try:
                    number = float(my_string[i])
                    intpart = int(math.floor(number))
                    decimals = round(number - intpart, 3)
                    x = str(datetime.timedelta(seconds=intpart)) + str(decimals)[1:]
                except:
                    x = ""
                if x != "":
                    if int(intpart) > 60:
                        my_string[i] = my_string[i] + " (" + x[2:] + ")"

            if puzzle == "3" or puzzle == "3x3":
                outputString += "3x3\n```"
                outputString += "ao5: " + my_string[1] + "\n"
                outputString += "ao12: " + my_string[2] + "\n"
                outputString += "ao50: " + my_string[3] + "\n"
                outputString += "ao100: " + my_string[4] + "\n"
                outputString += "x10 marathon: " + my_string[5] + "\n"
                outputString += "x42 marathon: " + my_string[6] + "\n```"
            elif puzzle == "4" or puzzle == "4x4":
                outputString += "4x4\n```"
                outputString += "single: " + my_string[7] + "\n"
                outputString += "ao5: " + my_string[8] + "\n"
                outputString += "ao12: " + my_string[9] + "\n"
                outputString += "ao50: " + my_string[10] + "\n"
                outputString += "ao100: " + my_string[11] + "\n"
                outputString += "x10 marathon: " + my_string[12] + "\n"
                outputString += "x42 marathon: " + my_string[13] + "\n"
                outputString += "4x4 - 2x2 relay: " + my_string[14] + "\n```"
            elif puzzle == "5" or puzzle == "5x5":
                outputString += "5x5\n```"
                outputString += "single: " + my_string[15] + "\n"
                outputString += "ao5: " + my_string[16] + "\n"
                outputString += "ao12: " + my_string[17] + "\n"
                outputString += "ao50: " + my_string[18] + "\n"
                outputString += "5x5 - 2x2 relay: " + my_string[19] + "\n```"
            elif puzzle == "6" or puzzle == "6x6":
                outputString += "6x6\n```"
                outputString += "single: " + my_string[20] + "\n"
                outputString += "ao5: " + my_string[21] + "\n"
                outputString += "ao12: " + my_string[22] + "\n"
                outputString += "6x6 - 2x2 relay: " + my_string[23] + "\n```"
            elif puzzle == "7" or puzzle == "7x7":
                outputString += "7x7\n```"
                outputString += "single: " + my_string[24] + "\n"
                outputString += "ao5: " + my_string[25] + "\n"
                outputString += "7x7 - 2x2 relay: " + my_string[26] + "\n```"
            elif puzzle == "8" or puzzle == "8x8":
                outputString += "8x8\n```"
                outputString += "single: " + my_string[27] + "\n"
                outputString += "ao5: " + my_string[28] + "\n```"
            elif puzzle == "9" or puzzle == "9x9":
                outputString += "9x9\n```"
                outputString += "single: " + my_string[29] + "\n```"
            elif puzzle == "10" or puzzle == "10x10":
                outputString += "10x10\n```"
                outputString += "single: " + my_string[30] + "\n```"
            else:
                await message.channel.send(
                    "Can't find this puzzle, make sure it's from 3x3 to 10x10."
                )
                bad = True
            if not bad:
                await message.channel.send(outputString)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"Please specify the puzzle size, for example: !getreq ascended 4x4```\n{repr(e)}\n```")
    if message.content.startswith("!getprob"):
        try:
            # !getprob [size: N or WxH] [moves: a-b or e.g. >=m, <m, =m, etc.] [repetitions: optional]
            regex = re.compile("!getprob\s+(?P<width>[0-9]+)(x(?P<height>[0-9]+))?\s+(?P<range>((?P<moves_from>[0-9]+)-(?P<moves_to>[0-9]+))|((?P<comparison>[<>]?=?)(?P<moves>[0-9]*)))(\s+(?P<repetitions>[0-9]*))?")
            match = regex.fullmatch(message.content)

            if match is None:
                raise SyntaxError(f"failed to parse arguments")

            groups = match.groupdict()

            # read the size
            w = int(groups["width"])
            if groups["height"] is None:
                h = w
            else:
                h = int(groups["height"])

            # get the distribution
            dist = distributions.get_distribution(w, h)

            # check if from-to or comparison, and calculate probability
            moves_range = groups["range"]
            if groups["comparison"] is None:
                start = int(groups["moves_from"])
                end = int(groups["moves_to"])
                prob_one = dist.prob_range(start, end)
            else:
                comp = comparison.from_string(groups["comparison"])
                moves = int(groups["moves"])
                prob_one = dist.prob(moves, comp)

            # number of repetitions
            if groups["repetitions"] is None:
                reps = 1
            else:
                reps = int(groups["repetitions"])

            # compute the probability of a scramble appearing at least once
            prob = 1 - (1 - prob_one)**reps

            # write the message
            msg = f"Probability of {w}x{h} having an optimal solution of {moves_range} moves is {prob_one}\n"
            if reps > 1:
                msg += f"Probability of at least one scramble out of {reps} within that range is {prob}"

            await message.channel.send(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if "scrable" in message.content.lower():
        await message.channel.send("Infinity tps, " + message.author.mention + "?")
        await message.add_reaction("0️⃣")
    if message.content.startswith("!paint"):
        good = False
        try:
            img_data = requests.get(message.attachments[0].url).content
            good = True
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"Please upload an image file!\n```\n{repr(e)}\n```")
        if good:
            contentArray = message.content.lower().split(" ")
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
            f = open("scramble.txt", "w+")
            f.write(mystr)
            f.close()
            puzzleSize = str(puzzleSize)
            with open("scramble.txt", "rb") as f:
                await message.channel.send(
                    "Your scramble is ("
                    + puzzleSize
                    + "x"
                    + puzzleSize
                    + " sliding puzzle)\n(download file if its large):",
                    file=discord.File(f, "scramble.txt"),
                )
            os.remove("scramble.txt")
    if message.content.startswith("!rev"):
        alg = Algorithm(message.content[5:])
        alg.invert()
        await message.channel.send(alg.to_string())
    if message.content.startswith("!not"):
        alg = Algorithm(message.content[5:])
        alg.invert().revert()
        await message.channel.send(alg.to_string())
    if message.content.startswith("!tti"):
        try:
            words = message.content[5:]
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
    if message.content.startswith("!datecompare"):
        contentArray = message.content.lower().split(" ")
        if len(contentArray) != 3:
            await message.channel.send("Sorry your dates are wrong. Format:\n!datecompare 2021-06-13 2021-06-14")
        else:
            date1 = "SMART"+contentArray[1]
            date2 = "SMART"+contentArray[2]
            out = comparelist(date1, date2)
            f = open("compare.txt", "w+")
            f.write(out)
            f.close()
            with open("compare.txt", "rb") as f:
                txt = discord.File(f)
                await message.channel.send("Your cmp: ", file=txt)
            os.remove("compare.txt")
    if message.content.startswith("!movesgame"):
        scramble = scrambler.getScramble(4)
        img = draw_state(scramble)
        img.save('scramble.png', 'PNG')
        with open("scramble.png", "rb") as f:
            picture = discord.File(f)
            await message.channel.send("Check this: https://dphdmn.github.io/movesgame/\nFind good move at this scramble: \n" + scramble.to_string() + "\nYou will get answer in few seconds", file=picture)
        os.remove("scramble.png")

        # time the solve
        start_time = time.time()
        good_moves = [move.to_string(sol.first()) for sol in solvers[4].solveGood(scramble)]
        elapsed = time.time() - start_time

        # wait until 5s has elapsed, including solve time
        await asyncio.sleep(5 - elapsed)

        msg = ""
        for m in "ULDR":
            if m in good_moves:
                msg += f"**{m}** \tis \t**OK!**\t move\n"
            else:
                msg += f"{m} \tis \tbad\t move\n"
        await message.channel.send("||" + msg + "||")
    if message.content.startswith("!goodm"):
        try:
            scramble = PuzzleState(message.content[7:])
            size = scramble.size()
            if size == (3, 3) or size == (4, 4):
                solver = solvers[size[0]]
                good_moves = [move.to_string(sol.first()) for sol in solver.solveGood(scramble)]
                await message.channel.send("Your scramble:\n" + scramble.to_string() + "\nGood moves for your scramble: " + ", ".join(good_moves))
            else:
                raise ValueError(f"puzzle size {scramble.size()} must be 3x3 or 4x4")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!eggsolve"):
        scramble = PuzzleState(message.content[10:])
        size = scramble.size()
        if size == (3, 3) or size == (4, 4):
            try:
                a = perf_counter()
                solutions = solvers[size[0]].solveAll(scramble)
                b = perf_counter()
                string = ""
                string += "Time: " + str(round((b - a), 3)) + "\n"
                string += "Amount of solutions: " + str(len(solutions)) + "\n"
                string += "Len: " + str(solutions[0].length()) + "\n"
                string += '\n'.join([s.to_string() for s in solutions])
                await makeTmpSend("Solutions.txt", string, "All solutions for scramble " + scramble.to_string(), message.channel)
            except Exception as e:
                traceback.print_exc()
                await message.channel.send(f"```\n{repr(e)}\n```")
        else:
            print(len(scramble))
            await message.channel.send("Your scramble is wrong.")
    if message.content.startswith("!solve") or message.content.startswith("!video"):
        try:
            video = message.content.startswith("!video")

            scramble = PuzzleState(message.content[7:])
            size = scramble.size()

            # don't allow daily fmc scramble
            if fmc.status() == 1:
                daily_fmc_scramble = fmc.scramble()
                if scramble == daily_fmc_scramble:
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
            solution_str = solution.to_string()
            if solution_str == "":
                solution_str = ":egg:"

            msg = f"Scramble: {scramble.to_string()}\n"
            msg += f"Solution [{solution.length()}]: ||{solution_str}||\n"
            msg += f"Time: {round((b - a), 3)}"

            if video:
                msg += "\nPlease wait! I'm making a video for you!"

            await message.channel.send(msg)

            if video:
                make_video(scramble, solution, 8)
                with open("movie.webm", "rb") as f:
                    video = discord.File(f)
                    await message.channel.send("", file=video)
                os.remove("movie.webm")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!simplify"):
        try:
            alg = Algorithm(message.content[10:])
            old_len = alg.length()
            alg.simplify()
            new_len = alg.length()
            alg_str = alg.to_string()
            await message.channel.send(f"[{old_len} -> {new_len}] {alg_str}")
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!solvable"):
        try:
            pos = PuzzleState(message.content[10:])
            if pos.solvable():
                msg = "solvable"
            else:
                msg = "unsolvable"
            await message.reply(msg)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content.startswith("!8fmc"):
        try:
            if len(message.content) == 5:
                n = 100
            else:
                n = int(message.content[6:])
                n = max(1, min(1000, n))

            data = ""
            l = []
            for i in range(n):
                scramble = scrambler.getScramble(3)
                solution = solvers[3].solveOne(scramble)
                length = solution.length()

                l.append(length)
                data += scramble.to_string() + "\t" + str(length) + "\n"

            msg = "Average: " + str(round(sum(l)/n, 3)) + "\n"
            msg += "Longest: " + str(max(l)) + "\n"
            msg += "Shortest: " + str(min(l))

            await makeTmpSend("8fmc.txt", data, msg, message.channel)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    if message.content == "!egg":
        egg = readFilenormal("misc/egg.txt")
        await message.channel.send("```" + egg + "```")
    if message.content.startswith("!help"):
        await message.channel.send(
            "Egg bot commands: https://github.com/dphdmn/newEggBot/blob/master/README.md"
        )
    if message.content.startswith("!git"):
        if message.author.guild_permissions.administrator:
            await message.channel.send(bot.git_info)
    if message.content.startswith("!restart"):
        if message.author.guild_permissions.administrator:
            await message.channel.send("Restarting...")
            db["restart/channel_id"] = message.channel.id
            db["restart/message"] = "Restarted"
            bot.restart()
    if message.content.startswith("!botupdate"):
        if message.author.guild_permissions.administrator:
            await message.channel.send("Updating...")
            db["restart/channel_id"] = message.channel.id
            db["restart/message"] = "Updated!"
            bot.update()
            bot.restart()

@tasks.loop(seconds=1)
async def spam(chan, msg):
    await chan.send(msg)


keep_alive()
try:
    client.run(os.environ["eggkey"])
except:
    req = requests.get("https://discord.com/api/path/to/the/endpoint")
    print(req.text)
