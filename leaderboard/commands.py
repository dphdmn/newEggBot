import leaderboard.leaderboard as lb
from leaderboard.categories import categories, category_names
from leaderboard.tiers import tiers, get_tier
import leaderboard.username as names
import time_format

def get_pb(width, height, user):
    username = names.find_username(user)

    # get all the relevant data in one leaderboard call
    data = lb.get_leaderboard(width, height, user=username)

    msg = ""
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
            tier_index = lb.result_tier(i, best_time)
            if tier_index is None:
                tier = "Unranked"
            else:
                tier = tiers[tier_index]["name"]

            msg += f"{category_names[i]}: {time_format.format(best_time)} ({tier})\n"

    return msg

def get_req(width, height, tier_name):
    msg = ""
    tier = get_tier(tier_name)
    for i, category in enumerate(categories):
        if category["width"] == width and category["height"] == height:
            req = tier["times"][i]
            msg += f"{category_names[i]}: {time_format.format(req)}\n"

    return msg
