import discord

from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def close(self, ctx):
        self.bot.logger.info("Closing bot")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def queuedata(self, ctx):
        await ctx.send(
            f"```\nObjects in queue: {len(self.bot.event_queue)}\n"
            f"Total objects streamed: {self.bot.streamed_counter}\n```"
        )

    @commands.command()
    @commands.is_owner()
    async def dumpdata(self, ctx):
        self.bot.dump_data()
        await ctx.send("Finished dumping bot data")

    @commands.command()
    @commands.is_owner()
    async def prawconnection(self, ctx):
        try:
            redditor = self.bot.reddit.redditor('modqueuestreamer')
            await ctx.send("Connection is still open!")
        except:
            await ctx.send("Connection has been closed, please reload connection.")

    @commands.command()
    @commands.is_owner()
    async def forcenewconnection(self, ctx):
        self.bot.reddit = self.bot.create_reddit_connection()
        await ctx.send("Connection created")


def setup(bot):
    bot.add_cog(Admin(bot))
