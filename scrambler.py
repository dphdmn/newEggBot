import random
from puzzle_state import PuzzleState
from move import Move

def evenPermutation(n):
    if n <= 1:
        raise ValueError(f"list size ({n}) should be greater than 1")

    arr = list(range(1, n+1))
    parity = False

    for i in range(n-2):
        t = random.randint(i, n-1)
        if i != t:
            parity = not parity
        arr[i], arr[t] = arr[t], arr[i]

    if parity:
        arr[n-2], arr[n-1] = arr[n-1], arr[n-2]

    return arr

def getScramble(n):
    if n <= 1:
        raise ValueError(f"puzzle size ({n}) should be greater than 1")

    arr = evenPermutation(n*n-1) + [0]

    scramble = PuzzleState()
    scramble.arr = [arr[n*i : n*(i+1)] for i in range(n)]

    d = random.randint(0, n-1)
    r = random.randint(0, n-1)

    for i in range(d):
        scramble.move(Move.D)
    for i in range(r):
        scramble.move(Move.R)

    return scramble
