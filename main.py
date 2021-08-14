import scrambler
from solver import solvers
import os
from keep_alive import keep_alive
from prettytable import PrettyTable
import discord
from discord.ext import tasks, commands
import urllib.request
import html2text
import traceback
from time import perf_counter
import datetime
import math
import numpy as np
import cv2
import sys
import requests
import glob
import zlib
import re
import regex
import bot as bot_helper
import time_format
import move
import helper.serialize as serialize
from animate import make_video
from puzzle_state import PuzzleState
from algorithm import Algorithm
from analyse import analyse
from draw_state import draw_state
from fmc.daily_fmc import DailyFMC
from fmc.fmc import FMC
from movesgame.movesgame import MovesGame
from movesgame.tournament import MovesGameTournament
from probability import comparison, distributions
from replit import db

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

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

def addConstants():
    for filename in glob.glob('Constant_Files/*.*'):
        print(filename[15:])
        text = readFilenormal(filename)
        db[filename[15:]] = text

addConstants()

#_______________________________Auto leaderboard

def getLeaderboard():
    my_secret = os.environ['slidysim']
    r = requests.post(my_secret, data = {
        'width':'-1',
        'height':'-1',
        'solvetype':'any',
        'displaytype':'Standard',
        'avglen':'-1',
        'pbtype':'time',
        'sortby':'time',
        'controls':'km',
        'user':'',
        'solvedata':0,
        'version':'28.3'
    })

    data = r.text.split("<br>")
    data = data[1:-1]
    solvesdata = []
    catNames = [
        ["3x3-ao5", "Standard", "3x3", "5"],
        ["3x3-ao12","Standard", "3x3", "12"],
        ["3x3-ao50","Standard", "3x3", "50"],
        ["3x3-ao100","Standard", "3x3", "100"],
        ["3x3-x10","Marathon 10","3x3", "1"],
        ["3x3-x42","Marathon 42","3x3", "1"],
        ["4x4-sin","Standard", "4x4", "1"],
        ["4x4-ao5","Standard", "4x4", "5"],
        ["4x4-ao12","Standard", "4x4", "12"],
        ["4x4-ao50","Standard", "4x4", "50"],
        ["4x4-ao100","Standard", "4x4", "100"],
        ["4x4-x10","Marathon 10","4x4", "1"],
        ["4x4-x42","Marathon 42","4x4", "1"],
        ["4x4-rel","2-N relay","4x4", "1"],
        ["5x5-sin","Standard", "5x5", "1"],
        ["5x5-ao5","Standard", "5x5", "5"],
        ["5x5-ao12","Standard", "5x5", "12"],
        ["5x5-ao50","Standard", "5x5", "50"],
        ["5x5-rel","2-N relay","5x5", "1"],
        ["6x6-sin","Standard", "6x6", "1"],
        ["6x6-ao5","Standard", "6x6", "5"],
        ["6x6-ao12","Standard", "6x6", "12"],
        ["6x6-rel","2-N relay","6x6", "1"],
        ["7x7-sin","Standard", "7x7", "1"],
        ["7x7-ao5","Standard", "7x7", "5"],
        ["7x7-rel","2-N relay","7x7", "1"],
        ["8x8-sin","Standard", "8x8", "1"],
        ["8x8-ao5","Standard", "8x8", "5"],
        ["9x9-sin","Standard", "9x9", "1"],
        ["10x10-sin","Standard", "10x10", "1"],
    ]
    namelist=[]
    for i in data:
        ilist = i.split(",")
        puzzle=str(ilist[0]) + "x" + str(ilist[1])
        mode = ilist[2]
        name = ilist[4].upper()
        solvetime = str(format((int(ilist[5]))/1000, '.3f'))
        avgType = str(ilist[8])
        category = ""
        for cat in catNames:
            if cat[1]==mode and cat[2] == puzzle and cat[3] == avgType:
                category = cat[0]
        if category != "":
            if name not in namelist:
                namelist.append(name)
            solvesdata.append({
                "Cat" : category,
                "Name": name,
                "Time": solvetime,
            })
    reqstring = db["tiers.txt"].splitlines()
    req=[]
    tier_cost = db["tier_cost.txt"].lower().split("\t")
    for id, item in enumerate(tier_cost):
        tier_cost[id] = int(item)
    tier_limits = db["tier_limits.txt"].lower().split("\t")
    for id, item in enumerate(tier_limits):
        tier_limits[id] = int(item)
    id = 0
    tierNames=["Unranked"]
    for i in reqstring:
        i = i.split("\t")
        tierNames.append(i[0])
        req.append({"Tiercost":tier_cost[id],"Tierlimit":tier_limits[id], "Scores": i[1:], "TierID":id+1})
        id += 1
    req.reverse()
    #print(namelist)
    userData = []
    for name in namelist:
        scoresRow=[]
        userCatsolves = [name]
        power=0
        for catid, cat in enumerate(catNames):
            category = cat[0]
            solves=[]
            for solve in solvesdata:
                if solve["Cat"] == category and solve["Name"] == name:
                    solves.append(float(solve["Time"]))
            if len(solves) == 0:
                userCatsolves.append("N/A")
                scoresRow.append(0)
            else:
                userscoretime=round(min(solves),3)
                userCatsolves.append(str(format(userscoretime,'.3f')))
                myscoreid=0
                for reqdata in req:
                    scoresValues=reqdata["Scores"]
                    if userscoretime < float(scoresValues[catid]):
                        power+=int(reqdata["Tiercost"])
                        myscoreid=reqdata["TierID"]
                        #if name == "dphdmn":
                        #  print(int(reqdata["Tiercost"]), power)
                        break
                scoresRow.append(myscoreid)
        userCatsolves.append(str(power))
        tierID=0
        for id,i in enumerate(tier_limits):
            if power>=int(i):
                tierID=id+1
        userCatsolves.append(tierNames[tierID])
        userCatsolves.extend(scoresRow)
        userData.append(userCatsolves)
        #print(userCatsolves)
    string = ""
    userData.sort(key=lambda x: int(x[31]))
    userData.reverse()
    smartstring = ""
    y = PrettyTable()
    y.field_names = ["Name","Place","Power","Tier","3x3 ao5","3x3 ao12","3x3 ao50","3x3 ao100","3x3 x10", "3x3 x42", "4x4 single", "4x4 ao5", "4x4 ao12", "4x4 ao50", "4x4 ao100", "4x4 x10", "4x4 x42", "4x4 relay", "5x5 single", "5x5 ao5", "5x5 ao12", "5x5 ao50", "5x5 relay", "6x6 single", "6x6 ao5", "6x6 ao12", "6x6 relay", "7x7 single", "7x7 ao5", "7x7 relay", "8x8 single", "8x8 ao5", "9x9 single", "10x10 single"]
    headers = ["3x3 ao5","3x3 ao12","3x3 ao50","3x3 ao100","3x3 x10", "3x3 x42", "4x4 single", "4x4 ao5", "4x4 ao12", "4x4 ao50", "4x4 ao100", "4x4 x10", "4x4 x42", "4x4 relay", "5x5 single", "5x5 ao5", "5x5 ao12", "5x5 ao50", "5x5 relay", "6x6 single", "6x6 ao5", "6x6 ao12", "6x6 relay", "7x7 single", "7x7 ao5", "7x7 relay", "8x8 single", "8x8 ao5", "9x9 single", "10x10 single"]
    rows=[]
    scoresbase=33
    for num,i in enumerate(userData):
        row=[]
        #print("doing")
        #print(str(i))
        string+='\t'.join(str(x) for x in i)+"\n"
        row.append(i[0])
        row.append(str(num+1))
        row.append(i[31])
        row.append(i[32])
        smartstring += i[0] + "\t" + str(num+1) +"\t" + i[31] + "\t"
        for j in range(len(catNames)):
            smartstring += i[j+1] + "\t"
            row.append(''.join([i[j+1]]))
        smartstring += "\n"
        rows.append(row)
    y.add_rows(rows)
    tierNames.reverse()
    myhtml="<main class=\"st_viewport\">"
    for id, tier in enumerate(tierNames):
        if tier != "Unranked":
            myreqdata = req[id]
        reqscoreslist=myreqdata["Scores"]
        myhtml+="<div class=\"st_wrap_table\" data-table_id=\"" + str(id+1)+"\">\n"
        myhtml+="<header class=\"st_table_header\">\n"
        myhtml+="<h2>"
        myhtml+= tier
        myhtml+="</h2>\n"
        myhtml+="<div class=\"st_row\">\n"
        myhtml+="<div class=\"st_column _name\"></div>\n"
        myhtml+="<div class=\"st_column _place\">"+str(myreqdata["Tiercost"])+"</div>\n"
        myhtml+="<div class=\"st_column _power\">"+str(myreqdata["Tierlimit"])+"</div>\n"
        for e,_ in enumerate(headers):
            myhtml+="<div class=\"st_column _score\">"+ str(reqscoreslist[e]) +"</div>\n"
        myhtml+="</div>\n"
        myhtml+="<div class=\"st_row\">\n"
        myhtml+="<div class=\"st_column _name\">Name</div>\n"
        myhtml+="<div class=\"st_column _place\">Place</div>\n"
        myhtml+="<div class=\"st_column _power\">Power</div>\n"
        for i in headers:
            myhtml+="<div class=\"st_column _score\">"+ i +"</div>\n"
        myhtml+="</div>\n"
        myhtml+="</header>\n"

        myhtml+="<div class=\"st_table\">\n"
        for personid, person in enumerate(rows):
            dataRow = userData[personid]
            if person[3] == tier:
                userTierID = 12-int(tierNames.index(tier))
                myhtml+="<div class=\"st_row\">\n"
                myhtml+="<div class=\"st_column _name\">"+person[0]+"</div>\n"
                myhtml+="<div class=\"st_column _place\">"+str(person[1])+"</div>\n"
                myhtml+="<div class=\"st_column _power\">"+str(person[2])+"</div>\n"
                for idsmall,_ in enumerate(headers):
                    #print(scoresbase+idsmall)
                    #print (dataRow)
                    #print("last id: "+str((len(dataRow)-1)))
                    scoreTierID = int(dataRow[scoresbase+idsmall])
                    if scoreTierID > userTierID:
                        colorID = 3
                    elif scoreTierID == userTierID-1:
                        colorID = 1
                    elif scoreTierID == userTierID:
                        colorID = 0
                    else:
                        colorID = 2
                    score = str(person[idsmall+4])
                    if score == "N/A":
                        score = ""
                    myhtml+="<div class=\"st_column _score\" color-id=\"" + str(colorID)+"\">"+ score +"</div>\n"
                myhtml+="</div>\n"
        myhtml+="</div>\n"
        myhtml+="</div>\n"
    myhtml+="</main>"
    updatedate = str(datetime.datetime.today().strftime('%Y-%m-%d'))
    #updatedate = "2021-06-14"
    db["leaderboard.txt"] = string #only for getPB command, should be fixed and removed
    db["smartboard.txt"] = smartstring #main format for compare
    db["prettylb.txt"] = y.get_string() #90% useless thing for !getlb - txt format lb
    db["egg.html"] = myhtml #lb that is using on website
    db["HTML" + updatedate] = dbcomp(myhtml)
    db["SMART" + updatedate] = dbcomp(smartstring)
    updatehtml()

def dbcomp(string):
    return zlib.compress(string.encode("utf-8")).hex()

def dbdecomp(compthingy):
    return zlib.decompress(bytes.fromhex(compthingy)).decode("utf-8")

def getAllHTML():
    matches = db.prefix("HTML")
    print("ALL DATES")
    print(matches)
    myhtmlshots = []
    for i in matches:
        mydate = i.replace("HTML", "")
        myhtmlshots.append({"date": mydate, "htmlinfo": dbdecomp(db[i])})
    myhtmlshots.sort(key=lambda x: datetime.datetime.strptime(x["date"], '%Y-%m-%d'))
    myhtmlshots.reverse()
    return myhtmlshots

def updatehtml():
    allhtml = getAllHTML()
    allhtml = [allhtml[0]]
    egginfo = ""
    egginfo += "<div class=\"tab\">\n"
    #headers
    for e, i in enumerate(allhtml):
        mydate = i["date"]
        if e == 0:
            egginfo += "<button class=\"tablinks\" id=\"defaultOpen\" onclick=\"openCity(event, \'" + mydate + "\')\">" + mydate + "</button>\n"
        else:
            egginfo += "<button class=\"tablinks\" onclick=\"openCity(event, \'" + mydate + "\')\">" + mydate + "</button>\n"
    egginfo += "<div>\n"
    #content
    for i in allhtml:
        myinfo = i["htmlinfo"]
        mydate = i["date"]
        egginfo += "<div id=\"" + mydate + "\" class=\"tabcontent\">\n"
        egginfo += myinfo
        egginfo += "</div>\n"
    f = open("templates/index.html", "w+")
    f.write(db["header.html"])
    f.write(egginfo)
    f.write(db["footer.html"])
    f.close()

# _____________compare tables___________________

def readFile(name):
    with open(name, "r") as file:
        mystr = file.read().lower()
    return mystr


def fixSpaces(string):
    out = string.replace("\t\t", "\tN/A\t")
    if string == out:
        return out
    return fixSpaces(out)


def makeList(string, tierL, rankNames):
    list = []
    for i in string:
        i = i.split("\t")
        try:
            power = int(i[2])
        except:
            print(i)
        rankN = 0
        for j in tierL:
            if power > j:
                rankN += 1
        if "".join(i[3:]).upper() != "N/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/AN/A":
            list.append({
                "Name": i[0],
                "Place": i[1],
                "Power": i[2],
                "Rank": rankNames[rankN],
                "rankID": rankN,
                "Scores": i[3:],
            })
    return list


def getScores(req, old, new, catNames, rankID):
    log = ""
    ids = []
    for id, (valueNew, valueOld) in enumerate(zip(new, old)):
        if valueNew != "" and valueNew != "N/A" and valueNew != "n/a":
            if valueOld == "" or valueOld == "N/A" or valueOld == "n/a" or float(valueNew) < float(valueOld):
                ids.append(id)
    for i in req:
        scoreslog = ""
        tier = i["Tier"]
        scores = i["Scores"]
        reqId = i["rankID"]
        watched = []
        for j in ids:
            if reqId > rankID - 2 and float(new[j]) < float(scores[j]):
                if (old[j] == "" or old[j] == "N/A" or old[j] == "n/a") or float(old[j]) > float(scores[j]):
                    scoreslog += " {{" + catNames[j] + "[" + old[j] + "->" + new[j] + "]}}"
                else:
                    scoreslog += " " + catNames[j] + "[" + old[j] + "->" + new[j] + "]"
                watched.append(j)
        if scoreslog != "":
            log += " _ _ ---" + tier + "_scores---" + scoreslog + " "
        for i in watched:
            ids.remove(i)
    return log[:-1]


def comparelist(name1, name2):
    req = []
    catNames = [
        "3x3-ao5",
        "3x3-ao12",
        "3x3-ao50",
        "3x3-ao100",
        "3x3-x10",
        "3x3-x42",
        "4x4-sin",
        "4x4-ao5",
        "4x4-ao12",
        "4x4-ao50",
        "4x4-ao100",
        "4x4-x10",
        "4x4-x42",
        "4x4-rel",
        "5x5-sin",
        "5x5-ao5",
        "5x5-ao12",
        "5x5-ao50",
        "5x5-rel",
        "6x6-sin",
        "6x6-ao5",
        "6x6-ao12",
        "6x6-rel",
        "7x7-sin",
        "7x7-ao5",
        "7x7-rel",
        "8x8-sin",
        "8x8-ao5",
        "9x9-sin",
        "10x10-sin",
    ]
    rankNames = ["{UNRANKED}"]
    reqstring = db["tiers.txt"].lower().splitlines()
    id = 0
    for i in reqstring:
        i = i.split("\t")
        id += 1
        req.append({"Tier": i[0].upper(), "rankID": id, "Scores": i[1:]})
        rankNames.append(i[0].upper())
    req.reverse()
    tier_limits = db["tier_limits.txt"].lower().split("\t")
    for id, item in enumerate(tier_limits):
        tier_limits[id] = int(item)
    try:
        dberror = "none"
        textinfo1 = fixSpaces(dbdecomp(db[name1]).lower()).splitlines()
        textinfo2 = fixSpaces(dbdecomp(db[name2]).lower()).splitlines()
    except:
        print(traceback.format_exc())
        dberror = "Error with loading data"
    if dberror != "Error with loading data":
        old_list = makeList(textinfo1, tier_limits, rankNames)
        new_list = makeList(textinfo2, tier_limits, rankNames)

        log = ""

        list_of_lists = []
        #superid=0
        for item_new in new_list:
            item_old = next(
                (item for item in old_list if item["Name"] == item_new["Name"]), None
            )
            name = item_new["Name"]
            if item_old == None:
                mylist = []
                mylist.append(name)
                mylist.append("[#" + item_new["Place"] + "]")
                mylist.append(item_new["Rank"])
                mylist.append("-")
                mylist.append("New player")
                mylist.append("Welcome!")
                list_of_lists.append(mylist)
            else:
                # if int(item_old["Power"]) < int(item_new["Power"]):
                if "".join(item_old["Scores"]).upper() != "".join(item_new["Scores"]).upper() and ("".join(item_old["Scores"]).upper()+"N/A") != "".join(item_new["Scores"]).upper():
                    #  print(item_new["Name"]+''.join(item_old["Scores"]))
                    # print(''.join(item_new["Scores"]))
                    # print("".join(item_old["Scores"]).upper())
                    # print("".join(item_new["Scores"]).upper())
                    mylist = []
                    if int(item_old["Place"]) > int(item_new["Place"]):
                        mylist.append(name)
                        mylist.append(
                            "[#" + item_old["Place"] + " -> #" + item_new["Place"] + "]"
                        )
                    else:
                        mylist.append(name)
                        mylist.append("[#" + item_new["Place"] + "]")

                    if item_old["Rank"] != item_new["Rank"]:
                        mylist.append("[New Tier: " + item_new["Rank"] + "!]")
                    else:
                        mylist.append("===" + item_new["Rank"] + "===")
                    mylist.extend(
                        getScores(
                            req,
                            item_old["Scores"],
                            item_new["Scores"],
                            catNames,
                            item_new["rankID"],
                        ).split()
                    )
                    if item_new["Rank"] == "{UNRANKED}":
                        mylist.append(" ")
                        mylist.append(" ")
                        mylist.append("Nice pbs!")
                        mylist.append("Good luck")
                        mylist.append("With beginner scores")
                        mylist.append("Next time :)")
                    #mylist[0] = mylist[0] + str(superid)
                    #superid += 1
                    list_of_lists.append(mylist)
        maxDepth = 0
        maxColumns = len(list_of_lists)

        tableRows = []
        for i in list_of_lists:
            l = len(i)
            if l > maxDepth:
                maxDepth = l
        for j in range(maxDepth):
            myrow = []
            for i in range(maxColumns):
                i_list = list_of_lists[i]
                if len(i_list) > j:
                    myrow.append(i_list[j])
                else:
                    myrow.append("_")
            tableRows.append(myrow)
        x = PrettyTable()
        x.field_names = tableRows[0]
        x.add_rows(tableRows[1:])
        return x.get_string().replace("_", " ")
    else:
        return dberror

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
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

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
    daily_fmc = DailyFMC(bot, int(os.environ["daily_fmc_channel"]), int(os.environ["daily_fmc_results_channel"]))
    short_fmc = FMC(bot, int(os.environ["fmc_channel"]))
    await daily_fmc.start()

    # dict of fmc objects by id
    global fmcs
    fmcs = {x.channel.id : x for x in [daily_fmc, short_fmc]}

    # create movesgame
    global movesgame, movesgame_tournament
    movesgame = MovesGame(bot, int(os.environ["movesgame_channel"]))
    movesgame_tournament = MovesGameTournament(bot, int(os.environ["movesgame_tournament_channel"]))

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
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

    if message.content.startswith("!spam"):
        if message.author.guild_permissions.administrator:
            shit = message.content[6:]
            msg = ""
            for x in range(3000):
                msg += shit + " "
            spam.start(message.channel, msg[:2000])
    elif message.content.startswith("!fmc"):
        if message.channel.id not in fmcs:
            return
        fmc = fmcs[message.channel.id]
        if not fmc.round.running():
            return
        msg = "Current FMC scramble: " + fmc.round.get_scramble().to_string() + "\n"
        msg += "Optimal solution length: " + str(fmc.round.get_solution().length()) + "\n"
        msg += "Time remaining: " + time_format.format(fmc.round.remaining())
        await message.channel.send(msg)
    elif message.content.startswith("!submit"):
        if message.channel.id not in fmcs:
            return
        fmc = fmcs[message.channel.id]
        if not fmc.round.running():
            return
        try:
            await message.delete()
            solution = Algorithm(message.content[8:])
            await fmc.submit(message.author, solution)
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif message.content.startswith("!results"):
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
                    msg += f"{user.name}: {result.length()}\n"
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

            msg = ""
            for id in sorted_ids:
                user = bot.get_user(id)
                good = results[id]["correct"]
                bad = results[id]["incorrect"]
                formatted = format(100*good/(good+bad), ".2f") + "%"

                # only show results for people with at least 10 rounds
                if good+bad >= 10:
                    msg += f"{user.name}: {good}/{good+bad} = {formatted}\n"

            await message.channel.send(msg)
    elif message.content.startswith("!startfmc"):
        if message.channel.id != short_fmc.channel.id or short_fmc.round.running():
            return
        await short_fmc.start()
    elif message.content.startswith("!getlb"):
        await makeTmpSend("prettylb.txt", db["prettylb.txt"], "Leaderboard for ranks: ", message.channel)
    elif message.content.startswith("!wrupdate"):
        url = os.environ["updateURL"]
        x = requests.get(url).text
        if x == "":
            x = "WRs updated\n" + \
                "WRs: http://slidysim.000webhostapp.com/leaderboard/records.html\n" + \
                "WRs (all): http://slidysim.000webhostapp.com/leaderboard/records_all.html\n" + \
                "WRs (moves): http://slidysim.000webhostapp.com/leaderboard/records_moves.html\n" + \
                "WRs (moves, all): http://slidysim.000webhostapp.com/leaderboard/records_all_moves.html"
        await message.channel.send(x)
    elif message.content.startswith("!update"):
        await message.channel.send("Wait for it!")
        try:
            getLeaderboard()
            webpage = os.environ["webpage"]
            msg = f"Check this: {webpage}\nProbably updated! Try !getpb command:"
            await makeTmpSend("smartboard.txt", db["smartboard.txt"], msg, message.channel)
            db["lastupdate"] = datetime.datetime.now().timestamp()
        except Exception as e:
            traceback.print_exc()
            await message.channel.send(f"```\n{repr(e)}\n```")
    elif message.content.startswith("!stop"):
        if message.author.guild_permissions.administrator:
            spam.cancel()
    elif message.content.startswith("!getreal"):
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
    elif message.content.startswith("!getscramble"):
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
    elif message.content.startswith("!getwr"):
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
    elif message.content.startswith("!wrsby"):
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
    elif message.content.startswith("!getpb"):
        mystr=db["leaderboard.txt"].lower()
        # print(mystr)
        mystr = mystr.splitlines()
        contentArray = message.content.lower().split(" ")
        # print(contentArray)
        username = contentArray[1]
        matching = [s for s in mystr if username in s]
        my_string = matching[0]
        my_string = my_string.split("\t")

        if len(contentArray) == 2:
            ids = [800468752905797664, 800468727324737586, 800468938629972038, 800468948939309117,
                   800468960348733461, 818585243560312852, 818585257393389658, 818585267924893706]
            if message.channel.id in ids:
                n = ids.index(message.channel.id)+3
            else:
                n = 4
            contentArray.append(str(n))

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
    elif message.content.startswith("!animate"):
        try:
            # !animate [optional scramble] [solution] [optional tps]
            scr_reg = regex.puzzle_state("scramble")
            mov_reg = regex.algorithm("moves")
            tps_reg = regex.positive_integer("tps")
            reg = re.compile(f"!animate\s*{scr_reg}?\s*{mov_reg}\s*{tps_reg}?")
            match = reg.fullmatch(message.content)

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
    elif message.content.startswith("!analyse"):
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
    elif message.content.startswith("!draw"):
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
    elif message.content.startswith("!getreq"):
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

        if len(contentArray) == 2:
            ids = [800468752905797664, 800468727324737586, 800468938629972038, 800468948939309117,
                   800468960348733461, 818585243560312852, 818585257393389658, 818585267924893706]
            if message.channel.id in ids:
                n = ids.index(message.channel.id)+3
            else:
                n = 4
            contentArray.append(str(n))

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
    elif message.content.startswith("!getprob"):
        try:
            # !getprob [size: N or WxH] [moves: a-b or e.g. >=m, <m, =m, etc.] [repetitions: optional]
            size_reg = regex.size("width", "height")
            reps_reg = regex.positive_integer("repetitions")
            reg = re.compile(f"!getprob\s+{size_reg}\s+(?P<range>((?P<moves_from>[0-9]+)-(?P<moves_to>[0-9]+))|((?P<comparison>[<>]?=?)(?P<moves>[0-9]*)))(\s+{reps_reg})?")
            match = reg.fullmatch(message.content)

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
    elif message.content.startswith("!paint"):
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
    elif message.content.startswith("!rev"):
        alg = Algorithm(message.content[5:])
        alg.invert()
        await message.channel.send(alg.to_string())
    elif message.content.startswith("!not"):
        alg = Algorithm(message.content[5:])
        alg.invert().revert()
        await message.channel.send(alg.to_string())
    elif message.content.startswith("!tti"):
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
    elif message.content.startswith("!savecmp"):
        if message.author.guild_permissions.administrator:
            today = str(datetime.datetime.today().strftime('%Y-%m-%d'))
            db["SMARTanon"] = db["SMART"+today]
            await message.channel.send("Saved to anon!")
        else:
            await message.channel.send("Sorry, you are not admin")
    elif message.content.startswith("!anoncmp"):
        date1 = "SMARTanon"
        date2 = "SMART" + str(datetime.datetime.today().strftime('%Y-%m-%d'))
        out = comparelist(date1, date2)
        f = open("compare.txt", "w+")
        f.write(out)
        f.close()
        with open("compare.txt", "rb") as f:
            txt = discord.File(f)
            await message.channel.send("Your cmp to last anon: ", file=txt)
        os.remove("compare.txt")
    elif message.content.startswith("!datecompare"):
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
    elif message.content.startswith("!compare"):
        out = comparelist("file1.txt", "file2.txt")
        if len(out) > 1900:
            f = open("compare.txt", "w+")
            f.write(out)
            f.close()
            with open("compare.txt", "rb") as f:
                txt = discord.File(f)
                await message.channel.send("Your cmp: ", file=txt)
            os.remove("compare.txt")
        else:
            await message.channel.send("```" + out + "```")
    elif message.content.startswith("!cmp1"):
        good = False
        try:
            text = requests.get(message.attachments[0].url).content.decode("utf-8")
            # print(message.attachments)
            good = True
        except:
            await message.channel.send("Can't get file")
        if good:
            db["file1.txt"] = dbcomp(text)
            await message.channel.send("Probably updated")
    elif message.content.startswith("!cmp2"):
        good = False
        try:
            text = requests.get(message.attachments[0].url).content.decode("utf-8")
            # print(message.attachments)
            good = True
        except:
            await message.channel.send("Can't get file")
        if good:
            db["file2.txt"] = dbcomp(text)
            await message.channel.send("Probably updated")
    elif message.content.startswith("!movesgame"):
        if message.channel.id == movesgame.channel.id:
            await movesgame.start()
    elif message.content.startswith("!tournament"):
        if message.channel.id == movesgame_tournament.channel.id:
            await movesgame_tournament.run()
    elif message.content.startswith("!goodm"):
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
    elif message.content.startswith("!eggsolve"):
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
    elif message.content.startswith("!solve") or message.content.startswith("!video"):
        try:
            video = message.content.startswith("!video")

            scramble = PuzzleState(message.content[7:])
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
    elif message.content.startswith("!simplify"):
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
    elif message.content.startswith("!solvable"):
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
    elif message.content.startswith("!8fmc"):
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
    elif message.content == "!egg":
        egg = readFilenormal("misc/egg.txt")
        await message.channel.send("```" + egg + "```")
    elif message.content.startswith("!help"):
        await message.channel.send(
            "Egg bot commands: https://github.com/dphdmn/newEggBot/blob/master/README.md"
        )
    elif message.content.startswith("!git"):
        if message.author.guild_permissions.administrator:
            await message.channel.send(bot_helper.git_info)
    elif message.content.startswith("!restart"):
        if message.author.guild_permissions.administrator:
            await message.channel.send("Restarting...")
            db["restart/channel_id"] = message.channel.id
            db["restart/message"] = "Restarted"
            bot_helper.restart()
    elif message.content.startswith("!botupdate"):
        if message.author.guild_permissions.administrator:
            await message.channel.send("Updating...")
            db["restart/channel_id"] = message.channel.id
            db["restart/message"] = "Updated!"
            bot_helper.update()
            bot_helper.restart()
    elif message.content.startswith("!dbdump"):
        owner = int(os.environ["owner"])
        if message.author.id == owner:
            my_db = {}
            for key in db.keys():
                my_db[key] = db[key]
            await makeTmpSend("db.txt", serialize.serialize(my_db), "", message.channel)

@tasks.loop(seconds=1)
async def spam(chan, msg):
    await chan.send(msg)

keep_alive()
try:
    bot.run(os.environ["eggkey"])
except:
    req = requests.get("https://discord.com/api/path/to/the/endpoint")
    print(req.text)
