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