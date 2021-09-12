def format_long(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h == 0:
        if m == 0:
            return f"{s} seconds"
        return f"{m} minutes, {s} seconds"
    return f"{h} hours, {m} minutes, {s} seconds"
