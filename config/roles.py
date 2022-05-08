import os

fmc = int(os.environ["role_fmc"])

_tier_names = [
    "Beginner",
    "Bronze",
    "Silver",
    "Gold",
    "Platinum",
    "Diamond",
    "Master",
    "Grandmaster",
    "Nova",
    "Ascended",
    "Aleph",
    "Gamma"
]

_tier_ids = [int(x) for x in os.environ["role_tiers"].split(",")]
tiers = {_tier_names[i]: _tier_ids[i] for i in range(len(_tier_names))}

_true_tier_ids = [int(x) for x in os.environ["role_true_tiers"].split(",")]
true_tiers = {_tier_names[i]: _true_tier_ids[i] for i in range(len(_tier_names))}
