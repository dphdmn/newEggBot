import asyncio
import time
from log import log
import solver
from solver import SolverRunType
import scrambler
import move
from draw_state import draw_state
import helper.discord as dh

class OptimalGameRound:
    def __init__(self, bot, channel, scramble=None):
        self.bot = bot
        self.channel = channel
        self.running = False

        # time per round in seconds
        self.delay = 8

        # scramble, if given
        self.scramble = scramble

        # add on_message function as a listener
        bot.add_listener(self.on_message)

    async def run(self):
        if self.running:
            return

        log.info("starting optimal_game round")
        self.running = True

        # timestamp at the start of the round
        timestamp = int(time.time())

        # generate scramble if not already given
        if self.scramble is None:
            scramble = scrambler.getScramble(4)
            log.info(f"generated scramble: {scramble}")
        else:
            scramble = self.scramble
            log.info(f"using given scramble: {scramble}")

        # calculate optimal solution length
        solution = solver.solve(scramble, SolverRunType.ONE)
        opt_len = len(solution)
        log.info(f"optimal solution: {solution} ({opt_len})")

        # draw image
        img = draw_state(scramble)

        # post start message
        msg = f"Scramble: {scramble}"
        await dh.send_image(img, "scramble.png", msg, self.channel)

        # prepare to collect results
        self.results = {}

        # wait for people to submit guesses and then close
        log.info(f"waiting {self.delay} seconds for submissions")
        await asyncio.sleep(self.delay)

        log.info("finishing optimal_game round")
        self.running = False

        # return the round info as a dict
        return {
            "scramble"   : str(scramble),
            "solution"   : str(solution),
            "timestamp"  : timestamp,
            "results"    : self.results
        }

    def submit(self, user, length):
        log.info(f"user {user} submitted {length}")
        self.results[user.id] = length

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != self.channel.id:
            return

        if self.running:
            try:
                length = int(message.content)
                self.submit(message.author, length)
            except ValueError:
                pass

