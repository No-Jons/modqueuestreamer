import discord
import praw

from discord.ext import commands
from utils.etc import create_code
from utils.checks import Checks


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checks = Checks(self.bot)

    @commands.command(aliases=['verify', 'verify_sr'])
    async def register(self, ctx, subreddit: str, username: str = None,
                       modqueue_channel: discord.TextChannel = None, modmail_channel: discord.TextChannel = None):
        self.bot.logger.info(f"Starting verification process on subreddit /r/{subreddit} "
                             f"invoked by {ctx.author.name}#{ctx.author.discriminator} {ctx.author.id} /u/{username}")
        modqueue_channel = modqueue_channel or ctx.channel
        modmail_channel = modmail_channel or modqueue_channel
        if username is None:
            username = await self.checks.get_username(ctx)
        to_msg = await self.checks.get_redditor(ctx, username)
        if not await self.checks.user_is_mod(ctx, to_msg, subreddit) \
                or await self.checks.subreddit_is_verified(ctx, subreddit):
            return
        verification_code = create_code()
        to_msg.message(subject=f"Verification for /r/{subreddit} setup",
                       message=f"Hello! "
                       f"If you did not expect to receive this message, please ignore it.\n"
                       f"Your verification code is {verification_code}.\n"
                       f"\n^Requested ^by ^{ctx.author.name}#{ctx.author.discriminator} ^{ctx.author.id}")
        await ctx.send(f"Sent a PM to /u/{username}, send the verification code (the six numbers sent by the bot) "
                       f"to *this channel* to verify /r/{subreddit}")
        self.bot.verification_queue[username] = {"subreddit" : subreddit, "channel" : ctx.channel,
                                                 "modqueue" : modqueue_channel, "modmail" : modmail_channel,
                                                 "username" : username, "author" : ctx.author,
                                                 "code" : verification_code}
        self.bot.logger.info(f"Added user /u/{username} and subreddit /r/{subreddit} to verification queue")

    @commands.command(aliases=['verify_me'])
    async def register_me(self, ctx, username: str):
        self.bot.logger.info(f"Starting verification for /u/{username}")
        if await self.checks.user_is_verified(ctx, username):
            return
        to_msg = await self.checks.get_redditor(ctx, username)
        verification_code = create_code()
        to_msg.message(subject=f"Verification for /u/{username}",
                       message=f"Hello! "
                       f"If you did not expect to receive this message, please ignore it.\n"
                       f"Your verification code is {verification_code}.\n"
                       f"\n^Requested ^by ^{ctx.author.name}#{ctx.author.discriminator} ^{ctx.author.id}")
        await ctx.send(f"Sent a PM to /u/{username}, send the verification code (the six numbers sent by the bot) "
                       f"to *this channel* to verify your account.")
        self.bot.verification_queue[username] = {"username" : username, "author" : ctx.author,
                                                 "code" : verification_code}
        self.bot.logger.info(f"Added user /u/{username} to verification queue")

    @commands.command()
    async def modqueue(self, ctx, subreddit: str = "", channel: discord.TextChannel = None):
        self.bot.logger.info(f"Changing modqueue channel for {ctx.guild.name} {ctx.guild.id}")
        channel = channel or ctx.channel
        subreddit = await self.checks.get_subreddit(ctx, subreddit)
        username = await self.checks.get_username(ctx)
        if (subreddit or username) is None:
            return
        self.bot.logger.info(f"Subreddit /r/{subreddit}")
        self.bot.logger.info(f"Requester /u/{username}")
        redditor = self.bot.reddit.redditor(username)
        if not await self.checks.user_is_mod(ctx, redditor, subreddit):
            return
        await ctx.send("Changing modqueue channel...")
        self.bot.channel_config[subreddit]['modqueue'] = channel.id
        await channel.send("Modqueue channel successfully set to this channel.")

    @commands.command()
    async def modmail(self, ctx, subreddit: str = "", channel: discord.TextChannel = None):
        self.bot.logger.info(f"Changing modmail channel for {ctx.guild.name} {ctx.guild.id}")
        channel = channel or ctx.channel
        subreddit = await self.checks.get_subreddit(ctx, subreddit)
        username = await self.checks.get_username(ctx)
        self.bot.logger.info(f"Subreddit /r/{subreddit}")
        self.bot.logger.info(f"Requester /u/{username}")
        redditor = self.bot.reddit.redditor(username)
        if not await self.checks.user_is_mod(ctx, redditor, subreddit):
            return
        await ctx.send("Changing modmail channel...")
        self.bot.channel_config[subreddit]['modmail'] = channel.id
        await channel.send("Modmail channel successfully set to this channel.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        verified = False
        for i in self.bot.verification_queue.values():
            if i["author"].id == message.author.id and message.content.lower() == i["code"]:
                username = i['username']
                if self.bot.verification_queue[username].get('subreddit'):
                    if self.bot.verification_queue[username]['subreddit'] \
                            not in self.bot.channel_config:
                        self.setup_guild(message.author, username)
                        verified = True
                    else:
                        await message.channel.send("The subreddit requested is already verified!")
                    break
                else:
                    self.setup_verified_user(message.author, username)
                    verified = True
                    break
        if verified:
            await message.delete()
            del self.bot.verification_queue[username.lower()]
            await message.channel.send(f"Your verification request has been confirmed and accepted!")

    def setup_guild(self, author, username):
        modqueue_channel = self.bot.verification_queue[username]['modqueue']
        modmail_channel = self.bot.verification_queue[username]['modmail']
        self.bot.channel_config[self.bot.verification_queue[username]['subreddit']] = \
            {'modqueue' : modqueue_channel.id,
             'modmail' : modmail_channel.id,
             'guild' : self.bot.verification_queue[username]['channel'].guild.id}
        if not username.lower() in self.bot.verified_users:
            self.setup_verified_user(author, username)
        self.bot.logger.info(f"Verified subreddit /r/"
                             f"{self.bot.verification_queue[username.lower()]['subreddit']}")

    def setup_verified_user(self, author, username):
        self.bot.verified_users[str(author.id)] = username.lower()


def setup(bot):
    bot.add_cog(Registration(bot))
