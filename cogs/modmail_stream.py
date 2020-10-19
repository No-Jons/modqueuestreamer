import discord

from discord.ext import commands
from utils.process_handler import StreamHandler
from utils.formatter import format_modmail_msg


class ModmailStreamHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        StreamHandler(target=self.modmail).start()

    def modmail(self):
        for obj in self.bot.reddit.subreddit("mod").mod.stream.modmail_conversations(skip_existing=True):
            embed = format_modmail_msg(obj)
            if str(obj.owner) in self.bot.channel_config:
                channel = self.bot.get_channel(int(self.bot.channel_config[str(obj.owner)]['modmail']))
                self.bot.event_queue.append({"embed" : embed, "channel" : channel})
                # todo: cache
            else:
                self.bot.logger.info(f"Subreddit {obj.owner} has not set logging channel, skipped log")


def setup(bot):
    bot.add_cog(ModmailStreamHandler(bot))