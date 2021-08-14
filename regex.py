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
