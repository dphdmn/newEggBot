import asyncio
import time
import os
from solver import solvers
import scrambler
import move
from draw_state import draw_state
import discord
from replit import db

class MovesGameRound:
    def __init__(self, bot, channel, scramble=None, good_moves=None):
        self.bot = bot
        self.channel = channel
        self.db_path = f"{self.channel.guild.id}/movesgame/{self.channel.id}/"
        self.running = False

        # time per round in seconds
        self.delay = 8

        # scramble and good moves, if given
        self.scramble = scramble
        self.good_moves = good_moves

        # add on_message function as a listener
        bot.add_listener(self.on_message)

    async def run(self):
        if self.running:
            return

        self.running = True

        # timestamp at the start of the round
        timestamp = int(time.time())

        # delete any results from the database that were left from a previous round
        for key in db.prefix(self.db_path + "current"):
            del db[key]

        # generate scramble if not already given
        if self.scramble is None:
            scramble = scrambler.getScramble(4)
        else:
            scramble = self.scramble

        # calculate good moves if not already given
        if self.good_moves is None:
            solutions = solvers[4].solveGood(scramble)
            good_moves = "".join([move.to_string(sol.first()) for sol in solutions])
        else:
            good_moves = self.good_moves

        # draw image
        img = draw_state(scramble)
        img.save("scramble.png", "PNG")

        # post start message
        with open("scramble.png", "rb") as f:
            msg = f"Scramble: {scramble.to_string()}"
            img = discord.File(f)
            await self.channel.send(msg, file=img)
        os.remove("scramble.png")

        # wait for people to submit moves and then close
        await asyncio.sleep(self.delay)

        # get results
        keys = db.prefix(self.db_path + "current/results")
        results = {}
        for key in keys:
            id = int(key.split("/")[-1])
            results[id] = db[key]

        self.running = False

        # return the round info as a dict
        return {
            "scramble"   : scramble.to_string(),
            "good_moves" : good_moves,
            "timestamp"  : timestamp,
            "results"    : results
        }

    def submit(self, user, move):
        db[self.db_path + f"current/results/{user.id}"] = move

    async def on_message(self, message):
        if message.channel.id != self.channel.id:
            return

        if self.running:
            m = message.content.upper()
            if len(m) == 1 and m in "ULDR":
                self.submit(message.author, m)