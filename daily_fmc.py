import datetime as dt
from solver import solvers
import scrambler
import os
import time
from animate import make_video
from puzzle_state import PuzzleState
from algorithm import Algorithm
from draw_state import draw_state
from replit import db
import discord
from discord.ext import tasks
from prettytable import PrettyTable

class DailyFMC:
    def __init__(self, client, channel_id, results_channel_id):
        self.client = client
        self.channel = client.get_channel(channel_id)
        self.results_channel = client.get_channel(results_channel_id)
        self.db_path = f"{self.channel.guild.id}/fmc/{self.channel.id}/"

    def is_open(self):
        return self.db_path + "start_time" in db

    def scramble(self):
        return PuzzleState(db[self.db_path + "scramble"])

    def solution(self):
        return Algorithm(db[self.db_path + "solution"])

    def elapsed(self):
        return int(time.time()) - int(db[self.db_path + "start_time"])

    def remaining(self):
        return max(0, 86400 - self.elapsed())

    def date_string(self):
        start = db[self.db_path + "start_time"]
        return dt.datetime.utcfromtimestamp(start).strftime("%Y-%m-%d")

    def result(self, id):
        key = self.db_path + f"results/{id}"
        if key in db:
            return Algorithm(db[key])
        else:
            user = self.client.get_user(id)
            raise ValueError(f"user \"{user.name}\" (id={id}) has not submitted a solution")

    def results(self):
        ids = [int(x.split("/")[-1]) for x in db.keys() if x.startswith(self.db_path + "results/")]

        results = {}
        for id in ids:
            results[id] = self.result(id)

        sorted_results = dict(sorted(results.items(), key=lambda x: x[1].length()))

        return sorted_results

    def start(self):
        self.loop.start()

    async def open(self):
        if self.is_open():
            pass
        else:
            await self.channel.send("Starting daily FMC, please wait!")
            scramble = scrambler.getScramble(4)
            solution = solvers[4].solveOne(scramble)

            db[self.db_path + "scramble"] = scramble.to_string()
            db[self.db_path + "solution"] = solution.to_string()
            db[self.db_path + "start_time"] = int(time.time())
            db[self.db_path + "one_hour_warning"] = False

            msg = "Daily FMC scramble: " + scramble.to_string() + "\n"
            msg += "Optimal solution length: " + str(solution.length()) + "\n"
            msg += "Use **!submit** command to submit solutions (You can submit multiple times!), for example:\n"
            msg += "!submit LULD3RU2LD2LUR2UL2D2RU2RLULDR3UL2D2R2U2L2DLDRU2LDRURDL2DR2U2L2DRULDR2ULDLU\n"

            img = draw_state(scramble)
            img.save("scramble.png", "PNG")

            with open("scramble.png", "rb") as f:
                picture = discord.File(f)
                await self.channel.send(msg, file=picture)
            os.remove("scramble.png")

            # ping fmc role
            id = os.environ["fmc_role_id"]
            await self.channel.send(f"<@&{id}>")

    async def close(self):
        if not self.is_open():
            pass
        else:
            results = self.results()
            date = self.date_string()
            scramble = self.scramble()
            optSolution = self.solution()
            optLength = optSolution.length()

            db[self.db_path + f"history/{date}/scramble"] = db[self.db_path + "scramble"]
            db[self.db_path + f"history/{date}/solution"] = db[self.db_path + "solution"]
            for id in results:
                db[self.db_path + f"history/{date}/results/{id}"] = db[self.db_path + f"results/{id}"]

            del db[self.db_path + "scramble"]
            del db[self.db_path + "solution"]
            for id in results:
                del db[self.db_path + f"results/{id}"]
            del db[self.db_path + "start_time"]
            del db[self.db_path + "one_hour_warning"]

            msg = "Daily FMC results!\n"
            msg += "Date: " + date + "\n"
            msg += "Scramble: " + scramble.to_string() + "\n"
            msg += f"Optimal solution [{optLength}]: {optSolution.to_string()}"

            if len(results) == 0:
                msg += "\n\nNo one joined :("
                await self.channel.send(msg)
                await self.results_channel.send(msg)
            else:
                table = PrettyTable()
                table.field_names = ["Username", "Moves", "To optimal", "Solution"]

                # organise results in an array
                for (id, solution) in results.items():
                    user = self.client.get_user(id)
                    length = solution.length()
                    table.add_row([user.name, length, length - optLength, solution.to_string()])

                with open("results.txt", "w+") as f:
                    f.write(table.get_string())
                    f.close()

                with open("results.txt", "rb") as f:
                    txt = discord.File(f)
                    await self.channel.send(msg, file=txt)
                    f.close()

                with open("results.txt", "rb") as f:
                    txt = discord.File(f)
                    await self.results_channel.send(msg, file=txt)
                    f.close()

                os.remove("results.txt")

            make_video(scramble, optSolution, 8)
            with open("movie.webm", "rb") as f:
                picture = discord.File(f)
                await self.channel.send("", file=picture)
            os.remove("movie.webm")

    async def submit(self, user, solution):
        # check that the solution works
        scramble = self.scramble()
        scramble.apply(solution)
        if not scramble.solved():
            raise ValueError(f"solution does not solve scramble \"{scramble.to_string()}\"")

        name = user.name
        id = user.id

        result_key = self.db_path + f"results/{id}"
        if result_key not in db:
            db[result_key] = solution.to_string()
            await self.channel.send(f"[{solution.length()}] Solution added for {name}")
        else:
            previous = self.result(id)
            previous_length = previous.length()
            new_length = solution.length()
            if new_length < previous_length:
                db[result_key] = solution.to_string()
                await self.channel.send(f"[{previous_length} -> {new_length}] Solution updated for {name}")
            else:
                await self.channel.send(f"[{new_length}] You already have a {previous_length} move solution, {name}")

    @tasks.loop(seconds=10)
    async def loop(self):
        if not self.is_open():
            await self.open()
        elif self.elapsed() >= 86400:
            # close and open, but set the start time to exactly 86400 seconds after the previous
            # start time, otherwise there will be a slight shift in start time over many rounds
            start = db[self.db_path + "start_time"]
            await self.close()
            await self.open()
            db[self.db_path + "start_time"] = start + 86400
        elif self.elapsed() >= 86400 - 3600:
            if not db[self.db_path + "one_hour_warning"]:
                await self.channel.send("One hour remaining!")
                db[self.db_path + "one_hour_warning"] = True
