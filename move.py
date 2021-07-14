from enum import Enum

class Move(Enum):
    U = 0
    L = 1
    D = 2
    R = 3

def to_string(move):
    if move == Move.U:
        return "U"
    elif move == Move.L:
        return "L"
    elif move == Move.D:
        return "D"
    elif move == Move.R:
        return "R"

def from_string(move):
    if move == "U":
        return Move.U
    elif move == "L":
        return Move.L
    elif move == "D":
        return Move.D
    elif move == "R":
        return Move.R

def inverse(move):
    if move == Move.U:
        return Move.D
    elif move == Move.L:
        return Move.R
    elif move == Move.D:
        return Move.U
    elif move == Move.R:
        return Move.L
