import discord
import praw


class Checks:
    def __init__(self, bot):
        self.bot = bot
        self._emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

    async def get_subreddit(self, ctx, subreddit):
        subs = list()
        # todo: multi-page subreddit choice for multi-sub guilds?
        for item in self.bot.channel_config.keys():  # holy shit this code sucks
            if self.bot.channel_config[item]["guild"] == ctx.guild.id:
                if item == subreddit.lower():
                    break
                subs.append(item)
        if not subreddit:
            if len(subs) == 0:
                await ctx.send("Your subreddit has not been verified yet! Fix that by using the `r!register` command!")
                self.bot.logger.info("Verification failed: no subreddit provided")
                return None
            if len(subs) > 1:
                if len(subs) > 9:
                    subs = subs[:9]
                # todo: selection embed
                embed = discord.Embed(title="Choose a subreddit to edit the config of:", color=discord.Color.green())
                for i in range(len(subs)):
                    embed.add_field(name=f"{self._emojis[i]}.", value=f"/r/{subs[i]}")
                message = await ctx.send(embed=embed)
                for i in range(len(subs)):
                    await message.add_reaction(self._emojis[i])
                r, u = await self.bot.wait_for('reaction_add',
                                          check= lambda r, u: r.emoji in self._emojis and u.id == ctx.author.id)
                await message.delete()
                list_index = self._emojis.index(r.emoji)
                return subs[list_index]
        else:
            return subreddit

    async def get_username(self, ctx):
        username = None
        for i in self.bot.verified_users.keys():
            if i == str(ctx.author.id):
                username = self.bot.verified_users[i]
        if username is None:
            await ctx.send("You are not a verified user yet! Fix that by using the `r!register_me` command!")
            self.bot.logger.info("Verification failed: unverified user")
        return username

    async def user_is_mod(self, ctx, redditor, subreddit):
        if subreddit.lower() not in [i.display_name.lower() for i in redditor.moderated()]:
            await ctx.send("You can't register this bot on a subreddit that you don't mod!")
            self.bot.logger.info("Verification failed: invalid user")
            return False
        return True

    async def user_is_verified(self, ctx, username):
        if username.lower() in self.bot.verified_users.values():
            await ctx.send(f"You're already verified as /u/{username}")
            self.bot.logger.info("Verification failed: user already verified")
            return True
        return False

    async def subreddit_is_verified(self, ctx, subreddit):
        if subreddit.lower() in self.bot.channel_config:
            await ctx.send("Your subreddit is already verified!")
            self.bot.logger.info("Verification failed, subreddit already verified")
            return True
        return False

    async def get_redditor(self, ctx, username):
        try:
            redditor = self.bot.reddit.redditor(username)
        except praw.reddit.RedditAPIException as e:
            await ctx.send(f"No user found with username /u/{username}")
            self.bot.logger.info(f"Verification failed, invalid user: {e}")
            return None
        return redditor
