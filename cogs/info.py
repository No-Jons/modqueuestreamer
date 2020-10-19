import discord

from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def subreddits(self, ctx, username: str = None):
        self.bot.logger.info(f"Command subreddits invoked by {ctx.author.name}#{ctx.author.discriminator} "
                             f"{ctx.author.id}")
        if username is None:
            for i in self.bot.verified_users.keys():
                if i == str(ctx.author.id):
                    username = self.bot.verified_users[i]
            if username is None:
                await ctx.send("You aren't a verified user! Fix that by using the `r!register_me` command!")
                self.bot.logger.info("Verification failed: unregistered user")
                return
        redditor = self.bot.reddit.redditor(username)
        subs = str()
        sub_count = 0
        idx = 0
        for i in redditor.moderated():
            sub_count += i.subscribers
            idx += 1
            if idx <= 20:
                subs += f"{i.display_name}: {i.subscribers}\n"

        embed = discord.Embed(name=f"/u/{username}'s moderated subreddits",
                              description=f"Moderated subs: {idx}\nTotal subscribers: {sub_count}",
                              color=discord.Color.red())
        embed.add_field(name="Subreddits:", value=subs)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
