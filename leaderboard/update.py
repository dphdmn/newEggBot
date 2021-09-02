import base64
import datetime as dt
import json
import pickle
import zlib
import leaderboard.leaderboard as lb
import leaderboard.tiers as tiers
import leaderboard.categories as categories
from replit import db

def store_results():
    table = lb.results_table()

    # pickle, compress, convert to base64 so it can be stored in the db
    pickled_table = pickle.dumps(table)
    compressed_table = zlib.compress(pickled_table, level=9)
    base64_table = base64.b64encode(compressed_table).decode()

    # store in the database
    today = dt.datetime.now().strftime("%Y-%m-%d")
    db[f"leaderboard/data/{today}"] = base64_table

def update_webpage():
    dates = [x[17:] for x in db.prefix("leaderboard/data/")]
    dates.sort()

    # write dates into an array
    file = "export const dates = ["
    for date in dates:
        file += "\"" + date + "\","
    file = file[:-1] + "];\n"

    # write tiers into an array of json objects
    file += "export const tiers = " + json.dumps(tiers.tiers) + ";\n"

    # write categories
    file += "export const categories = " + json.dumps(categories.categories) + ";\n"

    # write table data into the js variable data
    file += "export const data = ["
    for date in dates:
        base64_table = db["leaderboard/data/" + date]
        compressed_table = base64.b64decode(base64_table.encode())
        pickled_table = zlib.decompress(compressed_table)
        table = pickle.loads(pickled_table)
        table_str = lb.format_results_table(table)

        # compress the table string and convert to base 64
        compressed_str = zlib.compress(table_str.encode(), level=9)
        base64_str = base64.b64encode(compressed_str).decode()
        file += "\"" + base64_str + "\","

    file = file[:-1] + "];\n"

    # write to data file
    with open("data.js", "w") as f:
        f.write(file)
        f.close()

def update():
    store_results()
    update_webpage()
