import discord
import praw
import re
import json

from discord.ext import commands
from utils.process_handler import StreamHandler


class InboxStreamHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        StreamHandler(target=self.accept_mod_invites).start()

    def accept_mod_invites(self):
        for message in self.bot.reddit.inbox.stream(skip_existing=True):
            is_mod_invite = re.search(r"\*\*you are invited to become a moderator\*\*", message.body.lower())
            if is_mod_invite:
                subreddit = self.bot.reddit.subreddit(str(message.subreddit))
                self.bot.logger.info(f"Invitation to moderate {subreddit.display_name} received")
                try:
                    subreddit.mod.accept_invite()
                    self.bot.logger.info(f"Accepted invite to moderate {subreddit.display_name}")
                    subreddit.message(subject="Discord invite",
                                      message=f"Hello! Thanks for inviting me to your subreddit. Invite me to your "
                                              f"discord server of choice [here]({self.bot.default_invite})! Make sure "
                                              f"you have \"manage_server\" perms on the server you want to add me to. "
                                              f"After you invite me, be sure to run the `r!register` command!")
                except praw.reddit.RedditAPIException as e:
                    self.bot.logger.error(f"Failed to accept moderator invite to {subreddit.display_name}: "
                                          f"{e}")
                    subreddit.message(subject="Failed to accept moderator invite",
                                      message="Whoops! I seem to have encountered an error while trying to accept "
                                              "the moderator invite you sent my way! If this error has occoured "
                                              "multiple times, feel free to contact my owner, /u/Kirby_Stomp, about "
                                              "this incident.")


def setup(bot):
    bot.add_cog(InboxStreamHandler(bot))
