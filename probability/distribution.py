import numpy as np
from numpy.polynomial.polynomial import polypow
from enum import Flag

class Comparison(Flag):
    LessThan = 1
    Equal = 2
    GreaterThan = 4
    LessThanOrEqual = LessThan | Equal
    GreaterThanOrEqual = GreaterThan | Equal
    NotEqual = LessThan | GreaterThan

# represents a discrete probability distribution on the points 0, 1, ..., n
class Distribution:
    def __init__(self, arr):
        total = sum(arr)
        self.n = len(arr)-1
        self.arr = np.array([x/total for x in arr])

    # sum of n iid copies of this distribution
    def sum_distribution(self, n):
        return Distribution(polypow(self.arr, n))

    def prob(self, n, comparison):
        if n < 0:
            return 0
        if n > self.n:
            return 1

        less = comparison & Comparison.LessThan
        equal = comparison & Comparison.Equal
        greater = comparison & Comparison.GreaterThan

        total = 0
        if less:
            total += sum(self.arr[:n])
        if equal:
            total += self.arr[n]
        if greater:
            total += sum(self.arr[n+1:])

        return total