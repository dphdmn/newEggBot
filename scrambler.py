import random

def evenPermutation(n):
    assert n > 2

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
    assert n > 1

    arr = evenPermutation(n*n-1) + [0]
    g = n*n-1

    d = random.randint(0, n-1)
    r = random.randint(0, n-1)

    for i in range(d):
        arr[g], arr[g-n] = arr[g-n], arr[g]
        g = g-n

    for i in range(r):
        arr[g], arr[g-1] = arr[g-1], arr[g]
        g = g-1

    return arr
