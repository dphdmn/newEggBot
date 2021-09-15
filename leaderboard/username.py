from helper import serialize
from replit import db

# find the first username which contains s as a substring
def find_username(s):
    s = s.lower()

    # get all usernames from the db, and convert to lower case
    names = serialize.deserialize(db["leaderboard/usernames"])
    names = [name.lower() for name in names]

    # check if there's an exact match
    if s in names:
        return s

    # if not, find the first username containing s as a substring
    for name in names:
        if s in name:
            return name

    # none found
    raise ValueError("username not found")
