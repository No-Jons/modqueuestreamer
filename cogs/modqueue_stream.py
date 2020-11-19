import discord

from discord.ext import commands
from prawcore.exceptions import PrawcoreException
from utils.process_handler import StreamHandler
from utils.formatter import format_msg


class ModqueueStreamHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        StreamHandler(target=self.modqueue).start()

    def modqueue(self):
        while self.bot.running:
            try:
                self.bot.logger.info("Started modqueue stream")
                for obj in self.bot.reddit.subreddit("mod").mod.stream.modqueue(skip_existing=True):
                    embed = format_msg(obj)
                    if obj.subreddit.display_name.lower() in self.bot.channel_config:
                        channel = self.bot.get_channel(
                            int(self.bot.channel_config[obj.subreddit.display_name.lower()]['modqueue'])
                        )
                        self.bot.event_queue.add({"embed" : embed, "channel" : channel, "obj" : obj})
                    else:
                        self.bot.logger.info(f"Subreddit {obj.subreddit} has not set logging channel, skipped log")
            except PrawcoreException:
                self.bot.logger.error("Modqueue stream closed, reloading...")


def setup(bot):
    bot.add_cog(ModqueueStreamHandler(bot))
