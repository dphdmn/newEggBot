import subprocess

class Solver:
    def __init__(self, size):
        self.size = size

    def start(self):
        self.process = subprocess.Popen(f"./solver{self.size}", stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

    def stop(self):
        self.process.terminate()

    def solve(self, scramble):
        self.process.stdin.write(scramble.strip()+"\n")
        self.process.stdin.flush()

        solutions = []
        while True:
            line = self.process.stdout.readline().strip()
            if line == "done":
                break
            else:
                solutions.append(line)

        return solutions

    def solveOne(self, scramble):
        self.process.stdin.write("one\n")
        return self.solve(scramble)[0]

    def solveGood(self, scramble):
        self.process.stdin.write("good\n")
        return self.solve(scramble)

    def solveAll(self, scramble):
        self.process.stdin.write("all\n")
        return self.solve(scramble)
