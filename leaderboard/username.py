from helper import serialize
from replit import db

def get_usernames():
    # get the most recent data that we have
    date = db.prefix("leaderboard/data/")[-1]
    data = db[date]

    # decompress it and get the usernames
    data = serialize.deserialize(data)
    usernames = list(data.keys())

    return usernames

# find the first username which contains s as a substring
def find_username(s):
    for name in get_usernames():
        if s.lower() in name.lower():
            return name
    raise ValueError("username not found")
