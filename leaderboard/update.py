import base64
import datetime as dt
from helper import serialize
import json
import zlib
import leaderboard.leaderboard as lb
import leaderboard.tiers as tiers
import leaderboard.categories as categories
from replit import db

# filters the leaderboard results, removing any results that don't correspond
# to one of our categories. each result has a "category" parameter appended
# which is the index of the category in leaderboard.categories.categories.
def get_category_results():
    # get the full leaderboard
    full_lb = lb.get_leaderboard()

    # filter the results
    filtered_lb = []
    entries = ["width", "height", "solvetype", "avglen"]
    for result in full_lb:
        result_category = {x : result[x] for x in entries}
        try:
            # add the category index for convenience
            index = categories.categories.index(result_category)
            result["category"] = index
            filtered_lb.append(result)
        except ValueError as e:
            continue

    # sort by username
    filtered_lb.sort(key=lambda x: x["user"])

    return filtered_lb

# creates a dict of the form {username : [list of category times]}
# where the i'th element of the list of times is the users time in
# the i'th category in leaderboard.categories.categories.
def results_table():
    results = get_category_results()
    users = sorted(set(x["user"] for x in results))

    table = {}

    for user in users:
        # create an empty row with one entry per category
        row = [None]*len(categories.categories)

        for result in results:
            if result["user"] != user:
                continue

            category = result["category"]

            # fill in the entry in the table with the users best time.
            # note that there may be multiple results in the leaderboard
            # if the user has done solves with both control schemes,
            # so we need to choose the fastest one.
            if row[category] is None:
                row[category] = result["time"]
            else:
                row[category] = min(row[category], result["time"])

        # add the users results to the table
        table[user] = row

    return table

def power(results_list):
    total = 0
    for i, result in enumerate(results_list):
        tier = tiers.result_tier(i, result)
        if tier is None:
            continue
        total += tier["power"]
    return total

# sort rows of the table by power
def sort_table(results_table):
    return dict(sorted(results_table.items(), key=lambda x: -power(x[1])))

# takes a dict of results {user : [results]} and creates a list of lists
# of the form [[user, place, power, results], ...]
def format_results_table(results_table):
    sorted_table = sort_table(results_table)
    formatted_table = []
    for i, user in enumerate(sorted_table):
        # add row but replace None with -1 in the results
        new_row = [user, i+1, power(sorted_table[user])]
        new_row += [x if x is not None else -1 for x in sorted_table[user]]
        formatted_table.append(new_row)
    return formatted_table

# get the latest results table that we have stored in the db
def latest_from_db():
    date = db.prefix("leaderboard/data/")[-1]
    table = serialize.deserialize(db[date])
    return table

def store_results():
    table = results_table()
    today = dt.datetime.now().strftime("%Y-%m-%d")
    db[f"leaderboard/data/{today}"] = serialize.serialize(table)

def store_usernames():
    # latest data that we have stored
    table = latest_from_db()

    # format the table
    sorted_table = sort_table(table)
    usernames = list(sorted_table.keys())

    # store sorted list of usernames in db
    db["leaderboard/usernames"] = serialize.serialize(usernames)

def update_webpage():
    # get sorted list of all dates that we have data for
    dates = [x[17:] for x in db.prefix("leaderboard/data/")]
    dates.sort()

    # create a dict of the form {date : data, ...}
    data_dict = {}
    for date in dates:
        # read the data from the database and uncompress it
        table = serialize.deserialize(db[f"leaderboard/data/{date}"])

        # format and sort the data
        table_str = json.dumps(format_results_table(table))

        # compress the table string and convert to base 64
        compressed_str = zlib.compress(table_str.encode(), level=9)
        base64_str = base64.b64encode(compressed_str).decode()

        data_dict[date] = base64_str

    # write data.js file
    file  = "export const tiers = " + json.dumps(tiers.tiers) + ";\n"
    file += "export const categories = " + json.dumps(categories.category_names) + ";\n"
    file += "export const data = " + json.dumps(data_dict) + ";\n"
    with open("web/data.js", "w") as f:
        f.write(file)

def update():
    # read results from the leaderboard and store in the db
    store_results()

    # store list of all usernames, sorted by power
    store_usernames()

    update_webpage()
