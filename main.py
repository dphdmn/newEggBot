import scrambler
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
import random
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
from PIL import Image, ImageDraw, ImageFont
import glob

client = discord.Client()

def solvereverse(words):
  words = words.replace("R3", "RRR")
  words = words.replace("R2", "RR")
  words = words.replace("L3", "LLL")
  words = words.replace("L2", "LL")
  words = words.replace("U3", "UUU")
  words = words.replace("U2", "UU")
  words = words.replace("D3", "DDD")
  words = words.replace("D2", "DD")
  words = words.replace("R", "_")
  words = words.replace("L", "R")
  words = words.replace("_", "L")
  words = words.replace("U", "_")
  words = words.replace("D", "U")
  words = words.replace("_", "D")
  words = words[::-1]
  return words

#_______________________________Auto leaderboard

def getLeaderboard():
  my_secret = os.environ['slidysim']
  r = requests.post(my_secret, data = {'width':'-1',
'height':'-1',
'solvetype':'any',
'displaytype':'Standard',
'avglen':'-1',
'pbtype':'time',
'sortby':'time',
'controls':'km',
'user':'',
'solvedata':0,
'version':'28.3'})

  data = r.text.split("<br>")
  data = data[1:-1]
  solvesdata = []
 #goodPuzzles=["3x3","4x4","5x5","6x6","7x7","8x8","9x9","10x10"]
 # goodModes=["Standard","2-N relay", "Marathon 10", "Marathon 42"]
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
        }
    )
  reqstring = readFilenormal("tiers.txt").splitlines()
  req=[]
  tier_cost = readFile("tier_cost.txt").split("\t")
  for id, item in enumerate(tier_cost):
    tier_cost[id] = int(item)
  tier_limits = readFile("tier_limits.txt").split("\t")
  for id, item in enumerate(tier_limits):
    tier_limits[id] = int(item)   
  id = 0
  tierNames=["Unranked"]
  for i in reqstring:
    i = i.split("\t")
    tierNames.append(i[0])
    req.append({"Tiercost":tier_cost[id], "Scores": i[1:], "TierID":id+1})
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
    myhtml+="<div class=\"st_wrap_table\" data-table_id=\"" + str(id+1)+"\">\n"
    myhtml+="<header class=\"st_table_header\">\n"
    myhtml+="<h2>"
    myhtml+= tier
    myhtml+="</h2>\n"
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
  f = open("leaderboard.txt", "w+")    
  f.write(string)
  f.close()
  f = open("smartboard.txt", "w+")    
  f.write(smartstring)
  f.close()
  f = open("prettylb.txt", "w+")    
  f.write(y.get_string())
  f.close()
  f = open("templates/egg.html", "w+")   
  f.write(myhtml)
  f.close()
  updatehtml()

def updatehtml():
   f = open("templates/index.html", "w+")    
   f.write(readFilenormal("templates/header.html"))
   f.write(readFilenormal("templates/egg.html"))
   f.write(readFilenormal("templates/footer.html"))
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

def makeImages(scramble,solution):
  states = getStates(scramble, solution)
  for n, scr in enumerate(states):
    img = drawPuzzle(scr)
    img.save("images/" + str(n).zfill(5) + ".png", 'PNG')

#________________________________SCRAMBLE DRAWER

def color(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def makeImage(w, h):
    img = Image.new("RGB", (w, h))
    return img, ImageDraw.Draw(img, 'RGBA')

def drawSquare(img,x,y,r,color):
    shape = [(x, y), (x+r, y+r)]
    img.rectangle(shape, fill=color)
    return img


def drawTile(im, draw, pos, col, text):
    size = 100
    xP, yP = getXY(pos)
    x = xP*size
    y = yP*size
    font = ImageFont.truetype("font.ttf", int(size/2))
    W = size
    H = size
    w, h = draw.textsize(text,font=font)
    if text != "0":
        drawSquare(draw, x, y, size, col)
        draw.text(((W-w)/2+x,(H-h)/2+y), text, fill="black", font=font)
    else:
        mask = Image.new('L', im.size, color=255)
        mask_d = ImageDraw.Draw(mask)
        drawSquare(mask_d, x, y, size, 0)
        im.putalpha(mask)


def drawTiles(puz):
    img, draw = makeImage(400, 400)
    pos = 0
    tileColors = [color(255, 103, 103),
                  color(255, 163, 87),
                  color(255, 241, 83),
                  color(193, 255, 87),
                  color(123, 255, 97),
                  color(107, 255, 149),
                  color(121, 255, 222),
                  color(131, 230, 255),
                  color(139, 178, 255),
                  color(154, 141, 255),
                  color(207, 141, 255),
                  color(255, 133, 251)]
    colorCords = [10, 0, 0, 0, 0, 2, 4, 4, 4, 2, 6, 8, 8, 2, 6, 9]
    for i, row in enumerate(puz):
        for j in row:
            cord = colorCords[j]
            mycolor = tileColors[cord]
            drawTile(img, draw, pos, mycolor, str(j))
            pos += 1
    return img

def drawPuzzle(scramble):
    puz, _ = create_puz()
    puz, blank = scramble_puz(puz, scramble)
    img = drawTiles(puz)
    return img

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

def getGoodMoves(scramble):
  states = get4state(scramble)
  #opt = solveSimple(scramble)
  solves = []
  lens = []
  for i in states:
    sol=solveSimple(i[1])
    print(i[1])
    solves.append(i[0])
    lens.append(len(sol))
  min_value = min(lens)
  idlist=[]
  for id, i in enumerate(lens):
    if min_value == i:
      idlist.append(id)
  goodmoves=[]
  for i in idlist:
    goodmoves.append(solves[i])
  return goodmoves

def bannedmove(blank, move):
  if move == "R":
    return blank in [0,4,8,12]
  if move == "L":
    return blank in [3,7,11,15]
  if move == "D":
    return blank in [0,1,2,3]
  if move == "U":
    return blank in [12,13,14,15]

def getLegalmoves(blank):
  list=[]
  if not bannedmove(blank,"R"):
    list.append("R")
  if not bannedmove(blank,"U"):
    list.append("U")
  if not bannedmove(blank,"L"):
    list.append("L")
  if not bannedmove(blank,"D"):
    list.append("D") 
  return list

def get4state(scramble):
  list = [] 
  puzzle, blank = createScrambled(scramble)
  legalmoves=getLegalmoves(blank)
  print("legal moves" + str(legalmoves))
  for i in legalmoves:
    puzzle, blank = createScrambled(scramble)
    puz, _ =  move(puzzle, blank, i)
    list.append((i, toScramble(puz)))

  return list  

def isReverse(a, b):
  return getReverse(a) == b
def solveSimple(scramble):
  my_com = "./solver2 " + '"' + scramble + '"'
  print(my_com)
  cmd = my_com
  process = subprocess.Popen("exec " + cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
  stdout, stderr = process.communicate()
  sol = str(stdout)
  sol = sol.replace("b'","").replace("\\n'","")
  print(sol)
  return sol

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
        opt = solveSimple(i)
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
 # log+="Full log:\n"
 # log+=x.get_string()
  
  return log
# _______________________________________________________________

# ______________8 optimal solver____________
def solve8(scramble):
    searchfile = open("all_solutions.txt", "r")
    for line in searchfile:
        if scramble in line:
            searchfile.close()
            return line
    searchfile.close()
    return "That does not look like a scramble to me, example of a valid scramble: 0 7 8/2 3 6/4 1 5"


# _____________compare tables___________________
def readFilenormal(name):
    with open(name, "r") as file:
        mystr = file.read()
    return mystr
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
            list.append(
                {
                    "Name": i[0],
                    "Place": i[1],
                    "Power": i[2],
                    "Rank": rankNames[rankN],
                    "rankID": rankN,
                    "Scores": i[3:],
                }
            )
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
    reqstring = readFile("tiers.txt").splitlines()
    id = 0
    for i in reqstring:
        i = i.split("\t")
        id += 1
        req.append({"Tier": i[0].upper(), "rankID": id, "Scores": i[1:]})
        rankNames.append(i[0].upper())
    req.reverse()
    tier_limits = readFile("tier_limits.txt").split("\t")
    for id, item in enumerate(tier_limits):
        tier_limits[id] = int(item)
    textinfo1 = fixSpaces(readFile(name1)).splitlines()
    textinfo2 = fixSpaces(readFile(name2)).splitlines()

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
                #print("".join(item_old["Scores"]).upper())
                #print("".join(item_new["Scores"]).upper())
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
#____________________________discord started
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

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
    if "!spam" in message.content.lower():
        if message.author.guild_permissions.administrator:
            shit = message.content[6:]
            msg = ""
            for x in range(3000):
                msg += shit + " "
            spam.start(message.channel, msg[:2000])
    if "!getlb" in message.content.lower():
      with open("prettylb.txt", "rb") as f:
          txt = discord.File(f)
          await message.channel.send("Leaderboard for ranks: ", file=txt)
    if "!update" in message.content.lower():
      await message.channel.send("Wait for it!")
      try:
        getLeaderboard()
        with open("smartboard.txt", "rb") as f:
          txt = discord.File(f)
          await message.channel.send("Check this: https://eggserver.dphdmntranquilc.repl.co/\nProbably updated! Try !getpb command: ", file=txt)
      except:
        print(traceback.format_exc())
        await message.channel.send("Sorry, something is wrong")
    if "!stop" in message.content.lower():
        if message.author.guild_permissions.administrator:
            spam.cancel()
    if "!getreal" in message.content.lower():
      scramble = scrambler.getScramble(4)
      await message.channel.send("Please wait! I am slow, use ben's scrambler instead: http://benwh.000webhostapp.com/software/15poprs/index.html")
      solution = solveSimple(scramble)
      rever = solvereverse(solution)
      mypuz, blank = create_puz()
      out = "DDDRUURDDRUUULLL" + rever
      mypuz, _ = doMoves(mypuz, blank, out)
      out = " ".join(list(out))
      out = out.replace("D D D", "D3")
      out = out.replace("D D", "D2")
      out = out.replace("L L L", "L3")
      out = out.replace("L L", "L2")
      out = out.replace("U U U", "U3")
      out = out.replace("U U", "U2")
      out = out.replace("R R R", "R3")
      out = out.replace("R R", "R2")
      scr=toScramble(mypuz)
      img = drawPuzzle(scr)
      img.save('scramble.png', 'PNG')
      with open("scramble.png", "rb") as f:
        picture = discord.File(f)
        await message.channel.send("Your scramble: \n" + out + "\n" +scr, file=picture)      
    if "!getscramble" in message.content.lower():
      contentArray = message.content.lower().split(" ")
      n = 4
      if len(contentArray)>1:
        n = int(contentArray[1])
      scramble = scrambler.getScramble(n)
      if n == 4:
        img = drawPuzzle(scramble)
        img.save('scramble.png', 'PNG')
        with open("scramble.png", "rb") as f:
          picture = discord.File(f)
          await message.channel.send("Your random 4x4 scramble: \n" + scramble, file=picture)
      else: 
        await message.channel.send("Random scramble for " + str(n) + "x" + str(n) + " puzzle\n" + scramble)
    if "!getwr" in message.content:
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
    if "!wrsby" in message.content:
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
                else:
                  await message.channel.send("```" + my_string + "```")
        except:
            await message.channel.send(
                "Something is wrong\n```" + traceback.format_exc() + "```"
            )
    if "!getpb" in message.content:
        with open("leaderboard.txt", "r") as file:
            mystr = file.read().lower()  # .replace('\n', '')
        # print(mystr)
        filedate = str(mod_date("leaderboard.txt")).split(" ")[0]
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
                outputString += "\nLast time update: " + filedate
                # print(outputString)
                await message.channel.send(outputString)
        except:
            await message.channel.send(
                "Please specify the puzzle size, for example: !getpb dphdmn 4x4"
            )
    if "!animate" in message.content:
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
      except Exception as e:
        #print(e)
        print(traceback.print_exc())
        await message.channel.send("Sorry, something is wrong")
    if "!analyse" in message.content:
      if message.author.guild_permissions.administrator:
        await message.channel.send("Working on it!")
        try:
          contentArray = message.content.split("\n")
          scramble = contentArray[1]
          solution = contentArray[2]
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
          out = analyse(scramble, solution)
        except Exception as e:
          out="Something is wrong with your inputs"
          print(str(e))
        f = open("anal.txt", "w+")
        f.write(out)
        f.close()
        with open("anal.txt", "rb") as f:
          txt = discord.File(f)
          await message.channel.send("Your analysis: ", file=txt)
      else:
        await message.channel.send("Sorry you are not admin")
    if "!draw" in message.content.lower():
      try:
        scramble=message.content[6:]
        img = drawPuzzle(scramble)
        img.save('scramble.png', 'PNG')
        with open("scramble.png", "rb") as f:
          picture = discord.File(f)
          await message.channel.send("Your scramble: ", file=picture)
      except:
        await message.channel.send("Something is wrong, sorry")
    if "!getreq" in message.content:
        with open("tiers.txt", "r") as file:
            mystr = file.read().lower()  # .replace('\n', '')
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
    if (
        "!getprob" in message.content.lower()
    ):  #!getprob 4x4 30 40 1000, or !getprob 4x4 30 40, or !getprob 4x4 30
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
            # getProbText(f1, f2, pzlName, nscr)
        except:
            await message.channel.send(
                "Something is wrong\n```" + traceback.format_exc() + "```"
            )
    if "!ip" in message.content.lower():
        try:
            fp = urllib.request.urlopen("https://2ip.ru/")
            mybytes = fp.read()
            mystr = mybytes.decode("utf8")
            mystr = html2text.html2text(mystr)
            mystr = mystr.splitlines()
            fp.close()
            username = "Ваш IP адрес"
            matching = [s for s in mystr if username in s]
            # my_string = ';\n'.join(matching)
            await message.channel.send(
                mystr[mystr.index(matching[0]) + 2].replace("__", "")
            )
            await message.channel.send(
                "It's not my ip probably. My actual ip at 21.05.2021 was 128.71.69.147 but you probably don't need it"
            )
        except:
            await message.channel.send(
                "Something is wrong\n```" + traceback.format_exc() + "```"
            )
    if "scrable" in message.content.lower():
        await message.channel.send("Infinity tps, " + message.author.mention + "?")
        await message.add_reaction("0️⃣")
    if "!osu" in message.content:
        await message.channel.send(
            "Osu command probably is not working, why using it tho, it's sliding puzzle server"
        )
    if "!paint" in message.content.lower():
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
    if "!rev" in message.content.lower():
        words = message.content[5:]
        wrods = solvereverse(words)
        await message.channel.send("Reversed moves:\n||" + words + "||")
    if "!not" in message.content.lower():
        words = message.content[5:]
        words = words.replace("R", "_")
        words = words.replace("L", "R")
        words = words.replace("_", "L")
        words = words.replace("U", "_")
        words = words.replace("D", "U")
        words = words.replace("_", "D")
        words = words.replace(" ", "")
        await message.channel.send("Changed notation moves:\n||" + words + "||")
    if "!tti" in message.content.lower():
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
        except:
            await message.channel.send("Something is wrong")
    if "!compare" in message.content.lower():
        out = comparelist("file1.txt", "file2.txt")
        if len(out) > 1900:
            f = open("compare.txt", "w+")
            f.write(out)
            f.close()
            with open("compare.txt", "rb") as f:
                txt = discord.File(f)
                await message.channel.send("Your cmp: ", file=txt)
        else:
            await message.channel.send("```" + out + "```")
    if "!cmp1" in message.content.lower():
        good = False
        try:
            text = requests.get(message.attachments[0].url).content.decode("utf-8")
            # print(message.attachments)
            good = True
        except:
            await message.channel.send("Can't get file")
        if good:
            f = open("file1.txt", "w+")
            f.write(text)
            f.close()
            await message.channel.send("Probably updated")
    if "!cmp2" in message.content.lower():
        good = False
        try:
            text = requests.get(message.attachments[0].url).content.decode("utf-8")
            # print(message.attachments)
            good = True
        except:
            await message.channel.send("Can't get file")
        if good:
            f = open("file2.txt", "w+")
            f.write(text)
            f.close()
            await message.channel.send("Probably updated")
    if "!movesgame" in message.content.lower():
      
      scramble = scrambler.getScramble(4)
      img = drawPuzzle(scramble)
      img.save('scramble.png', 'PNG')
      with open("scramble.png", "rb") as f:
        picture = discord.File(f)
        await message.channel.send("Find good move at this scramble: \n" + scramble + "\nYou will get answer in few seconds", file=picture)
      goodmoves = getGoodMoves(scramble)
      goodmovesmessage=""
      for j in ["R","U","L","D"]:
        if j in goodmoves:
          goodmovesmessage+= "**"+j+"**" +" \tis \t**OK!**\t move\n"
        else:
          goodmovesmessage+= ""+j+"" +" \tis \tbad\t move\n"
      await message.channel.send("\n" + "||" + goodmovesmessage + "||")
    if "!goodm" in message.content.lower():
      try:
        scramble = message.content[7:]
        goodmoves = getGoodMoves(scramble)
        await message.channel.send("Your scramble:\n"+scramble+"\nGood moves for your scramble: " + ' or '.join(goodmoves))
      except:
        print(traceback.format_exc())
        await message.channel.send("Sorry, something is wrong")
    if "!solve" in message.content.lower() or "!video" in message.content.lower():
        try:
            solve = "!solve" in message.content.lower()
            video = "!video" in message.content.lower()

            thingy = message.content[7:]
            if len(thingy) == 37:
                await message.channel.send(
                    "Hello, i am solving your scramble, please wait 30s before trying another scramble."
                )
                a = perf_counter()
                my_com = "./solver2 " + '"' + thingy + '"'
                solution = ""
                print(my_com)
                cmd = my_com
                command = Command(cmd)
                command.run(timeout=30)
                solution = command.getSol()
                b = perf_counter()
                if solution == "":
                    await message.channel.send(
                        "Uh sorry, that scramble is very hard (30s) :( "
                    )
                else:
                    print(solution)
                    solution = solution.replace("b", "")
                    solution = solution.replace(" ", "")
                    solution = solution.replace("\\r\\n", "\n")
                    solution = solution.replace("'", "")
                    solution = solution.replace("\\n", "")
                    outm = "Solution for: " + thingy + "\n"
                    outm += solution + "\n"
                    outm += "Moves: " + str(len(solution)) + "\n"
                    outm += "Time: " + str(round((b - a), 3))
                    if video:
                        outm += "\nPlease wait! I'm making a video for you!"
                    await message.channel.send(outm)
                    if video:
                        makeGif(thingy, solution, 10)
                        with open("movie.webm", "rb") as f:
                            picture = discord.File(f)
                            await message.channel.send("Solution for " + thingy + "\nOptimal: " + str(len(solution)) + " moves", file=picture)
            elif solve:
                if len(thingy) == 17:
                    await message.channel.send(solve8(thingy).replace(", ", "\n"))
                else:
                    await message.channel.send(
                        "Sorry, something is wrong with your scramble"
                    )
        except Exception as e:
            await message.channel.send("Something is wrong\n```" + str(e) + "```")
    if "!help" in message.content.lower():
        await message.channel.send(
            "Egg bot commands:\nhttps://discord.com/channels/800441014611214337/800505933137707052/809695325203333140"
        )


@tasks.loop(seconds=1)
async def spam(chan, msg):
    await chan.send(msg)


keep_alive()
try:
    client.run(os.environ["eggkey"])
except:
    req = requests.get("https://discord.com/api/path/to/the/endpoint")
    print(req.text)
