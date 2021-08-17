import datetime as dt
from solver import solvers
import scrambler
import time
from puzzle_state import PuzzleState
from algorithm import Algorithm
from discord.ext import tasks
from replit import db

class FMCRound:
    def __init__(self, db_path, scramble=None, duration=86400, warnings=[], on_close=None, on_warning=None):
        self.db_path = db_path + "current/"
        self.scramble = scramble
        self.duration = duration
        self.warnings = warnings
        self.on_close = on_close
        self.on_warning  = on_warning

        self.loop.start()

    def running(self):
        return self.db_path + "start_time" in db

    def get_scramble(self):
        return PuzzleState(db[self.db_path + "scramble"])

    def get_solution(self):
        return Algorithm(db[self.db_path + "solution"])

    def elapsed(self):
        return int(time.time()) - int(db[self.db_path + "start_time"])

    def remaining(self):
        return max(0, self.duration - self.elapsed())

    def has_result(self, id):
        return self.db_path + f"results/{id}" in db

    def result(self, id):
        key = self.db_path + f"results/{id}"
        if key in db:
            return Algorithm(db[key])
        else:
            raise ValueError(f"user id {id} has not submitted a solution")

    def results(self):
        ids = [int(x.split("/")[-1]) for x in db.prefix(self.db_path + "results/")]

        results = {}
        for id in ids:
            results[id] = self.result(id)

        sorted_results = dict(sorted(results.items(), key=lambda x: x[1].length()))

        return sorted_results

    def open(self):
        if self.running():
            return

        if self.scramble is None:
            scramble = scrambler.getScramble(4)
        else:
            scramble = self.scramble
        solution = solvers[4].solveOne(scramble)

        db[self.db_path + "scramble"] = scramble.to_string()
        db[self.db_path + "solution"] = solution.to_string()
        db[self.db_path + "start_time"] = int(time.time())

        # initialize warning db entries
        for warning in self.warnings:
            db[self.db_path + f"warnings/{warning}"] = False

    def close(self):
        if not self.running():
            return

        scramble = self.get_scramble()
        solution = self.get_solution()
        timestamp = db[self.db_path + "start_time"]
        results = self.results()

        # clean up db
        for x in db.prefix(self.db_path):
            del db[x]

        return {
            "scramble"  : scramble.to_string(),
            "solution"  : solution.to_string(),
            "timestamp" : timestamp,
            "results"   : results
        }

    def submit(self, user_id, solution):
        if not self.running():
            return

        # check that the solution works
        scramble = self.get_scramble()
        scramble.apply(solution)
        if not scramble.solved():
            # scramble has been modified, so get a new copy of the scramble from the db to print
            scramble = self.get_scramble()
            raise ValueError(f"solution does not solve scramble \"{scramble.to_string()}\"")

        # add the new result if it's better than any previous result
        result_key = self.db_path + f"results/{user_id}"
        if result_key in db:
            old = self.result(user_id)
            if solution.length() < old.length():
                db[result_key] = solution.to_string()
        else:
            db[result_key] = solution.to_string()

    @tasks.loop(seconds=10)
    async def loop(self):
        if not self.running():
            return

        elapsed = self.elapsed()

        # check for any time warnings that need to be emitted
        if self.on_warning is not None:
            for warning in self.warnings:
                key = self.db_path + f"warnings/{warning}"
                if elapsed >= warning and not db[key]:
                    db[key] = True
                    await self.on_warning(warning)

        if elapsed >= self.duration:
            round_dict = self.close()
            if self.on_close is not None:
                await self.on_close(round_dict)
