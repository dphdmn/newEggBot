from algorithm import Algorithm
from optimal_game.round import OptimalGameRound
from database import db
from puzzle_state import PuzzleState

class OptimalGame:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/optimal_game/{self.channel.id}/"
        self.running = False

        # number of rounds to store in each "block" in the database, using a single key
        self.block_size = 100

        # initialize db keys
        if self.db_path + "lifetime_results" not in db:
            db[self.db_path + "lifetime_results"] = {}
        if self.db_path + "round_number" not in db:
            # -1 so that the first round is round 0
            db[self.db_path + "round_number"] = -1

    def round_number(self):
        return db[self.db_path + "round_number"]

    def lifetime_results(self):
        key = self.db_path + "lifetime_results"
        return db[key]

    async def start(self):
        if self.running:
            return

        self.running = True

        # run the round
        round = await OptimalGameRound(self.bot, self.channel).run()

        # increment the round number
        db[self.db_path + "round_number"] += 1

        # store the history in blocks of n rounds per key
        round_num = self.round_number()
        block       = round_num // self.block_size
        block_round = round_num  % self.block_size

        # get the block and add the round to it
        block_path = self.db_path + f"history/round_blocks/{block}"
        if block_round == 0:
            block_dict = {}
        else:
            block_dict = db[block_path]
        block_dict[block_round] = round
        db[block_path] = block_dict

        solution = Algorithm(round["solution"])
        opt_len = len(solution)
        msg = f"Optimal length: {opt_len}\n"

        # update lifetime results
        lifetime_results = self.lifetime_results()
        results = round["results"]
        if len(results) == 0:
            msg += "No one joined :("
        else:
            for (id, guess) in results.items():
                # if this is the users first round, create lifetime results entries
                if id not in lifetime_results:
                    lifetime_results[id] = {
                        "distance"  : 0,
                        "rounds"    : 0
                    }

                lifetime_results[id]["distance"] += abs(opt_len - guess)
                lifetime_results[id]["rounds"] += 1
            
            msg += "Results:\n"
            results = dict(sorted(results.items(), key=lambda x: abs(opt_len - x[1])))
            
            for (i, (id, guess)) in enumerate(results.items()):
                user = self.bot.get_user(id)
                diff = guess - opt_len
                if diff == 0:
                    diff_str = ""
                elif diff < 0:
                    diff_str = f" ({diff})"
                else:
                    diff_str = f" (+{diff})"
                msg += f"{i+1}. {user.name}{diff_str}\n"

        # store the updated lifetime results
        db[self.db_path + "lifetime_results"] = lifetime_results

        await self.channel.send(msg)

        self.running = False

    # given a scramble, find the round number that had it
    def find_scramble(self, scramble: PuzzleState):
        keys = db.prefix(self.db_path + "history/round_blocks/")
        for key in keys:
            block_num = int(key.split("/")[-1])
            block = db[key]
            for j in range(self.block_size):
                r = block[j]
                round_scramble = PuzzleState(r["scramble"])
                if round_scramble == scramble:
                    return self.block_size * block_num + j
        raise Exception("scramble not found")

    # delete a users historical result
    def delete_result(self, round_num, user):
        block       = round_num // self.block_size
        block_round = round_num  % self.block_size

        key = self.db_path + f"history/round_blocks/{block}"
        b = db[key]
        r = b[block_round]
        solution = Algorithm(r["solution"])

        # update lifetime results
        lifetime_results = db[self.db_path + "lifetime_results"]
        user_results = lifetime_results[user]
        user_length = r["results"][user]
        opt_length = len(solution)
        distance = abs(opt_length - user_length)
        user_results["distance"] -= distance
        user_results["rounds"] -= 1
        lifetime_results["user"] = user_results
        db[self.db_path + "lifetime_results"] = lifetime_results

        # delete their results
        del b[block_round]["results"][user]
        db[key] = b
