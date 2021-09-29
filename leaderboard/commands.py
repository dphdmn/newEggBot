import leaderboard.leaderboard as lb
from leaderboard.categories import categories, category_names
from leaderboard import tiers
from leaderboard import ranking
from leaderboard import db
import leaderboard.username as names
import time_format

def get_pb(width, height, user):
    username = names.find_username(user)

    # get all the relevant data in one leaderboard call
    data = lb.get_leaderboard(width, height, user=username)

    msg = f"{width}x{height} PBs for {username}\n"
    msg += "```\n"
    for i, category in enumerate(categories):
        if category["width"] == width and category["height"] == height:
            # find the users pb for this category
            best_time = None
            for result in data:
                if result["solvetype"] == category["solvetype"] and result["avglen"] == category["avglen"]:
                    if best_time is None:
                        best_time = result["time"]
                    else:
                        best_time = min(best_time, result["time"])

            # find the tier of this result
            tier = tiers.result_tier(i, best_time)
            if tier is None:
                tier_name = "Unranked"
            else:
                tier_name = tier["name"]

            msg += f"{category_names[i]}: {time_format.format(best_time)} ({tier_name})\n"
    msg += "```"

    return msg

def get_req(width, height, tier_name):
    tier = tiers.get_tier(tier_name)
    real_tier_name = tier["name"]

    msg = f"Requirements for {real_tier_name} {width}x{height}\n"
    msg += "```\n"
    for i, category in enumerate(categories):
        if category["width"] == width and category["height"] == height:
            req = tier["times"][i]
            msg += f"{category_names[i]}: {time_format.format(req)}\n"
    msg += "```"

    return msg

def rank(user):
    username = names.find_username(user)
    table = db.latest_results()
    position = ranking.place(table, username)
    power = ranking.power(table[username])
    power_tier_name = tiers.power_tier(power)["name"]
    return f"{username} is in position {position} with {power} power ({power_tier_name})"
