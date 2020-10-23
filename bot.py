import praw
import discord
import json
import atexit

from discord.ext import commands
from utils.auth import Auth
from utils.logger import set_logger
from utils.cache import Cache
from utils.queue import Queue


class ModqueueStreamer(commands.Bot):
    def __init__(self, command_prefix: str, intents: discord.Intents, **kwargs):
        super().__init__(command_prefix=command_prefix, intents=intents, **kwargs)
        self.logger = set_logger()
        self.verification_queue = dict()
        self.event_queue = Queue()
        self.obj_cache = Cache()
        self.default_invite = \
            "https://discord.com/api/oauth2/authorize?client_id=767842408758771742&permissions=51200&scope=bot"
        self.reddit = self.create_reddit_connection()
        self.load_data()

    def setup(self):
        self.logger.info("Called `setup` method")
        for ext in ['cogs.modqueue_stream', 'cogs.registration', 'cogs.inbox_stream', 'cogs.modmail_stream',
                    'cogs.object_stream', 'cogs.admin']:
            self.load_extension(ext)
        self.logger.info('Successfully loaded all cogs')

    def create_reddit_connection(self):
        if hasattr(self, 'reddit'):
            del self.reddit
        reddit = praw.Reddit(
            client_id=Auth.REDDIT_CLIENT_ID,
            client_secret=Auth.REDDIT_CLIENT_SECRET,
            user_agent="modqueue streaming bot v0.3, /u/Kirby_Stomp",
            username="modqueuestreamer",
            password=Auth.REDDIT_PASSWORD
        )
        self.obj_cache.update_reddit(reddit)
        self.logger.info("Succesfully logged into reddit as `u/modqueuestreamer`")
        return reddit

    def dump_data(self):
        self.logger.info("Dumping bot data")
        with open('./data/channel_config.json', 'w') as fp:
            json.dump(self.channel_config, fp)
        with open('./data/backups/channel_config.json', 'w') as fp:
            json.dump(self.channel_config, fp)
        with open('./data/verified_users.json', 'w') as fp:
            json.dump(self.verified_users, fp)
        with open('./data/backups/verified_users.json', 'w') as fp:
            json.dump(self.verified_users, fp)
        self.logger.info("Finished dumping bot data")

    def load_data(self):
        with open('./data/channel_config.json', 'r') as fp:
            self.channel_config = json.load(fp)
        with open('./data/verified_users.json', 'r') as fp:
            self.verified_users = json.load(fp)
        self.logger.info('Successfully loaded json data files')

    def close_bot(self):
        self.dump_data()


if __name__ == '__main__':
    bot = ModqueueStreamer(command_prefix="r!", intents=discord.Intents(
        messages=True, members=True, guilds=True, reactions=True))
    try:
        bot.setup()
        atexit.register(bot.close_bot)
        bot.run(Auth.DISCORD_TOKEN)
    finally:
        bot.close_bot()
