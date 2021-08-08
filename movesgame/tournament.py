from collections import Counter
import random
import asyncio
import scrambler
from movesgame.round import MovesGameRound
from algorithm import Algorithm

class Tournament:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.running = False

    async def run(self):
        if self.running:
            return

        # helper function to get username from id
        def name(id):
            return self.bot.get_user(id).name

        self.running = True

        # generate a scramble to use
        scramble = scrambler.getScramble(4)

        # start running the rounds
        round_num = 0
        rounds = {}
        while True:
            await self.channel.send(f"Starting round {round_num+1}!")

            # run the round
            round = await MovesGameRound(self.bot, self.channel, scramble=scramble).run()
            
            # the players in the tournament are whoever submitted in the first round
            if round_num == 0:
                players = list(round["results"].keys())
                still_in = {x : 1 for x in players}

                # if <2 players, we can't run a tournament
                if len(players) < 2:
                    await self.channel.send("Sorry, can't run a tournament with fewer than 2 players")
                    return None
            # if not the first round, delete the results of anyone who isn't still in
            else:
                results = round["results"]
                for id in results:
                    if id not in players or not still_in[id]:
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
                msg += "The winners are " + ", ".join(["**" + name(id) + "**" for id in still_in_before_round])
                tournament_over = True
            elif len(losers) == 0:
                msg += f"Everyone continues to round {round_num+2}!"
            elif len(winners) == 1:
                winner = list(winners)[0]
                msg += f"**{name(winner)}** is the winner!\n"
                msg += "Everyone else was eliminated"
                tournament_over = True
            else:
                msg += ", ".join(["**" + name(id) + "**" for id in winners]) + f" continue to round {round_num+2}!\n"
                msg += ", ".join([name(id) for id in losers]) + " were eliminated"

            await self.channel.send(msg)

            if tournament_over:
                break

            # find the most common correct move suggestion
            winner_moves = {id: move for (id, move) in round["results"].items() if id in winners}
            move_amounts = Counter(winner_moves)
            max_frequency = max(move_amounts.values())
            commonest_moves = [move for move in "ULDR" if move_amounts[move] == max_frequency]

            # if there are multiple commonest moves, pick one at random
            next_move = random.choice(commonest_moves)
            scramble.apply(Algorithm(next_move))

            # increment the round number
            round_num += 1

            await self.channel.send("Next round will start in 5 seconds")
            await asyncio.sleep(5)

        self.running = False

        return rounds
