def format_prob(p):
    if p < 0.01:
        n = round(1/p)
        return f"1/{n}"
    else:
        return format(100*p, ".2f") + "%"