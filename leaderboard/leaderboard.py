import os
import requests
from categories import categories

def get_leaderboard(width=-1, height=-1, solvetype="any", avglen=-1, user=""):
    url = os.environ['slidysim']
    r = requests.post(url, data = {
        "width"       : width,
        "height"      : height,
        "solvetype"   : solvetype,
        "displaytype" : "Standard",
        "avglen"      : avglen,
        "pbtype"      : "time",
        "sortby"      : "time",
        "controls"    : "km",
        "user"        : user,
        "solvedata"   : 0,
        "version"     : "28.3"
    })

    data = [line.split(",") for line in r.text[19:].split("<br>")[:-1]]

    leaderboard = []
    for row in data:
        leaderboard.append({
            "width"       : row[0],
            "height"      : row[1],
            "solvetype"   : row[2],
            "displaytype" : row[3],
            "user"        : row[4],
            "time"        : row[5],
            "moves"       : row[6],
            "tps"         : row[7],
            "avglen"      : row[8],
            "controls"    : row[9],
            "pbtype"      : row[10],
            "timestamp"   : row[12]
        })

    return leaderboard

def get_category_results():
    # get the full leaderboard
    lb = get_leaderboard()

    # filter the results
    filtered_lb = []
    entries = ["width", "height", "solvetype", "avglen"]
    for result in lb:
        result_category = {x : result[x] for x in entries}
        if result_category in categories:
            filtered_lb.append(result)

    # sort by username
    filtered_lb.sort(key=lambda x: x["user"])

    return filtered_lb
