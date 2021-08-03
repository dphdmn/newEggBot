import os
import requests
from categories import categories
from tiers import tiers

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
            "width"       : int(row[0]),
            "height"      : int(row[1]),
            "solvetype"   : row[2],
            "displaytype" : row[3],
            "user"        : row[4],
            "time"        : int(row[5]),
            "moves"       : int(row[6]),
            "tps"         : int(row[7]),
            "avglen"      : int(row[8]),
            "controls"    : row[9],
            "pbtype"      : row[10],
            "timestamp"   : int(row[12])
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
        try:
            # add the category index for convenience
            index = categories.index(result_category)
            result["category"] = index
            filtered_lb.append(result)
        except ValueError as e:
            continue

    # sort by username
    filtered_lb.sort(key=lambda x: x["user"])

    return filtered_lb

def results_table():
    results = get_category_results()
    users = sorted(set(x["user"] for x in results))

    table = {}

    for user in users:
        # create an empty row with one entry per category
        row = [None]*len(categories)

        for result in results:
            if result["user"] != user:
                continue

            category = result["category"]

            # fill in the entry in the table.
            # we need the min() because the user might have times with
            # keyboard and mouse, and we have to choose the faster time
            if row[category] is None:
                row[category] = result["time"]
            else:
                row[category] = min(row[category], result["time"])

        # add the users results to the table
        table[user] = row

    return table

def result_tier(category_index, time):
    if time is None:
        return None

    for i, tier in enumerate(tiers):
        if time > tier["times"][category_index]:
            # if the result doesn't make the first tier, return None
            # otherwise, return the previous tier
            if i == 0:
                return None
            return i-1

    # highest tier
    return len(tiers)-1

def power(results_list):
    total = 0
    for i, result in enumerate(results_list):
        tier = result_tier(i, result)
        if tier is None:
            continue
        total += tiers[tier]["power"]
    return total

def format_results_table(results_table):
    users = results_table.keys()

    # sort users by power
    user_power = dict(sorted([(user, power(results_table[user])) for user in users], key=lambda x: (-x[1], x[0])))
    sorted_users = user_power.keys()

    table = []
    for i, user in enumerate(sorted_users):
        results_str = [format(x/1000, ".3f") if x is not None else "" for x in results_table[user]]
        row = [user, i+1, user_power[user]] + results_str
        table.append(row)

    return str(table)
