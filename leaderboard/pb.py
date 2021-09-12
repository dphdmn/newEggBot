import leaderboard.leaderboard as lb
from leaderboard.categories import categories, category_names
from leaderboard.tiers import tiers

def get_pb(width, height, user):
    # get all the relevant date in one leaderboard call
    data = lb.get_leaderboard(width, height, user=user)

    msg = ""
    for i, category in enumerate(categories):
        if category["width"] == width and category["height"] == height:
            # find the users pb for this category
            best_time = 1e100
            for result in data:
                if result["solvetype"] == category["solvetype"] and result["avglen"] == category["avglen"]:
                    best_time = min(best_time, result["time"])

            # find the tier of this result
            tier_index = lb.result_tier(i, best_time)
            tier = tiers[tier_index]["name"]

            msg += f"{category_names[i]}: {best_time} ({tier})\n"

    return msg