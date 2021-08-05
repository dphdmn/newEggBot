import asyncio
import os
from solver import solvers
import scrambler
import move
from draw_state import draw_state
import discord
from replit import db

class MovesGame:
    def __init__(self, client, channel_id):
        self.client = client
        self.channel = client.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/movesgame/{self.channel.id}/"
        self.delay = 8

        # if there is no key in the db showing how many rounds there have been
        # then this must be the first time we are running movesgame
        if self.db_path + "round_number" not in db:
            db[self.db_path + "round_number"] = 0

        db[self.db_path + "status"] = "closed"

    def is_open(self):
        return db[self.db_path + "status"] == "open"

    def good_moves(self):
        return db[self.db_path + "good_moves"]

    def round_number(self):
        return db[self.db_path + "round_number"]

    def results(self):
        keys = db.prefix(self.db_path + "results")

        results = {}
        for key in keys:
            id = int(key.split("/")[-1])
            results[id] = db[key]

        return results

    async def open(self):
        if self.is_open():
            pass
        else:
            db[self.db_path + "status"] = "open"
            db[self.db_path + "round_number"] += 1

            # generate scramble and calculate good moves
            scramble = scrambler.getScramble(4)
            solutions = solvers[4].solveGood(scramble)
            good_moves = "".join([move.to_string(sol.first()) for sol in solutions])

            # draw image
            img = draw_state(scramble)
            img.save("scramble.png", "PNG")

            # store scramble and moves in db
            db[self.db_path + "scramble"] = scramble.to_string()
            db[self.db_path + "good_moves"] = good_moves

            # post start message
            with open("scramble.png", "rb") as f:
                msg = f"Scramble: {scramble.to_string()}"
                img = discord.File(f)
                await self.channel.send(msg, file=img)
            os.remove("scramble.png")

            # wait for people to submit moves and then close
            await asyncio.sleep(self.delay)
            await self.close()

    async def close(self):
        if not self.is_open():
            pass
        else:
            db[self.db_path + "status"] = "closed"

            results = self.results()
            round = self.round_number()
            good_moves = self.good_moves()

            db[self.db_path + f"history/{round}/scramble"] = db[self.db_path + "scramble"]
            db[self.db_path + f"history/{round}/good_moves"] = db[self.db_path + "good_moves"]
            for id in results:
                db[self.db_path + f"history/{round}/results/{id}"] = db[self.db_path + f"results/{id}"]

            del db[self.db_path + "scramble"]
            del db[self.db_path + "good_moves"]
            for id in results:
                del db[self.db_path + f"results/{id}"]

            msg = "Good moves: " + ", ".join(good_moves) + "\n"

            if len(results) == 0:
                msg += "No one joined :("
            else:
                winners = []
                for (id, m) in results.items():
                    if m in good_moves:
                        user = self.client.get_user(id)
                        winners.append(user.name)
                
                if len(winners) == 0:
                    msg += "Everyone was wrong :egglet:"
                else:
                    msg += "Winners: " + ", ".join(winners)

            await self.channel.send(msg)

    def submit(self, user, move):
        db[self.db_path + f"results/{user.id}"] = move
