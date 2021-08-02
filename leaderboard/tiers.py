from categories import categories

with open("data/tier_names.txt", "r") as f:
    tier_names = f.read().strip().split("\n")
    f.close()

with open("data/tier_power.txt", "r") as f:
    tier_power = [int(x) for x in f.read().strip().split("\n")]
    f.close()

with open("data/tier_limits.txt", "r") as f:
    tier_limits = [int(x) for x in f.read().strip().split("\n")]
    f.close()

with open("data/tier_times.txt", "r") as f:
    tier_times = [[int(x) for x in row.split(",")] for row in f.read().strip().split("\n")]
    f.close()

assert len(tier_names) == len(tier_power) == len(tier_limits) == len(tier_times)

tiers = []
for i in range(len(tier_names)):
    assert len(categories) == len(tier_times[i])

    tiers.append({
        "name"  : tier_names[i],
        "power" : tier_power[i],
        "limit" : tier_limits[i],
        "times" : tier_times[i]
    })
