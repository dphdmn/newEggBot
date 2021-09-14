from helper import serialize
from helper import edit_distance
from replit import db

def get_usernames():
    # get the most recent data that we have
    date = db.prefix("leaderboard/data/")[-1]
    data = db[date]

    # decompress it and get the usernames
    data = serialize.deserialize(data)
    usernames = list(data.keys())

    return usernames

# find the username which is nearest to a string
def nearest(s):
    return edit_distance.nearest(get_usernames(), s)
