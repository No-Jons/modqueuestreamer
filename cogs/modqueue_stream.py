import discord

from discord.ext import commands
from utils.process_handler import StreamHandler
from utils.formatter import format_msg


class ModqueueStreamHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        StreamHandler(target=self.modqueue).start()

    def modqueue(self):
        for obj in self.bot.reddit.subreddit("mod").mod.stream.modqueue(skip_existing=True):
            embed = format_msg(obj, "Modqueue")
            if obj.subreddit.display_name.lower() in self.bot.channel_config:
                channel = self.bot.get_channel(
                    int(self.bot.channel_config[obj.subreddit.display_name.lower()]['modqueue'])
                )
                self.bot.event_queue.append({"embed" : embed, "channel" : channel})
                # todo: cache?
            else:
                self.bot.logger.info(f"Subreddit {obj.subreddit} has not set logging channel, skipped log")


def setup(bot):
    bot.add_cog(ModqueueStreamHandler(bot))
