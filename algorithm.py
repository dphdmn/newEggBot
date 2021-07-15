import re
import move
from move import Move

class Algorithm:
    def __init__(self, alg=""):
        # remove all whitespace
        alg = "".join(alg.split())

        regex = re.compile("[ULDR]\d*")
        moves = re.findall(regex, alg)

        # valid algorithm if joining the moves produces the original string
        if "".join(moves) != alg:
            raise ValueError(f"algorithm \"{alg}\" is invalid")

        # read moves and amounts
        def parse_move(m):
            # if no amount given, use 1
            if len(m) == 1:
                amount = 1
            else:
                amount = int(m[1:])

            return move.from_string(m[0]), amount

        # parse moves
        arr = []
        for m in moves:
            next_move = parse_move(m)
            # add the first move
            if arr == []:
                arr.append(next_move)
            else:
                # check if direction is the same as previous move. if yes, combine them
                if arr[-1][0] == next_move[0]:
                    amount = arr[-1][1] + next_move[1]
                    arr[-1] = (arr[-1][0], amount)
                else:
                    arr.append(next_move)

        self.moves = arr

    def __add__(self, other):
        if self.moves == []:
            return other

        if other.moves == []:
            return self

        # check if the last move of self and the first move of other are the same direction
        if self.moves[-1][0] == other.moves[0][0]:
            # all moves of self, except last
            arr = self.moves[:-1]

            # add combined last and first moves
            amount = self.moves[-1][1] + other.moves[0][1]
            arr.append((self.moves[-1][0], amount))

            # add all moves of other, except first
            arr += other.moves[1:]
        else:
            # join the two arrays
            arr = self.moves + other.moves

        a = Algorithm()
        a.moves = arr
        return a

    def length(self):
        return sum([m[1] for m in self.moves])

    def to_string(self):
        def to_string(t):
            # if amount = 1, just write e.g. "R" instead of "R1"
            if t[1] == 1:
                return move.to_string(t[0])
            else:
                return move.to_string(t[0]) + str(t[1])

        return "".join([to_string(m) for m in self.moves])

    def invert(self):
        arr = [(move.inverse(m), a) for (m, a) in self.moves]
        arr.reverse()
        self.moves = arr

    def inverse(self):
        a = self
        a.invert()
        return a