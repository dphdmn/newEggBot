from collections import Counter
import random
import asyncio
import time
import scrambler
from helper import serialize
from movesgame.round import MovesGameRound
from algorithm import Algorithm
from replit import db

class MovesGameTournament:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/movesgame_tournament/{self.channel.id}/"
        self.running = False

        # number of tournaments per block
        self.block_size = 25

        if self.db_path + "tournament_number" not in db:
            # -1 so that the first tournament is 0
            db[self.db_path + "tournament_number"] = -1

    def tournament_number(self):
        return db[self.db_path + "tournament_number"]

    async def run(self):
        if self.running:
            return

        timestamp = int(time.time())

        # helper function to get username from id
        def name(id):
            return self.bot.get_user(id).name

        self.running = True

        # generate a scramble to use
        scramble = scrambler.getScramble(4)

        # initialize an empty solution algorithm
        solution = Algorithm("")

        # start running the rounds
        round_num = 0
        rounds = {}
        while True:
            await self.channel.send(f"Starting round {round_num+1}!")

            # run the round
            round = await MovesGameRound(self.bot, self.channel, scramble=scramble).run()

            # don't need to store timestamp or scramble for every single round
            # we store the timestamp at the beginning of the tournament, and the scramble and moves that were applied
            del round["timestamp"]
            del round["scramble"]

            # the players in the tournament are whoever submitted in the first round
            if round_num == 0:
                players = list(round["results"].keys())
                still_in = {x : 1 for x in players}

                # if <2 players, we can't run a tournament
                if len(players) < 2:
                    await self.channel.send("Sorry, can't run a tournament with fewer than 2 players")
                    self.running = False
                    return
            # if not the first round, delete the results of anyone who isn't still in
            else:
                results = round["results"]
                entries_to_delete = [id for id in results if id not in players or not still_in[id]]
                for id in entries_to_delete:
                    del results[id]
                round["results"] = results

            # store the round in rounds
            rounds[round_num] = round

            # eliminate players who were wrong
            msg = "Good moves: " + ", ".join(round["good_moves"]) + "\n"
            winners = set()
            still_in_before_round = set([id for id in players if still_in[id]])
            for (id, m) in round["results"].items():
                if m in round["good_moves"]:
                    winners.add(id)
                else:
                    still_in[id] = 0
            losers = still_in_before_round.difference(winners)

            # check a few conditions for the tournament to be over
            tournament_over = False
            if len(winners) == 0:
                msg += "Everyone was eliminated!\n"
                if round_num == 0:
                    msg += "There are no winners."
                    tournament_winners = set()
                else:
                    msg += "The winners are " + ", ".join(["**" + name(id) + "**" for id in still_in_before_round])
                    tournament_winners = still_in_before_round
                tournament_over = True
            else:
                # find the most common correct move suggestion
                winner_moves = {id: move for (id, move) in round["results"].items() if id in winners}
                move_amounts = Counter(winner_moves.values())
                max_frequency = max(move_amounts.values())
                commonest_moves = [move for move in "ULDR" if move_amounts[move] == max_frequency]

                # if there are multiple commonest moves, pick one at random
                next_move = random.choice(commonest_moves)
                next_move_alg = Algorithm(next_move)
                scramble.apply(next_move_alg)
                solution += next_move_alg

                if scramble.solved():
                    msg += "The puzzle is solved!\n"
                    msg += "The winners are " + ", ".join(["**" + name(id) + "**" for id in winners]) + "!"
                    tournament_winners = winners
                    tournament_over = True
                elif len(losers) == 0:
                    msg += f"Everyone continues to round {round_num+2}!"
                elif len(winners) == 1:
                    winner = list(winners)[0]
                    msg += f"**{name(winner)}** is the winner!\n"
                    msg += "Everyone else was eliminated"
                    tournament_winners = winners
                    tournament_over = True
                else:
                    msg += ", ".join(["**" + name(id) + "**" for id in winners]) + f" continue to round {round_num+2}!\n"
                    if len(losers) == 1:
                        loser = list(losers)[0]
                        msg += loser + " was eliminated"
                    else:
                        msg += ", ".join([name(id) for id in losers]) + " were eliminated"

            await self.channel.send(msg)

            if tournament_over:
                break

            # increment the round number
            round_num += 1

            await self.channel.send("Next round will start in 5 seconds")
            await asyncio.sleep(5)

        # store in the db
        db[self.db_path + "tournament_number"] += 1
        tournament_num = self.tournament_number()

        block       = tournament_num // self.block_size
        block_round = tournament_num  % self.block_size

        block_path = self.db_path + f"history/blocks/{block}"
        if block_round == 0:
            block_dict = {}
        else:
            block_dict = serialize.deserialize(db[block_path])
        block_dict[block_round] = {
            "scramble" : str(scramble),
            "solution" : str(solution),
            "rounds"   : rounds,
            "winners"  : tournament_winners
        }
        db[block_path] = serialize.serialize(block_dict)

        self.running = False
