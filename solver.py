from log import log
import subprocess
from algorithm import Algorithm

class Solver:
    def __init__(self, size):
        self.size = size

    def start(self):
        program = f"./solver{self.size}"
        log.info(f"starting solver \"{program}\"")
        self.process = subprocess.Popen(program, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    def stop(self):
        log.info(f"terminating solver {self.size}")
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
    3: Solver(3),
    4: Solver(4)
}

solvers[3].start()
solvers[4].start()
