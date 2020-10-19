import discord
import praw

from discord.ext import commands
from utils.etc import create_code


class Registration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['verify', 'verify_sr'])
    async def register(self, ctx, subreddit: str, username: str = None,
                       modqueue_channel: discord.TextChannel = None, modmail_channel: discord.TextChannel = None):
        self.bot.logger.info(f"Starting verification process on subreddit /r/{subreddit} "
                             f"invoked by {ctx.author.name}#{ctx.author.discriminator} {ctx.author.id} /u/{username}")
        modqueue_channel = modqueue_channel or ctx.channel
        modmail_channel = modmail_channel or modqueue_channel
        if username is None:
            for i in self.bot.verified_users.keys():
                if i == str(ctx.author.id):
                    username = self.bot.verified_users[i]
            if username is None:
                await ctx.send("You are not a verified user yet! Fix that by using the `r!verify_me` command!")
                self.bot.logger.info("Verification failed: unverified user")
                return
        try:
            to_msg = self.bot.reddit.redditor(username)
        except praw.reddit.RedditAPIException as e:
            await ctx.send(f"No user found with username /u/{username}")
            self.bot.logger.info(f"Verification failed, invalid user: {e}")
            return
        if subreddit.lower() not in [i.display_name.lower() for i in to_msg.moderated()]:
            await ctx.send("You can't register this bot on a subreddit that you don't mod!")
            self.bot.logger.info("Verification failed: invalid user")
            return
        if subreddit.lower() in self.bot.channel_config:
            await ctx.send("Your subreddit is already verified!")
            return
        verification_code = create_code()
        to_msg.message(subject=f"Verification for /r/{subreddit} setup",
                       message=f"Hello! "
                       f"If you did not expect to receive this message, please ignore it. "
                       f"Your verification code is {verification_code}."
                       f"\n^Requested ^by ^{ctx.author.name}#{ctx.author.discriminator} ^{ctx.author.id}")
        await ctx.send(f"Sent a PM to /u/{username}, reply to the message to verify /r/{subreddit}")
        self.bot.verification_queue[username] = {'subreddit' : subreddit, 'channel' : ctx.channel,
                                                 'modqueue' : modqueue_channel, 'modmail' : modmail_channel,
                                                 'username' : username, 'author' : ctx.author,
                                                 "code" : verification_code}
        self.bot.logger.info(f"Added user /u/{username} and subreddit /r/{subreddit} to verification queue")

    @commands.command(aliases=['verify_me'])
    async def register_me(self, ctx, username: str):
        self.bot.logger.info(f"Starting verification for /u/{username}")
        try:
            to_msg = self.bot.reddit.redditor(username)
        except praw.reddit.RedditAPIException as e:
            await ctx.send(f"No user found with username /u/{username}")
            self.bot.logger.info(f"Verification failed, invalid user: {e}")
            return
        if username.lower() in self.bot.verified_users.values():
            await ctx.send(f"You're already verified as /u/{username}")
            self.bot.logger.info("Verification failed: user already verified")
            return
        verification_code = create_code()
        to_msg.message(subject=f"Verification for /u/{username}",
                       message=f"Hello! "
                       f"If you did not expect to receive this message, please ignore it. "
                       f"Your verification code is {verification_code}."
                       f"\n^Requested ^by ^{ctx.author.name}#{ctx.author.discriminator} ^{ctx.author.id}")
        self.bot.verification_queue[username] = {'username' : username, 'author' : ctx.author,
                                                 "code" : verification_code}
        self.bot.logger.info(f"Added user /u/{username} to verification queue")

    @commands.command()
    async def modqueue(self, ctx, subreddit: str = "", channel: discord.TextChannel = None):
        self.bot.logger.info(f"Changing modqueue channel for {ctx.guild.name} {ctx.guild.id}")
        channel = channel or ctx.channel
        subs_in_guild = 0
        subs = str()
        # todo: multi-page subreddit choice for multi-sub guilds?
        for item in self.bot.channel_config.keys():
            if self.bot.channel_config[item]["guild"] == ctx.guild.id:
                if item == subreddit.lower():
                    subs_in_guild = 1
                    break
                subs_in_guild += 1
                subs += "/r/" + item + "\n"
        if subs_in_guild == 0:
            await ctx.send("Your subreddit has not been verified yet! Fix that by using the `r!register` command!")
            self.bot.logger.info("Verification failed: no subreddit provided")
            return
        if subs_in_guild > 1:
            await ctx.send(f"Please specify one of:\n```\n{subs}\n```")
            return
        self.bot.logger.info(f"Subreddit /r/{subreddit}")
        username = None
        for i in self.bot.verified_users.keys():
            if i == str(ctx.author.id):
                username = self.bot.verified_users[i]
        if username is None:
            await ctx.send("You are not a verified user yet! Fix that by using the `r!register_me` command!")
            self.bot.logger.info("Verification failed: unverified user")
            return
        self.bot.logger.info(f"Requester /u/{username}")
        try:
            redditor = self.bot.reddit.redditor(username)
        except praw.reddit.RedditAPIException as e:
            await ctx.send(f"No user found with username /u/{username}")
            self.bot.logger.info(f"Verification failed, invalid user: {e}")
            return
        try:
            if subreddit.lower() not in [i.display_name.lower() for i in redditor.moderated()]:
                await ctx.send("You can't register this bot on a subreddit that you don't mod!")
                self.bot.logger.info("Verification failed: invalid user")
                return
        except praw.reddit.RedditAPIException as e:
            await ctx.send(f"Encountered error when verifying, are you sure /u/{username} exists?")
            self.bot.logger.info(f"Verification failed: invalid user: {e}")
            return
        await ctx.send("Changing modqueue channel...")
        self.bot.channel_config[subreddit]['modqueue'] = channel.id
        await channel.send("Modqueue channel successfully set to this channel.")

    @commands.command()
    async def modmail(self, ctx, subreddit: str = "", channel: discord.TextChannel = None):
        self.bot.logger.info(f"Changing modmail channel for {ctx.guild.name} {ctx.guild.id}")
        channel = channel or ctx.channel
        subs_in_guild = 0
        subs = str()
        # todo: multi-page subreddit choice for multi-sub guilds?
        for item in self.bot.channel_config.keys():
            if self.bot.channel_config[item]["guild"] == ctx.guild.id:
                if item == subreddit.lower():
                    subs_in_guild = 1
                    break
                subs_in_guild += 1
                subs += "/r/" + item + "\n"
        if subs_in_guild == 0:
            await ctx.send("Your subreddit has not been verified yet! Fix that by using the `r!register` command!")
            self.bot.logger.info("Verification failed: no subreddit provided")
            return
        if subs_in_guild > 1:
            await ctx.send(f"Please specify one of:\n```\n{subs}\n```")
            return
        self.bot.logger.info(f"Subreddit /r/{subreddit}")
        username = None
        for i in self.bot.verified_users.keys():
            if i == str(ctx.author.id):
                username = self.bot.verified_users[i]
        if username is None:
            await ctx.send("You are not a verified user yet! Fix that by using the `r!register_me` command!")
            self.bot.logger.info("Verification failed: unverified user")
            return
        self.bot.logger.info(f"Requester /u/{username}")
        try:
            redditor = self.bot.reddit.redditor(username)
        except praw.reddit.RedditAPIException as e:
            await ctx.send(f"No user found with username /u/{username}")
            self.bot.logger.info(f"Verification failed, invalid user: {e}")
            return
        try:
            if subreddit.lower() not in [i.display_name.lower() for i in redditor.moderated()]:
                await ctx.send("You can't register this bot on a subreddit that you don't mod!")
                self.bot.logger.info("Verification failed: invalid user")
                return
        except praw.reddit.RedditAPIException:
            await ctx.send(f"Encountered error when verifying, are you sure /u/{username} exists?")
            self.bot.logger.info("Verification failed: invalid user")
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
