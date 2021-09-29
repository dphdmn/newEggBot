import leaderboard.tiers as tiers

def power(results_list):
    total = 0
    for i, result in enumerate(results_list):
        tier = tiers.result_tier(i, result)
        if tier is None:
            continue
        total += tier["power"]
    return total

# sort rows of the table by power
def sort_table(results_table):
    return dict(sorted(results_table.items(), key=lambda x: -power(x[1])))

def place(results_table, user):
    sorted_table = sort_table(results_table)
    usernames = sorted_table.keys()
    for i, name in enumerate(usernames):
        if user == name:
            return i+1
    raise ValueError("username not found")
