from movesgame.round import MovesGameRound
from database import db
from puzzle_state import PuzzleState

class MovesGame:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/movesgame/{self.channel.id}/"
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
        round = await MovesGameRound(self.bot, self.channel).run()

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

        msg = "Good moves: " + ", ".join(round["good_moves"]) + "\n"

        # find winners and update lifetime results
        lifetime_results = self.lifetime_results()
        if len(round["results"]) == 0:
            msg += "No one joined :("
        else:
            winners = []
            for (id, m) in round["results"].items():
                # if this is the users first movesgame, create lifetime results entries
                if id not in lifetime_results:
                    lifetime_results[id] = {
                        "correct"   : 0,
                        "incorrect" : 0
                    }

                if m in round["good_moves"]:
                    user = self.bot.get_user(id)
                    winners.append(user.name)
                    lifetime_results[id]["correct"] += 1
                else:
                    lifetime_results[id]["incorrect"] += 1
            
            if len(winners) == 0:
                msg += "Everyone was wrong :egg:"
            else:
                msg += "Winners: " + ", ".join(winners)

        # store the updated lifetime results
        db[self.db_path + "lifetime_results"] = lifetime_results

        await self.channel.send(msg)

        self.running = False

    # given a scramble, find the round number that had it
    def find_scramble(self, scramble: PuzzleState):
        keys = db.prefix(self.db_path + "history/round_blocks/")
        for (i, key) in enumerate(keys):
            block = db[key]
            for j in range(self.block_size):
                r = block[j]
                round_scramble = PuzzleState(r["scramble"])
                if round_scramble == scramble:
                    return self.block_size * i + j
        raise Exception("scramble not found")

    # delete a users historical result
    def delete_result(self, round_num, user):
        block       = round_num // self.block_size
        block_round = round_num  % self.block_size

        key = self.db_path + f"history/round_blocks/{block}"
        b = db[key]
        r = b[block_round]

        # update lifetime results
        lifetime_results = db[self.db_path + "lifetime_results"]
        user_results = lifetime_results[user]
        good_moves = r["good_moves"]
        user_move = r["results"][user]
        if user_move in good_moves:
            user_results["correct"] -= 1
        else:
            user_results["incorrect"] -= 1
        lifetime_results["user"] = user_results
        db[self.db_path + "lifetime_results"] = lifetime_results

        # delete their results
        del b[block_round]["results"][user]
        db[key] = b
