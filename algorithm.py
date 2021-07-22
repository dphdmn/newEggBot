import re
import copy
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

    def simplify(self):
        i = 0
        while i < len(self.moves) - 1:
            # check for cancellation of moves i and i+1
            if self.moves[i][0] == self.moves[i+1][0] or self.moves[i][0] == move.inverse(self.moves[i+1][0]):
                direction = self.moves[i][0]
                if self.moves[i][0] == self.moves[i+1][0]:
                    amount = self.moves[i][1] + self.moves[i+1][1]
                else:
                    amount = self.moves[i][1] - self.moves[i+1][1]

                # if amount is 0, delete both moves
                if amount == 0:
                    self.moves.pop(i+1)
                    self.moves.pop(i)
                    i = max(i-1, 0)
                else:
                    # if amount is negative, flip the move, e.g. R(-2) -> L2
                    if amount < 0:
                        direction = move.inverse(direction)
                        amount = -amount

                    # delete i+1th move and update ith move
                    self.moves.pop(i+1)
                    self.moves[i] = (direction, amount)
            # no cancellation
            else:
                i += 1
        return self

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
        return self

    def inverse(self):
        a = copy.deepcopy(self)
        a.invert()
        return a

    def revert(self):
        self.moves.reverse()
        return self

    def reverse(self):
        a = copy.deepcopy(self)
        a.reverse()
        return a

    def at(self, n):
        if n < 0 or n >= self.length():
            raise ValueError(f"index {n} out of range")
        total = 0
        for (direction, amount) in self.moves:
            if total + amount < n + 1:
                total += amount
            else:
                return direction

    def take(self, n):
        if n == 0:
            return Algorithm("")

        arr = []
        total = 0
        for (direction, amount) in self.moves:
            if total + amount <= n:
                arr.append((direction, amount))
                if total + amount == n:
                    break
            else:
                arr.append((direction, n - total))
                break
            total += amount

        a = Algorithm()
        a.moves = arr
        return a

    def rtake(self, n):
        return self.inverse().take(n).inverse()

    def drop(self, n):
        return self.rtake(self.length()-n)

    def rdrop(self, n):
        return self.take(self.length()-n)

    def first(self):
        if self.moves == []:
            raise ValueError("algorithm is empty")
        return self.moves[0][0]

    def last(self):
        if self.moves == []:
            raise ValueError("algorithm is empty")
        return self.moves[-1][0]
