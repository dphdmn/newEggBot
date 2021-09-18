import base64
import datetime as dt
from helper import serialize
import json
import pickle
import zlib
import leaderboard.leaderboard as lb
import leaderboard.tiers as tiers
import leaderboard.categories as categories
from replit import db

def store_results():
    table = lb.results_table()
    today = dt.datetime.now().strftime("%Y-%m-%d")
    db[f"leaderboard/data/{today}"] = serialize.serialize(table)

def store_usernames():
    # latest data that we have stored
    table = lb.latest_from_db()

    # format the table
    sorted_table = lb.sort_table(table)
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
        table_str = json.dumps(lb.format_results_table(table))

        # compress the table string and convert to base 64
        compressed_str = zlib.compress(table_str.encode(), level=9)
        base64_str = base64.b64encode(compressed_str).decode()

        data_dict[date] = base64_str

    file = ""

    # write tiers into an array of json objects
    file += "export const tiers = " + json.dumps(tiers.tiers) + ";\n"

    # write categories
    file += "export const categories = " + json.dumps(categories.category_names) + ";\n"

    # write table data
    file += "export const data = " + json.dumps(data_dict) + ";\n"

    # write to data file
    with open("web/data.js", "w") as f:
        f.write(file)
        f.close()

def update():
    # read results from the leaderboard and store in the db
    store_results()

    # store list of all usernames, sorted by power
    store_usernames()

    update_webpage()
