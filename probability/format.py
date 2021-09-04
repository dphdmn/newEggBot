def format_prob(p):
    if p == 0:
        return "0"
    elif p < 1e-15:
        return "almost 0"
    elif p < 0.01:
        n = round(1/p)
        return f"1/{n}"
    else:
        return format(100*p, ".2f") + "%"
