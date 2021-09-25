import datetime as dt
from animate import make_video
from draw_state import draw_state
from puzzle_state import PuzzleState
from algorithm import Algorithm
from replit import db
from prettytable import PrettyTable
from fmc.round import FMCRound
import config.roles
import helper.discord as dh

class DailyFMC:
    def __init__(self, bot, channel_id, results_channel_id):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.results_channel = bot.get_channel(results_channel_id)
        self.db_path = f"{self.channel.guild.id}/fmc/{self.channel.id}/"

        self.round = FMCRound(self.db_path, warnings=[23*3600], on_close=self.on_close, on_warning=self.on_warning)

    async def start(self):
        if self.round.running():
            return

        await self.channel.send("Starting daily FMC, please wait!")

        self.round.open()

        scramble = self.round.get_scramble()
        solution = self.round.get_solution()

        msg  = f"Daily FMC scramble: {scramble}\n"
        msg += f"Optimal solution length: {len(solution)}\n"
        msg +=  "Use **!submit** command to submit solutions (You can submit multiple times!), for example:\n"
        msg +=  "!submit LUR2DL2URU2LDR2DLUR2D2LU3RD3LULU2RDLDR2ULDLURUL2"

        img = draw_state(scramble)
        await dh.send_image(img, "scramble.png", msg, self.channel)

        # ping fmc role
        await self.channel.send(f"<@&{config.roles.fmc}>")

    async def finish(self, round_dict):
        results = round_dict["results"]
        date = dt.datetime.utcfromtimestamp(round_dict["timestamp"]).strftime("%Y-%m-%d")
        scramble = PuzzleState(round_dict["scramble"])
        optSolution = Algorithm(round_dict["solution"])
        optLength = len(optSolution)

        db[self.db_path + f"history/{date}/scramble"] = str(scramble)
        db[self.db_path + f"history/{date}/solution"] = str(optSolution)
        for id in results:
            db[self.db_path + f"history/{date}/results/{id}"] = str(results[id])

        msg  =  "Daily FMC results!\n"
        msg += f"Date: {date}\n"
        msg += f"Scramble: {scramble}\n"
        msg += f"Optimal solution [{optLength}]: {optSolution}"

        if len(results) == 0:
            msg += "\n\nNo one joined :("
            await self.channel.send(msg)
            await self.results_channel.send(msg)
        else:
            table = PrettyTable()
            table.field_names = ["Username", "Moves", "To optimal", "Solution"]

            # organise results in an array
            for (id, solution) in results.items():
                user = self.bot.get_user(id)
                length = len(solution)
                table.add_row([user.name, length, length - optLength, str(solution)])

            await dh.send_as_file(table.get_string(), "results.txt", msg, self.channel)
            await dh.send_as_file(table.get_string(), "results.txt", msg, self.results_channel)

        make_video(scramble, optSolution, 8)
        await dh.send_binary_file("movie.webm", "", self.channel)

    async def on_close(self, round_dict):
        # close and open, but set the start time to exactly 86400 seconds after the previous
        # start time, otherwise there will be a slight shift in start time over many rounds
        await self.finish(round_dict)
        await self.start()

        timestamp = round_dict["timestamp"]
        db[self.round.db_path + "start_time"] = timestamp + self.round.duration

    async def on_warning(self, warning):
        if warning == 23*3600:
            await self.channel.send("One hour remaining!")

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
