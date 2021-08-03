with open("leaderboard/data/categories.txt", "r") as f:
    data = f.read().strip()
    f.close()

data = [line.split(",") for line in data.split("\n")]

categories = []
for row in data:
    categories.append({
        "width"     : int(row[0]),
        "height"    : int(row[1]),
        "solvetype" : row[2],
        "avglen"    : int(row[3])
    })
