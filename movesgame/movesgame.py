from helper import serialize
from movesgame.round import MovesGameRound
from database import db

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
            db[self.db_path + "lifetime_results"] = serialize.serialize({})
        if self.db_path + "round_number" not in db:
            # -1 so that the first round is round 0
            db[self.db_path + "round_number"] = -1

    def round_number(self):
        return db[self.db_path + "round_number"]

    def lifetime_results(self):
        key = self.db_path + "lifetime_results"
        return serialize.deserialize(db[key])

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
            block_dict = serialize.deserialize(db[block_path])
        block_dict[block_round] = round
        db[block_path] = serialize.serialize(block_dict)

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
        db[self.db_path + "lifetime_results"] = serialize.serialize(lifetime_results)

        await self.channel.send(msg)

        self.running = False
