import os
import copy
from animate import make_video
from draw_state import draw_state
from puzzle_state import PuzzleState
from algorithm import Algorithm
from helper import serialize
from replit import db
import discord
from prettytable import PrettyTable
from fmc.round import FMCRound
import helper.discord as dh

class FMC:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/fmc/{self.channel.id}/"
        self.block_size = 100

        self.round = FMCRound(self.db_path, duration=600, warnings=[60*5, 60*9], on_close=self.on_close, on_warning=self.on_warning)

        if self.db_path + "round_number" not in db:
            # -1 so that the first round is round 0
            db[self.db_path + "round_number"] = -1

    def round_number(self):
        return db[self.db_path + "round_number"]

    async def start(self):
        if self.round.running():
            return

        await self.channel.send("Starting FMC, please wait!")

        self.round.open()

        scramble = self.round.get_scramble()
        solution = self.round.get_solution()

        msg  = f"FMC scramble: {scramble}\n"
        msg += f"Optimal solution length: {len(solution)}\n"
        msg +=  "Use **!submit** command to submit solutions (You can submit multiple times!), for example:\n"
        msg +=  "!submit LUR2DL2URU2LDR2DLUR2D2LU3RD3LULU2RDLDR2ULDLURUL2"

        img = draw_state(scramble)
        await dh.send_image(img, "scramble.png", msg, self.channel)

    async def finish(self, round_dict):
        results = round_dict["results"]
        scramble = PuzzleState(round_dict["scramble"])
        optSolution = Algorithm(round_dict["solution"])
        optLength = len(optSolution)

        db[self.db_path + "round_number"] += 1

        # store the round in a block
        round_num = self.round_number()
        block       = round_num // self.block_size
        block_round = round_num  % self.block_size

        # get the block and add the round to it
        block_path = self.db_path + f"history/round_blocks/{block}"
        if block_round == 0:
            block_dict = {}
        else:
            block_dict = serialize.deserialize(db[block_path])

        # same as round_dict, but we convert the solutions to strings
        round_dict2 = copy.deepcopy(round_dict)
        for id in round_dict2["results"]:
            round_dict2["results"][id] = str(round_dict2["results"][id])

        block_dict[block_round] = round_dict2
        db[block_path] = serialize.serialize(block_dict)

        msg  =  "FMC results\n"
        msg += f"Scramble: {scramble}\n"
        msg += f"Optimal solution [{optLength}]: {optSolution}"

        if len(results) == 0:
            msg += "\n\nNo one joined :("
            await self.channel.send(msg)
        else:
            table = PrettyTable()
            table.field_names = ["Username", "Moves", "To optimal", "Solution"]

            # organise results in an array
            for (id, solution) in results.items():
                user = self.bot.get_user(id)
                length = len(solution)
                table.add_row([user.name, length, length - optLength, str(solution)])

            await dh.send_as_file(table.get_string(), "results.txt", msg, self.channel)

        make_video(scramble, optSolution, 8)
        with open("movie.webm", "rb") as f:
            picture = discord.File(f)
            await self.channel.send("", file=picture)
        os.remove("movie.webm")

    async def on_close(self, round_dict):
        await self.finish(round_dict)

    async def on_warning(self, warning):
        if warning == 60*5:
            await self.channel.send("5 minutes remaining!")
        elif warning == 60*9:
            await self.channel.send("One minute remaining!")

    async def submit(self, user, solution):
        id = user.id
        name = user.name

        # check if the user has already submitted a solution
        if self.round.has_result(id):
            previous_length = len(self.round.result(id))
        else:
            previous_length = None
        new_length = len(solution)

        # submit the new solution
        self.round.submit(id, solution)

        # send message
        if previous_length is None:
            await self.channel.send(f"[{new_length}] Solution added for {name}")
        else:
            if new_length < previous_length:
                await self.channel.send(f"[{previous_length} -> {new_length}] Solution updated for {name}")
            else:
                await self.channel.send(f"[{new_length}] You already have a {previous_length} move solution, {name}")
