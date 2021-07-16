import scrambler
from solver import solvers
import os
from keep_alive import keep_alive
from prettytable import PrettyTable
import subprocess
import threading
import discord
from re import match
from discord.ext import tasks
import urllib.request
import html2text
import traceback
from time import perf_counter
import datetime
import math
from decimal import Decimal
import numpy as np
import cv2
import sys
import requests
import shutil
import glob
import zlib
import bot
from puzzle_state import PuzzleState
from algorithm import Algorithm
from analyse import analyse
from draw_state import draw_state
from daily_fmc import DailyFMC
from replit import db

client = discord.Client()
print('\n'.join(db.keys()))
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

#___________GIF_MAKER
def clearImages():
    folder = 'images'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def makeGif(scramble,solution,tps):
    clearImages()
    makeImages(scramble,solution)
    img_array = []
    for filename in glob.glob('images/*.png'):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)
    out = cv2.VideoWriter('movie.webm',cv2.VideoWriter_fourcc(*'VP90'), tps, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
    clearImages()

def makeImages(scramble,solution):
    states = getStates(scramble, solution)
    for n, scr in enumerate(states):
        img = drawPuzzle(scr)
        img.save("images/" + str(n).zfill(5) + ".png", 'PNG')

# _________________________________________________________________________
# ________________solve_anal_project
# 0..3 to 0..15
# def XYtolin(X, Y):
#  N = 4
#  return Y*N + X

# 0..15 to 0..3
def getXY(lin):
    N = 4
    y = int(math.floor(lin / N))
    x = lin % N
    return x, y


# return empty puzzle (matrix from 1 to 16 (0))
def create_puz():
    arr = np.arange(1, 17)
    arr[15] = 0
    blank = 15
    return arr.reshape(4, 4), blank


# scramble matrix with string like slidysim
def scramble_puz(puzzle, scramble):
    blank = 15
    arr = tuple([int(a) for x in scramble.split("/") for a in x.split()])
    for idd, el in enumerate(arr):
        if el == 0:
            blank = idd
        x, y = getXY(idd)
        puzzle[y, x] = el
    return puzzle, blank


# do move, not check if possible, blank 0 id of empty, move - RULD
def move(puzzle, blank, move):
    xb, yb = getXY(blank)
    N = 4
    if move == "R":
        puzzle[yb, xb] = puzzle[yb, xb - 1]
        puzzle[yb, xb - 1] = 0
        blank -= 1
    if move == "L":
        puzzle[yb, xb] = puzzle[yb, xb + 1]
        puzzle[yb, xb + 1] = 0
        blank += 1
    if move == "D":
        puzzle[yb, xb] = puzzle[yb - 1, xb]
        puzzle[yb - 1, xb] = 0
        blank -= N
    if move == "U":
        puzzle[yb, xb] = puzzle[yb + 1, xb]
        puzzle[yb + 1, xb] = 0
        blank += N
    return puzzle, blank


# do moves sequence, like RULD... string, Null if whatever is wrong
def doMoves(puzzle, blank, moves):
    try:
        for i in moves:
            puzzle, blank = move(puzzle, blank, i)
            #print(toScramble(puzzle))
        return puzzle, blank
    except:
        return None, None


# returns true if puzzle is solved
def checkSolved(puzzle):
    s, _ = create_puz()
    return np.array_equal(puzzle, s)


# get slidysim style scramble from array
def toScramble(puzzle):
    scr = ""
    for i in puzzle:
        for j in i:
            scr += str(j) + " "
        scr = scr[:-1] + "/"
    return scr[:-1]


# get scrambled puzzle array
def createScrambled(scramble):
    mypuz, blank = create_puz()
    mypuz, blank = scramble_puz(mypuz, scramble)
    return mypuz, blank


# get states of every move
def getStates(scramble, solution):
    list = []
    mypuz, blank = createScrambled(scramble)
    list.append(scramble)
    for i in solution:
        mypuz, blank = doMoves(mypuz, blank, i)
        list.append(toScramble(mypuz))
    return list
    # return '\n'.join(list)
def getReverse(move):
    if move == "R":
        return "L"
    if move =="L":
        return "R"
    if move =="U":
        return "D"
    if move =="D":
        return "U"
    return None

def getGoodMoves(scramble, size):
    return [x[0] for x in solvers[size].solveGood(scramble)]

def isReverse(a, b):
    return getReverse(a) == b

def analyse(scramble, solution):
    solution = solution.upper()
    states = getStates(scramble,solution)
    if states[len(states)-1] == "1 2 3 4/5 6 7 8/9 10 11 12/13 14 15 0":
        optimals = []
        optl = []
        userlen=len(solution)
        #print('\n'.join(states))
        lastopt=""
        for id,i in enumerate(states):
            print(i)
            user_end_len=userlen-id
            predicted_opt_end_len=len(lastopt)-1
            if lastopt !="" and user_end_len==predicted_opt_end_len:
                opt = lastopt[1:]
            else:
                opt = solvers[4].solveOne(i)
            lastopt=opt
            optimals.append(opt)
            optl.append(len(opt))
        log = "Analysing " + scramble + "\n"
        log += "Your solution " + solution + " [" + str(userlen) + "]\n"
        dif = userlen-optl[0]
        log += "Your solution is [" + str(dif) + "] away from optimal\n"
        log += "Optimal: " + optimals[0] + " [" + str(optl[0]) + "]\n"
        x = PrettyTable()
        x.field_names = ["Move", "State", "Fail", "Your Before","Your Ending","Opt_Ending", "Your_with_Optimal_ending"]
        myrows=[]
        wrongmoves = []
        lasti = -1
        for id, move in enumerate(solution):
            movesdone=id+1
            userlen -= 1
            if userlen != -1:
                row = []
                #dif =  userlen - optl[movesdone]
                optdif = abs(optl[movesdone-1] - optl[movesdone] - 1)
                row.append(move)
                row.append(states[movesdone])
                #row.append(str(dif))
                if optdif == 0:
                    row.append(" ")
                    if len(myrows) > 1 and len(wrongmoves) > 0:
                        lastrow=myrows[len(myrows)-2]
                        movebeforerow=myrows[len(myrows)-1]
                        prev=wrongmoves[len(wrongmoves)-1]
                        #print(str(lastrow[1]==prev[1]) + str(movesdone)+str(lastrow)+str(prev))
                        if isReverse(move,movebeforerow[0]) and lastrow[1]==prev[1]:
                            prev[3]="!"+prev[3]
                else:
                    wrong= []
                    wrong.append(movesdone)
                    wrong.append(states[movesdone-1])
                    wrong.append(solution[:movesdone-1])
                    if movesdone-1 == lasti:
                        prev=wrongmoves[len(wrongmoves)-1]
                        prev[3]="!"+prev[3]
                    wrong.append(move)
                    lasti=movesdone
                    opt=optimals[movesdone-1]
                    wrong.append(opt[:1])
                    wrong.append(solution[movesdone-1:])
                    wrong.append(opt)
                    wrong.append(solution[:movesdone-1] + opt)
                    row.append(str(optdif))
                    wrongmoves.append(wrong)
                your = solution[:movesdone]
                yourend= solution[movesdone:]
                after = optimals[movesdone]
                full=your+after
                if len(your)>10:
                    your = your[:10] + "..."
                if len(yourend)>10:
                    yourend = yourend[:10] + "..."
                if len(after)>10:
                    after = after[:10] + "..."
                row.append(your)
                row.append(yourend + "[" + str(len(solution[movesdone:])) + "]")
                row.append(after + "[" + str(len(optimals[movesdone])) + "]")
                row.append(full)
                myrows.append(row)
        x.add_rows(myrows)

        y = PrettyTable()
        y.field_names = ["N","State","Setup","Move","Better","Your ending","Better ending","Your+opt"]
        y.add_rows(wrongmoves)
        if len(wrongmoves)>0:
            log+="Wrong moves:\n"
            log+=y.get_string() + "\n\n"
    else:
        log = "Something is wrong with your solution"

    return log
# _______________________________________________________________

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


# _______________processing commands in threads with timeout________________________
class Command(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def getSol(self):
        return self.solution

    def run(self, timeout):
        def target():
            print("Thread started")
            self.process = subprocess.Popen(
                "exec " + self.cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            stdout, stderr = self.process.communicate()
            self.solution = str(stdout)

            print("Thread finished")

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            print("Terminating process")
            self.process.kill()
            self.process.terminate()
            self.solution = "Timeout :("
            print("Timeout done")
            thread.join()
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

#_______________for !getprob____________________
def sumAm(a, b, cumA):
    val = 0
    if a > 0:
        val = cumA[b] - cumA[a - 1]
    else:
        val = cumA[b]
    return val


def getProbText(f1, f2, pzlName, nscr):
    f1 = int(f1)
    f2 = int(f2)
    nscr = int(nscr)
    if nscr == 0:
        nscr = 1
    num44 = [
        1,
        2,
        4,
        10,
        24,
        54,
        107,
        212,
        446,
        946,
        1948,
        3938,
        7808,
        15544,
        30821,
        60842,
        119000,
        231844,
        447342,
        859744,
        1637383,
        3098270,
        5802411,
        10783780,
        19826318,
        36142146,
        65135623,
        116238056,
        204900019,
        357071928,
        613926161,
        1042022040,
        1742855397,
        2873077198,
        4660800459,
        7439530828,
        11668443776,
        17976412262,
        27171347953,
        40271406380,
        58469060820,
        83099401368,
        115516106664,
        156935291234,
        208207973510,
        269527755972,
        340163141928,
        418170132006,
        500252508256,
        581813416256,
        657076739307,
        719872287190,
        763865196269,
        784195801886,
        777302007562,
        742946121222,
        683025093505,
        603043436904,
        509897148964,
        412039723036,
        317373604363,
        232306415924,
        161303043901,
        105730020222,
        65450375310,
        37942606582,
        20696691144,
        10460286822,
        4961671731,
        2144789574,
        868923831,
        311901840,
        104859366,
        29592634,
        7766947,
        1508596,
        272198,
        26638,
        3406,
        70,
        17,
    ]
    num33 = [
        1,
        2,
        4,
        8,
        16,
        20,
        39,
        62,
        116,
        152,
        286,
        396,
        748,
        1024,
        1893,
        2512,
        4485,
        5638,
        9529,
        10878,
        16993,
        17110,
        23952,
        20224,
        24047,
        15578,
        14560,
        6274,
        3910,
        760,
        221,
        2,
    ]
    maxStates4 = 10461394944000
    maxStates3 = 181440
    if pzlName == "3x3":
        numTable = num33
        pzlMaxStates = maxStates3
    if pzlName == "4x4":
        numTable = num44
        pzlMaxStates = maxStates4
    limitNum = len(numTable) - 1
    # print(limitNum)
    if f1 < 0:
        f1 = 0
    if f2 < 0:
        f1 = 0
        f2 = 0
    if f1 > limitNum:
        f1 = limitNum
        f2 = limitNum
    if f2 > limitNum:
        f2 = limitNum
    if f1 > f2:
        f1, f2 = f2, f1
    out = ""
    cumP = []
    cumA = []
    sum = 0
    maxV = len(numTable)
    for i in range(0, maxV):
        sum += numTable[i]
        cumA.append(sum)
        cumP.append(100 * (sum / pzlMaxStates))
    rp = getRangeP(f1, f2, cumP)
    out += "The probability of " + bl(pzlName) + " puzzle being optimally solved in "
    if f1 != f2:
        out += "range from " + bl(f1) + " to " + bl(f2) + " moves is "
    else:
        out += "*exactly* " + bl(f1) + " moves is "
    out += editP(rp)

    out += (
        "\n(since there are "
        + bl(sumAm(f1, f2, cumA))
        + " states in that range of total "
        + str(pzlMaxStates)
        + " states of this puzzle)"
    )
    pSc = (1 - ((1 - rp / 100) ** nscr)) * 100
    # sc = str(pSc)
    out += (
        "\nThe probability of getting at least one scramble within that range after "
        + bl(str(nscr))
        + " scrambles is "
        + editP(pSc)
    )
    # print(nscr)
    # if nscr > 100:
#    maxi = 1
#    maxFind = min(1000, nscr)
#    for i in range(1, maxFind):
#        ber = bernully(i, nscr, rp)
#        maxi = i
#        if ber != "[Very small]":
#            break
#    if bernully(maxi, nscr, rp) == "[Very small]":
#        out += (
#            "```Sorry, can't find chance of getting scramble exactly "
#            + str(maxi)
#            + " times after "
#            + str(nscr)
#            + " solves, it's still very small```"
#        )
#    else:
#        out += "```"
#        lasti = maxi + 17
#        for i in range(maxi, lasti):
#            berv = bernully(i, nscr, rp)
#            if berv == "1 in i":
#                berv = "[Very big]"
#            out += (
#                "\nChance of getting scramble exactly "
#                + str(i)
#                + " times after "
#                + str(nscr)
#                + " solves is "
#                + berv
#            )
#        out += "```"
    out += "\n\nCheck this: https://dphdmn.github.io/15puzzleprob/"
    return out


def bernully(k, n, p):  # k times in n tests, prob = p
    p = p / 100
    x1 = math.comb(n, k)
    x2 = p ** k
    x3 = (1 - p) ** (n - k)
    value = Decimal(x1) * Decimal(x2) * Decimal(x3)
    # print(bl(str(round(float(Decimal(100) / Decimal(value)), 0))))
    return editP(value * 100).replace("*", "")


def getRangeP(a, b, cumP):
    val = 0
    if a > 0:
        val = cumP[b] - cumP[a - 1]
    else:
        val = cumP[b]
    return val


def bl(s):
    return "**" + str(s) + "**"


def editP(rp):
    out = ""
    if rp == 0:
        return "[Very small]"
    if rp < 1:
        out += "1 in " + bl(str(round(float(Decimal(100) / Decimal(rp)), 0))[:-2])
    else:
        out += bl(str(round(float(rp), 2))) + "%"
    return out

#_________________daily fmc
def getFMCstatus():
    try:
        status = db["daily_status.txt"]
        return "CLOSED" in status #true if you can start
    except:
        return True



def checkSol(scramble, solution):
    result = False
    try:
        st = getStates(scramble,solution)
        #print(scramble, solution, st)
        result = (st[len(st)-1] == "1 2 3 4/5 6 7 8/9 10 11 12/13 14 15 0")
    except:
        result = False
    return result


def getDailyStats():
    return db["daily_status.txt"].splitlines()


def fixSolution(solution):
    words = solution
    words = words.replace("R3", "RRR")
    words = words.replace("R2", "RR")
    words = words.replace("L3", "LLL")
    words = words.replace("L2", "LL")
    words = words.replace("U3", "UUU")
    words = words.replace("U2", "UU")
    words = words.replace("D3", "DDD")
    words = words.replace("D2", "DD")
    return words

def rewriteFile(file, text):
    f = open(file, "w+")
    f.write(text)
    f.close()

def removeResult(name):
    text = db["daily_log.txt"].splitlines()
    newtext = ""
    name = name + "\t"
    for i in text:
        if not (name in i):
          newtext+= i + "\n"
    db["daily_log.txt"] = newtext


def readLog():
    try:
        text = db["daily_log.txt"].splitlines()
    except:
        text = ""
        db["daily_log.txt"] = ""
        print("DAILY LOG IS EMPTY ERROR")
    logdata = []
    for i in text:
        rowlist = i.split("\t")
        logdata.append({"Name":rowlist[0],"Solution": rowlist[1], "Len": rowlist[2]})
    return logdata


def addFMCResult(name, solution):
    text = name + "\t" + solution + "\t" + str(len(solution)) + "\n"
    appendDB("daily_log.txt", text)
    rewriteFile("daily_backup.txt", db["daily_log.txt"])

def appendDB(key, text):
    dbtext = db[key]
    dbtext += text
    db[key] = dbtext

def appendFile(file, text):
    f = open(file, 'a')
    f.write(text)
    f.close()

#____________________________discord started
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
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
    fmc = DailyFMC(client, int(os.environ["daily_fmc_channel"]))
    fmc.start()

@client.event
async def on_message(message):
    namea = str(message.author)
    if message.author == client.user:
        return
    if "pls" in message.content.lower():
        await message.add_reaction("eff:803888415858098217")
    if match("<@!?809437517564477522>", message.content) is not None:
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
    if message.content.startswith("!daily_scramble"):
        if getFMCstatus():
            await message.channel.send("No FMC challange is going on")
        else:
          stats = getDailyStats()
          out = "Current FMC scramble: " + stats[0] + "\nMoves: " + stats[2]
          await message.channel.send(out)
    if message.content.startswith("!daily_close"):
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Sorry you are not FMC manager.")
        else:
            await fmc.close()
    if message.content.startswith("!submit"):
        if getFMCstatus():
            await message.channel.send("Sorry, there is no FMC competition now.")
        else:
            name = message.author.name
            contentArray = message.content.split(" ")
            await message.delete()
            if len(contentArray) != 2:
                await message.channel.send("Sorry, " + name + ", I can't get your solution")
            else:
                solution = Algorithm(contentArray[1])
                await fmc.submit(name, solution)
    if message.content.startswith("!daily_open"):
        if not message.author.guild_permissions.administrator:
            await message.channel.send("Sorry you are not FMC manager.")
        else:
            await fmc.open()
    if message.content.startswith("!getlb"):
        await makeTmpSend("prettylb.txt", db["prettylb.txt"], "Leaderboard for ranks: ", message.channel)
    if message.content.startswith("!wrupdate"):
        if message.author.guild_permissions.administrator:
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
            getLeaderboard()
            webpage = os.environ["webpage"]
            msg = f"Check this: {webpage}\nProbably updated! Try !getpb command:"
            await makeTmpSend("smartboard.txt", db["smartboard.txt"], msg, message.channel)
            db["lastupdate"] = datetime.datetime.now().timestamp()
        except:
            print(traceback.format_exc())
            await message.channel.send("Sorry, something is wrong")
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
        except:
            await message.channel.send(
                "Something is wrong\n```" + traceback.format_exc() + "```"
            )
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
        except:
            await message.channel.send(
                "Something is wrong\n```" + traceback.format_exc() + "```"
            )
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
        except:
            await message.channel.send(
                "Please specify the puzzle size, for example: !getpb dphdmn 4x4"
            )
    if message.content.startswith("!animate"):
        try:
            contentArray = message.content.split("\n")
            await message.channel.send("Working on it! It may take some time, please wait")
            scramble = contentArray[1]
            solution = contentArray[2]
            if len(contentArray) == 4:
                tps = float(contentArray[3])
            else:
                tps = 10
            words = solution
            words = words.replace("R3", "RRR")
            words = words.replace("R2", "RR")
            words = words.replace("L3", "LLL")
            words = words.replace("L2", "LL")
            words = words.replace("U3", "UUU")
            words = words.replace("U2", "UU")
            words = words.replace("D3", "DDD")
            words = words.replace("D2", "DD")
            solution = words
            makeGif(scramble,solution, tps)
            with open("movie.webm", "rb") as f:
                picture = discord.File(f)
                await message.channel.send("Solution for " + scramble + " by " + message.author.mention + "\n" + str(len(solution)) + " moves (May not be optimal)\nTPS (playback): "+str(tps) +"\nTime (playback): "+ str(round(len(solution)/tps,3)) , file=picture)
            os.remove("movie.webm")
        except Exception as e:
            print(traceback.print_exc())
            await message.channel.send("Sorry, something is wrong")
    if message.content.startswith("!analyse"):
        await message.channel.send("Working on it!")
        try:
            contentArray = message.content.split("\n")
            scramble = PuzzleState(contentArray[1])
            solution = Algorithm(contentArray[2])
            out = analyse(scramble, solution)
        except Exception as e:
            out = "Something is wrong with your inputs"
            print(str(e))
        f = open("analysis.txt", "w+")
        f.write(out)
        f.close()
        with open("analysis.txt", "rb") as f:
            txt = discord.File(f)
            await message.channel.send("Your analysis: ", file=txt)
        os.remove("analysis.txt")
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
            await message.channel.send("Something is wrong\n```" + repr(e) + "```")
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
        except:
            await message.channel.send(
                "Please specify the puzzle size, for example: !getreq ascended 4x4"
            )
    if message.content.startswith("!getprob"):
        #!getprob 4x4 30 40 1000, or !getprob 4x4 30 40, or !getprob 4x4 30
        try:
            examples = "- !getprob <puzzle> <moves> [<moves>, <amount> || <amount] - get probability of getting N moves optimal scramble\nCommand examples:\n```!getprob 4x4 30 - get probability for 4x4 in 30 moves\n!getprob 4x4 30 40 - get probability for 4x4 from 30 to 40 moves\n!getprob 4x4 30 40 _1000 - from 30 to 40 moves, repeat 1000 times (default 100)\n!getprob 4x4 30 _1000 - 30 moves, repeat 1000 times\n!getprob 3x3 20 - 3x3 puzzle```\n"
            contentArray = message.content.lower().split(" ")
            arraylen = len(contentArray)
            if arraylen == 1:
                await message.channel.send(examples)
            elif arraylen == 2:
                examples = "Command should have at least 3 words in it.\n" + examples
                await message.channel.send(examples)
            elif arraylen == 3:
                pzlName = contentArray[1]
                if pzlName == "3x3" or pzlName == "4x4":
                    num = contentArray[2]
                    if num.isdigit():
                        f1 = num
                        f2 = num
                        await message.channel.send(getProbText(f1, f2, pzlName, 100))
                    else:
                        examples = (
                            "Something is wrong with your range number, most be positive integer.\n"
                            + examples
                        )
                        await message.channel.send(examples)
                else:
                    examples = (
                        "Something is wrong with your puzzle size (must be 4x4 or 3x3)\n"
                        + examples
                    )
                    await message.channel.send(examples)
            else:
                pzlName = contentArray[1]
                if pzlName == "3x3" or pzlName == "4x4":
                    if (
                        arraylen == 4
                    ):  # expect number and amount rep OR number and second number
                        num = contentArray[2]
                        if num.isdigit():
                            otherThing = contentArray[3]
                            if (
                                otherThing[:1] == "_"
                            ):  # thiking that this is number and amount of rep
                                num2 = otherThing[1:]
                                if num2.isdigit():
                                    await message.channel.send(
                                        getProbText(num, num, pzlName, num2)
                                    )
                                else:
                                    examples = (
                                        "Something is wrong with your range number, most be positive integer.\n"
                                        + examples
                                    )
                                    await message.channel.send(examples)
                            else:  # thinking that this number is just the 2nd range number
                                num2 = otherThing
                                if num2.isdigit():
                                    await message.channel.send(
                                        getProbText(num, num2, pzlName, 100)
                                    )
                                else:
                                    examples = (
                                        "Something is wrong with your range number, most be positive integer.\n"
                                        + examples
                                    )
                                    await message.channel.send(examples)
                        else:
                            examples = (
                                "Something is wrong with your range number, most be positive integer.\n"
                                + examples
                            )
                            await message.channel.send(examples)
                    else:  # we have 5 inputs
                        num1 = contentArray[2]
                        num2 = contentArray[3]
                        num3 = contentArray[4]
                        trueNum3 = num3
                        if num3[:1] == "_":
                            trueNum3 = num3[1:]
                        if num1.isdigit() and num2.isdigit() and trueNum3.isdigit():
                            await message.channel.send(
                                getProbText(num1, num2, pzlName, trueNum3)
                            )
                        else:
                            examples = (
                                "Something is wrong with your range number, most be positive integer.\n"
                                + examples
                            )
                            await message.channel.send(examples)
                else:
                    examples = (
                        "Something is wrong with your puzzle size (most be 4x4 or 3x3)\n"
                        + examples
                    )
                    await message.channel.send(examples)
        except:
            await message.channel.send(
                "Something is wrong\n```" + traceback.format_exc() + "```"
            )
    if "scrable" in message.content.lower():
        await message.channel.send("Infinity tps, " + message.author.mention + "?")
        await message.add_reaction("0️⃣")
    if message.content.startswith("!paint"):
        good = False
        try:
            img_data = requests.get(message.attachments[0].url).content
            good = True
        except:
            await message.channel.send(
                "Please add image file! (URL does not work, upload it, or paste like an image)"
            )
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
        words = message.content[5:]
        words = words.replace("R", "_")
        words = words.replace("L", "R")
        words = words.replace("_", "L")
        words = words.replace("U", "_")
        words = words.replace("D", "U")
        words = words.replace("_", "D")
        words = words.replace(" ", "")
        await message.channel.send("Changed notation moves:\n||" + words + "||")
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
        except:
            await message.channel.send("Something is wrong")
    if message.content.startswith("!savecmp"):
        if message.author.guild_permissions.administrator:
            today = str(datetime.datetime.today().strftime('%Y-%m-%d'))
            db["SMARTanon"] = db["SMART"+today]
            await message.channel.send("Saved to anon!")
        else:
            await message.channel.send("Sorry, you are not admin")
    if message.content.startswith("!anoncmp"):
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
    if message.content.startswith("!compare"):
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
    if message.content.startswith("!cmp1"):
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
    if message.content.startswith("!cmp2"):
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
    if message.content.startswith("!movesgame"):
        scramble = scrambler.getScramble(4)
        img = drawPuzzle(scramble)
        img.save('scramble.png', 'PNG')
        with open("scramble.png", "rb") as f:
            picture = discord.File(f)
            await message.channel.send("Check this: https://dphdmn.github.io/movesgame/\nFind good move at this scramble: \n" + scramble + "\nYou will get answer in few seconds", file=picture)
        os.remove("scramble.png")
        goodmoves = getGoodMoves(scramble, 4)
        goodmovesmessage=""
        for j in ["R","U","L","D"]:
            if j in goodmoves:
                goodmovesmessage+= "**"+j+"**" +" \tis \t**OK!**\t move\n"
            else:
                goodmovesmessage+= ""+j+"" +" \tis \tbad\t move\n"
        await message.channel.send("\n" + "||" + goodmovesmessage + "||")
    if message.content.startswith("!goodm"):
        try:
            scramble = message.content[7:]
            if len(scramble) == 37:
                size = 4
            elif len(scramble) == 17:
                size = 3
            goodmoves = getGoodMoves(scramble, size)
            await message.channel.send("Your scramble:\n"+scramble+"\nGood moves for your scramble: " + ' or '.join(goodmoves))
        except:
            print(traceback.format_exc())
            await message.channel.send("Sorry, something is wrong")
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
            except:
                await message.channel.send("Sorry, can't solve it.")
        else:
            print(len(scramble))
            await message.channel.send("Your scramble is wrong.")
    if message.content.startswith("!solve") or message.content.startswith("!video"):
        try:
            solve = message.content.startswith("!solve")
            video = message.content.startswith("!video")

            scramble = PuzzleState(message.content[7:])
            size = scramble.size()

            if size == (4, 4) or (size == (3, 3) and solve):
                a = perf_counter()
                solver = solvers[size[0]]
                solution = solver.solveOne(scramble)
                b = perf_counter()

                outm = "Solution for: " + scramble.to_string() + "\n"
                outm += "||" + solution.to_string() + "||\n"
                outm += "Moves: " + str(solution.length()) + "\n"
                outm += "Time: " + str(round((b - a), 3))

                if video:
                    outm += "\nPlease wait! I'm making a video for you!"

                await message.channel.send(outm)

                if video:
                    makeGif(scramble, solution, 10)
                    with open("movie.webm", "rb") as f:
                        picture = discord.File(f)
                        await message.channel.send("Solution for " + scramble + "\nOptimal: " + str(len(solution)) + " moves", file=picture)
                    os.remove("movie.webm")
            else:
                await message.channel.send(
                    "Sorry, something is wrong with your scramble"
                )
        except Exception as e:
            await message.channel.send("Something is wrong\n```" + str(e) + "```")
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
