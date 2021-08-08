import asyncio
import time
import os
from solver import solvers
import scrambler
import move
from draw_state import draw_state
from helper import serialize
import discord
from replit import db

class MovesGame:
    def __init__(self, client, channel_id):
        self.client = client
        self.channel = client.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/movesgame/{self.channel.id}/"

        # time per round in seconds
        self.delay = 8

        # number of rounds to store in each "block" in the database, using a single key
        self.block_size = 100

        # initialize db keys
        db[self.db_path + "status"] = "closed"
        db[self.db_path + "lifetime_results"] = serialize.serialize({})

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

    def lifetime_results(self):
        key = self.db_path + "lifetime_results"
        return serialize.deserialize(db[key])

    async def open(self):
        if self.is_open():
            pass
        else:
            db[self.db_path + "status"] = "open"

            # if there is no key in the db showing how many rounds there have been
            # then this must be the first time we are running movesgame
            if self.db_path + "round_number" not in db:
                db[self.db_path + "round_number"] = 0
            else:
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
            db[self.db_path + "timestamp"] = int(time.time())

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

            # store the data from the round in a dict
            round_dict = {
                "scramble"   : db[self.db_path + "scramble"],
                "good_moves" : db[self.db_path + "good_moves"],
                "timestamp"  : db[self.db_path + "timestamp"],
                "results"    : results
            }

            # store the history in blocks of n rounds per key
            block       = round // self.block_size
            block_round = round  % self.block_size

            # get the block and add the round to it
            block_path = self.db_path + f"history/round_blocks/{block}"
            if block_round == 0:
                block_dict = {}
            else:
                block_dict = serialize.deserialize(db[block_path])
            block_dict[block_round] = round_dict
            db[block_path] = serialize.serialize(block_dict)

            del db[self.db_path + "scramble"]
            del db[self.db_path + "good_moves"]
            del db[self.db_path + "timestamp"]
            for id in results:
                del db[self.db_path + f"results/{id}"]

            msg = "Good moves: " + ", ".join(good_moves) + "\n"

            # find winners and update lifetime results
            lifetime_results = self.lifetime_results()
            if len(results) == 0:
                msg += "No one joined :("
            else:
                winners = []
                for (id, m) in results.items():
                    # if this is the users first movesgame, create lifetime results entries
                    if id not in lifetime_results:
                        lifetime_results[id] = {
                            "correct"   : 0,
                            "incorrect" : 0
                        }

                    if m in good_moves:
                        user = self.client.get_user(id)
                        winners.append(user.name)
                        lifetime_results[id]["correct"] += 1
                    else:
                        lifetime_results[id]["incorrect"] += 1
                
                if len(winners) == 0:
                    msg += "Everyone was wrong :egg:"
                else:
                    msg += "Winners: " + ", ".join(winners)

            # store the updated lifetime results
            db[self.db_path + "lifetime_results"] = serialize.serialize(lifetime_results)

            await self.channel.send(msg)

    def submit(self, user, move):
        db[self.db_path + f"results/{user.id}"] = move
