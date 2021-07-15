from solver import solvers
import scrambler
import os
import time
from draw_state import draw_state
from replit import db
import discord
from discord.ext import tasks
from prettytable import PrettyTable

class DailyFMC:
    def __init__(self, client, channel_id):
        self.client = client
        self.channel = client.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/fmc/{self.channel.id}/"

        if self.db_path + "status" not in db:
            db[self.db_path + "status"] = 0

    def status(self):
        return db[self.db_path + "status"]

    def scramble(self):
        return db[self.db_path + "scramble"]

    def solution(self):
        return db[self.db_path + "solution"]

    def elapsed(self):
        return int(time.time()) - int(db[self.db_path + "start_time"])

    def results(self):
        keys = [x for x in db.keys() if x.startswith(self.db_path + "results/")]
        results = {}

        for key in keys:
            name = key.split("/")[-1]
            result = db[key].length()
            results[name] = result

        return results

    async def open(self):
        if self.status() == 1:
            pass
        else:
            await self.channel.send("Starting daily FMC, please wait!")
            scramble = scrambler.getScramble(4)
            solution = solvers[4].solveOne(scramble)

            db[self.db_path + "scramble"] = scramble
            db[self.db_path + "solution"] = solution
            db[self.db_path + "start_time"] = int(time.time())

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

            db[self.db_path + "status"] = 1

    async def close(self):
        if self.status() == 0:
            pass
        else:
            results = self.results()

            db[self.db_path + "status"] = 0
            del db[self.db_path + "scramble"]
            del db[self.db_path + "solution"]
            del db[self.db_path + "results"]
            del db[self.db_path + "start_time"]

            scramble = self.scramble()
            optSolution = self.solution()
            optLength = optSolution.length()

            msg = "FMC results!\n"
            msg += "Scramble was: " + scramble.to_string() + "\n"
            msg += "Optimal solution: " + optSolution.to_string() + "\n"
            msg += "Optimal moves: " + str(optLength) + "\n"
            msg += "Results:\n"
            
            rowarray = []
            rowheaders = ["Player", "Moves", "To optimal", "Solution"]
            
            for user in results:
                solution = results[user]
                length = solution.length()
                rowarray.append([user, str(length), str(length - optLength), solution.to_string()])

            if len(rowarray) > 0:
                rowarray.sort(key=lambda x: int(x[1]))

            table = PrettyTable()
            table.field_names = rowheaders
            table.add_rows(rowarray)
            
            with open("FMC_results.txt", "w+") as f:
                f.write(table.get_string())
                f.close()

            with open("FMC_results.txt", "rb") as f:
                txt = discord.File(f)
                if len(rowarray) == 0:
                    results_msg = await self.channel.send(msg + "\nNo one joined :(")
                else:
                    results_msg = await self.channel.send(msg, file=txt)
                await results_msg.pin()

            os.remove("FMC_results.txt")

#            makeGif(scramble, solution, 10)
#            with open("movie.webm", "rb") as f:
#                picture = discord.File(f)
#                await message.channel.send("Optimal solution for last FMC competition:\n" + scramble +"\n"+solution+"\n"+leng, file=picture)
#            os.remove("movie.webm")

    async def submit(self, name, solution):
        scramble = self.scramble()
        scramble.apply(solution)
        if not scramble.solved():
            await self.channel.send("Sorry, " + name + ", your solution is not working.")
        else:
            result_key = self.db_path + "results/" + name
            if result_key not in db:
                db[result_key] = solution.to_string()
                await self.channel.send(f"[{solution.length()}] Solution added for {name}")
            else:
                previous_length = db[result_key].length()
                new_length = solution.length()
                if new_length < previous_length:
                    db[result_key] = solution.to_string()
                    await self.channel.send(f"[{previous_length} -> {new_length}] Solution updated for {name}")
                else:
                    await self.channel.send(f"You already have a {previous_length} move solution, {name}")

    @tasks.loop(seconds=10)
    async def loop(self):
        if self.status() == 0:
            return

        if self.elapsed() >= 86400:
            await self.close()
            await self.open()