from log import log
import subprocess
import os
from algorithm import Algorithm

class Solver:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.name = f"solver{w}x{h}"

    def start(self):
        program = f"./solvers/{self.name}"
        log.info(f"starting solver \"{program}\"")
        self.process = subprocess.Popen(program, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    def stop(self):
        log.info(f"terminating {self.name}")
        self.process.terminate()

    def solve(self, scramble):
        # check that the scramble is solvable
        if not scramble.solvable():
            raise ValueError(f"puzzle state \"{scramble}\" is not solvable")

        log.info(f"solving scramble: {scramble}")

        self.process.stdin.write(f"{scramble}\n")
        self.process.stdin.flush()

        solutions = []
        while True:
            line = self.process.stdout.readline().strip()
            if line == "done":
                break
            else:
                solution = Algorithm(line)
                solutions.append(solution)
                log.info(f"found solution: {solution}")

        log.info(f"solver finished, found {len(solutions)} solutions")
        return solutions

    def solveOne(self, scramble):
        log.info("set solver to mode \"one\"")
        self.process.stdin.write("one\n")
        return self.solve(scramble)[0]

    def solveGood(self, scramble):
        log.info("set solver to mode \"good\"")
        self.process.stdin.write("good\n")
        return self.solve(scramble)

    def solveAll(self, scramble):
        log.info("set solver to mode \"all\"")
        self.process.stdin.write("all\n")
        return self.solve(scramble)

solvers = {
    (2, 2): Solver(2, 2),
    (3, 2): Solver(3, 2),
    (4, 2): Solver(4, 2),
    (5, 2): Solver(5, 2),
    (6, 2): Solver(6, 2),
    (7, 2): Solver(7, 2),
    (8, 2): Solver(8, 2),
    (3, 3): Solver(3, 3),
    (4, 3): Solver(4, 3),
    (5, 3): Solver(5, 3),
    (4, 4): Solver(4, 4)
}

solvers[(3, 3)].start()
solvers[(4, 4)].start()
