import asyncio
import time
from log import log
import solver
from solver import SolverRunType
import scrambler
import move
from draw_state import draw_state
import helper.discord as dh

class MovesGameRound:
    def __init__(self, bot, channel, scramble=None, good_moves=None):
        self.bot = bot
        self.channel = channel
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

        log.info("starting movesgame round")
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

        # calculate good moves if not already given
        if self.good_moves is None:
            solutions = solver.solve(scramble, SolverRunType.GOOD)
            good_moves = "".join([move.to_string(sol.first()) for sol in solutions])
            log.info(f"found good moves: {good_moves}")
        else:
            good_moves = self.good_moves
            log.info(f"using given good moves: {good_moves}")

        # draw image
        img = draw_state(scramble)

        # post start message
        msg = f"Scramble: {scramble}"
        await dh.send_image(img, "scramble.png", msg, self.channel)

        # prepare to collect results
        self.results = {}

        # wait for people to submit moves and then close
        log.info(f"waiting {self.delay} seconds for submissions")
        await asyncio.sleep(self.delay)

        log.info("finishing movesgame round")
        self.running = False

        # return the round info as a dict
        return {
            "scramble"   : str(scramble),
            "good_moves" : good_moves,
            "timestamp"  : timestamp,
            "results"    : self.results
        }

    def submit(self, user, move):
        log.info(f"user {user} submitted {move}")
        self.results[user.id] = move

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != self.channel.id:
            return

        if self.running:
            m = message.content.upper()
            if len(m) == 1 and m in "ULDR":
                self.submit(message.author, m)
            elif len(m) == 5 and m in ["||U||", "||L||", "||D||", "||R||"]:
                self.submit(message.author, m[2])
