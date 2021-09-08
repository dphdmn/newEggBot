import random
import time
from helper import serialize
from discord.ext import tasks
from replit import db

class RandomGame:
    def __init__(self, bot, channel_ids, freq):
        self.bot = bot
        self.channels = [bot.get_channel(c) for c in channel_ids]
        self.db_path = str(self.channels[0].guild.id) + "/random_game/"
        self.freq = freq
        self.running = False

        bot.add_listener(self.on_message)

        # initialize db keys
        if self.db_path + "scores" not in db:
            db[self.db_path + "scores"] = serialize.serialize({})
        if self.db_path + "rounds" not in db:
            db[self.db_path + "rounds"] = serialize.serialize({})
        if self.db_path + "round_number" not in db:
            # -1 so that the first round is round 0
            db[self.db_path + "round_number"] = -1

        # if there's already a round running and the bot was restarted for some reason, just delete it
        for x in db.prefix(self.db_path + "current"):
            del db[x]

    def start(self):
        self.loop.start()

    async def run(self):
        self.running = True

        channel = random.choice(self.channels)
        message = await channel.send(":egg: Egg! :egg:")

        timestamp = time.time()

        db[self.db_path + "current/message_id"] = message.id
        db[self.db_path + "current/channel_id"] = message.channel.id
        db[self.db_path + "current/timestamp"] = timestamp

    async def finish(self, winner_message, winner_timestamp):
        db[self.db_path + "round_number"] += 1

        round_number = db[self.db_path + "round_number"]
        message_id = db[self.db_path + "current/message_id"]
        channel_id = db[self.db_path + "current/channel_id"]
        timestamp = db[self.db_path + "current/timestamp"]
        winner_id = winner_message.author.id

        # store the round in the db
        round = {
            "message"          : message_id,
            "channel"          : channel_id,
            "timestamp"        : timestamp,
            "winner"           : winner_id,
            "winner_message"   : winner_message.id,
            "winner_timestamp" : winner_timestamp
        }
        rounds = serialize.deserialize(db[self.db_path + "rounds"])
        rounds[round_number] = round
        db[self.db_path + "rounds"] = serialize.serialize(rounds)

        # add a point to the lifetime scores
        scores = serialize.deserialize(db[self.db_path + "scores"])
        if winner_id not in scores:
            scores[winner_id] = 1
        else:
            scores[winner_id] += 1
        db[self.db_path + "scores"] = serialize.serialize(scores)

        del db[self.db_path + "current/message_id"]
        del db[self.db_path + "current/channel_id"]
        del db[self.db_path + "current/timestamp"]

        await winner_message.reply(f"You win!")

        self.running = False

    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return

        if not self.running:
            return

        # get the timestamp now so we don't include extra time used by the bot
        timestamp = time.time()

        id = db[self.db_path + "current/channel_id"]
        if message.channel.id == id:
            if message.content == "egg":
                await self.finish(message, timestamp)

    @tasks.loop(seconds=1)
    async def loop(self):
        if self.running:
            return

        n = random.randint(1, self.freq)
        print(f"random number: {n}")
        if n == 1:
            await self.run()
