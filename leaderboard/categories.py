with open("leaderboard/data/categories.txt", "r") as f:
    data = f.read().strip()
    f.close()

data = [line.split(",") for line in data.split("\n")]

categories = []
category_names = []
for row in data:
    width = int(row[0])
    height = int(row[1])
    solvetype = row[2]
    avglen = int(row[3])

    categories.append({
        "width"     : width,
        "height"    : height,
        "solvetype" : solvetype,
        "avglen"    : avglen
    })

    name = f"{width}x{height}"
    if solvetype[:8] == "Marathon":
        name += " x" + solvetype[9:]
    elif solvetype == "2-N relay":
        name += " relay"

    if avglen == 1:
        name += " single"
    else:
        name += f" ao{avglen}"

    category_names.append(name)
