from helper import serialize
from replit import db

# find the first username which contains s as a substring
def find_username(s):
    # get all usernames from the db, and convert to lower case
    names = serialize.deserialize(db["leaderboard/usernames"])
    names_lower = [name.lower() for name in names]

    # check if there's an exact match
    if s.lower() in names_lower:
        # return the non-lower-case version of the username
        index = names_lower.index(s.lower())
        return names[index]

    # if not, find the first username containing s as a substring
    for name in names:
        if s.lower() in name.lower():
            return name

    # none found
    raise ValueError("username not found")
