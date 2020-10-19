import discord
import json

from discord.ext import commands, tasks


class ObjStream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("Started streaming objects")
        try:
            self.read_queue.start()
            self.dump_bot_data.start()
        except RuntimeError:
            pass

    @tasks.loop(seconds=10.0)
    async def read_queue(self):
        for obj in self.bot.event_queue:
            try:
                await obj["channel"].send(embed=obj["embed"])
                self.bot.event_queue.remove(obj)
                self.bot.streamed_counter += 1
            except discord.Forbidden:
                self.bot.logger.error("Invalid permissions, not able to send messages...")
        self.bot.logger.debug("Executed task read_queue")

    @tasks.loop(minutes=30.0)
    async def dump_bot_data(self):
        self.bot.dump_data()


def setup(bot):
    bot.add_cog(ObjStream(bot))
