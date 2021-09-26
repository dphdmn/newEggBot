from helper import serialize
from replit import db

def latest_results():
    date = db.prefix("leaderboard/data/")[-1]
    table = serialize.deserialize(db[date])
    return table

def usernames():
    return serialize.deserialize(db["leaderboard/usernames"])
