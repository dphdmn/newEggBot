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
    # get sorted list of all dates that we have data for
    dates = [x[17:] for x in db.prefix("leaderboard/data/")]
    dates.sort()

    # create a dict of the form {date : data, ...}
    data_dict = {}
    for date in dates:
        # read the data from the database and uncompress it
        base64_table = db["leaderboard/data/" + date]
        compressed_table = base64.b64decode(base64_table.encode())
        pickled_table = zlib.decompress(compressed_table)
        table = pickle.loads(pickled_table)

        # format and sort the data
        table_str = lb.format_results_table(table)

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
    store_results()
    update_webpage()
