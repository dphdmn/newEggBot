from database import db

def latest_results():
    date = db.prefix("leaderboard/data/")[-1]
    table = db[date]
    return table

def usernames():
    return db["leaderboard/usernames"]
