from helper import serialize
from movesgame.round import MovesGameRound
from replit import db

class MovesGame:
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel = bot.get_channel(channel_id)
        self.db_path = f"{self.channel.guild.id}/movesgame/{self.channel.id}/"

        # time per round in seconds
        self.delay = 8

        # number of rounds to store in each "block" in the database, using a single key
        self.block_size = 100

        # initialize db keys
        db[self.db_path + "status"] = "closed"
        db[self.db_path + "lifetime_results"] = serialize.serialize({})

    def is_open(self):
        return db[self.db_path + "status"] == "open"

    def round_number(self):
        return db[self.db_path + "round_number"]

    def lifetime_results(self):
        key = self.db_path + "lifetime_results"
        return serialize.deserialize(db[key])

    async def open(self):
        if self.is_open():
            pass
        else:
            db[self.db_path + "status"] = "open"

            # run the round
            round = await MovesGameRound(self.bot, self.channel).run()

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

            db[self.db_path + "status"] = "closed"

    def submit(self, user, move):
        db[self.db_path + f"current/results/{user.id}"] = move
