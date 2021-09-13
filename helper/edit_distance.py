# https://en.wikipedia.org/wiki/Levenshtein_distance#Iterative_with_two_matrix_rows
def distance(a, b):
    m = len(a)
    n = len(b)

    v0 = list(range(n+1))
    v1 = list(range(n+1))

    for i in range(m):
        v1[0] = i+1
        for j in range(n):
            deletionCost = v0[j+1]+1
            insertionCost = v1[j]+1
            substitutionCost = v0[j]
            if a[i] != b[j]:
                substitutionCost += 1
            v1[j+1] = min(deletionCost, insertionCost, substitutionCost)
        v0, v1 = v1, v0

    return v0[n]

# return the nearest string in the list l to the string s
def nearest(l, s):
    min_dist = distance(s, l[0])
    best_str = l[0]
    for a in l:
        dist = distance(s, a)
        if dist < min_dist:
            min_dist = dist
            best_str = a
    return best_str
