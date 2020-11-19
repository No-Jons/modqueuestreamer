import discord

from discord.ext import commands
from prawcore.exceptions import PrawcoreException
from utils.process_handler import StreamHandler
from utils.formatter import format_modmail_msg


class ModmailStreamHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        StreamHandler(target=self.modmail).start()

    def modmail(self):
        while self.bot.running:
            try:
                self.bot.logger.info("Started modmail stream")
                for obj in self.bot.reddit.subreddit("mod").mod.stream.modmail_conversations(skip_existing=True):
                    embed = format_modmail_msg(obj)
                    if str(obj.owner).lower() in self.bot.channel_config:
                        channel = self.bot.get_channel(int(self.bot.channel_config[str(obj.owner).lower()]['modmail']))
                        self.bot.event_queue.add({"embed" : embed, "channel" : channel})
                    else:
                        self.bot.logger.info(f"Subreddit {obj.owner} has not set logging channel, skipped log")
            except PrawcoreException:
                self.bot.logger.error("Modmail stream closed, reloading...")


def setup(bot):
    bot.add_cog(ModmailStreamHandler(bot))
