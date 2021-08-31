def format(regex, name=None):
    if name is None:
        return f"({regex})"
    else:
        return f"(?P<{name}>{regex})"

def puzzle_state(name=None):
    return format("[0-9][0-9 /]*[0-9]", name)

def mtm_move(name=None):
    return format("[ULDR][0-9]*", name)

def algorithm(name=None):
    m = mtm_move()
    return format(f"({m} *)+{m}?", name)

def positive_integer(name=None):
    return format("[1-9][0-9]*", name)

def positive_real(name=None):
    return format("[0-9]+(\.[0-9]+)?", name)

def size(wname=None, hname=None, name=None):
    w = positive_integer(wname)
    h = positive_integer(hname)
    return format(f"{w}(x{h})?", name)

def optionally_spoilered(regex, spoiler_name="spoiler", name=None):
    return format(f"(?P<{spoiler_name}>(\|\|)?){regex}(?P={spoiler_name})", name)
