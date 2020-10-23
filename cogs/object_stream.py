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
            self.update_cache.start()
            self.dump_bot_data.start()
            self.refresh_reddit_connection.start()
        except RuntimeError:
            pass

    @tasks.loop(seconds=10.0)
    async def read_queue(self):
        for obj in self.bot.event_queue.queue:
            try:
                message = await obj["channel"].send(embed=obj["embed"])
                self.bot.event_queue.remove(obj)
                self.bot.obj_cache.add({"obj" : obj["obj"], "message" : message})
            except discord.Forbidden:
                self.bot.logger.error("Invalid permissions, not able to send messages...")
        self.bot.logger.debug("Executed task read_queue")

    @tasks.loop(minutes=10.0)
    async def update_cache(self):
        for obj in self.bot.obj_cache.queue:
            try:
                await self.bot.obj_cache.update(obj["obj"], obj["message"])
            except discord.HTTPException:
                self.bot.logger.error(f"Could not update message {obj['message'].id}")
        self.bot.logger.info("Executed task update_cache")

    @tasks.loop(minutes=30.0)
    async def dump_bot_data(self):
        self.bot.dump_data()

    @tasks.loop(minutes=30.0)
    async def refresh_reddit_connection(self):
        self.bot.reddit = self.bot.create_reddit_connection()


def setup(bot):
    bot.add_cog(ObjStream(bot))
