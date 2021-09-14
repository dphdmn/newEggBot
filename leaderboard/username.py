from helper import serialize
from helper import edit_distance
from replit import db

def get_usernames():
    # get the most recent data that we have
    dates = [x[17:] for x in db.prefix("leaderboard/data/")]
    dates.sort()
    date = dates[-1]

    # decompress it and get the usernames
    data = serialize.deserialize(db[date])
    usernames = data.keys()

    return usernames

# find the username which is nearest to a string
def nearest(s):
    return edit_distance.nearest(get_usernames(), s)
