import numpy as np
from numpy.polynomial.polynomial import polypow
from enum import Flag

class Comparison(Flag):
    Null               = 0
    LessThan           = 1
    Equal              = 2
    GreaterThan        = 4
    LessThanOrEqual    = LessThan | Equal
    GreaterThanOrEqual = GreaterThan | Equal
    NotEqual           = LessThan | GreaterThan
    All                = LessThan | Equal | GreaterThan

# represents a discrete probability distribution on the points 0, 1, ..., n
class Distribution:
    def __init__(self, arr):
        total = sum(arr)
        self.n = len(arr)-1
        self.arr = np.array([x/total for x in arr])

    # sum of n iid copies of this distribution
    def sum_distribution(self, n):
        return Distribution(polypow(self.arr, n))

    def prob_range(self, start, end):
        return sum(self.arr[start:end+1])

    def prob(self, n, comparison):
        if comparison == Comparison.Null:
            return 0
        if comparison == Comparison.All:
            return 1

        if comparison == Comparison.LessThan:
            start = 0
            end = n-1
        elif comparison == Comparison.Equal:
            start = n
            end = n
        elif comparison == Comparison.GreaterThan:
            start = n+1
            end = self.n
        elif comparison == Comparison.LessThanOrEqual:
            start = 0
            end = n
        elif comparison == Comparison.GreaterThanOrEqual:
            start = n
            end = self.n
        elif comparison == Comparison.NotEqual:
            return 1 - self.prob(n, Comparison.Equal)

        return self.prob_range(start, end)