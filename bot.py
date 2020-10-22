import praw
import discord
import json
import atexit

from discord.ext import commands
from utils.auth import Auth
from utils.logger import set_logger
from utils.cache import Cache
from utils.queue import Queue

bot = commands.Bot(command_prefix="r!", intents=discord.Intents.default())  # update custom bot class for this


def create_reddit_connection():
    if hasattr(bot, 'reddit'):
        del bot.reddit
    reddit = praw.Reddit(
        client_id=Auth.REDDIT_CLIENT_ID,
        client_secret=Auth.REDDIT_CLIENT_SECRET,
        user_agent="modqueue streaming bot v0.3, /u/Kirby_Stomp",
        username="modqueuestreamer",
        password=Auth.REDDIT_PASSWORD
    )
    bot.obj_cache.update_reddit(reddit)
    bot.logger.info("Succesfully logged into reddit as `u/modqueuestreamer`")
    return reddit


def setup():
    bot.logger = set_logger()
    bot.logger.info("Called `setup` method")

    bot.cached_items = set()
    bot.verification_queue = dict()
    bot.event_queue = Queue()
    bot.obj_cache = Cache()
    bot.dump_data = dump_data
    bot.create_reddit_connection = create_reddit_connection
    bot.default_invite = \
        "https://discord.com/api/oauth2/authorize?client_id=767842408758771742&permissions=51200&scope=bot"

    bot.reddit = create_reddit_connection()

    with open('./data/channel_config.json', 'r') as fp:
        bot.channel_config = json.load(fp)

    with open('./data/verified_users.json', 'r') as fp:
        bot.verified_users = json.load(fp)

    bot.logger.info('Successfully loaded json data files')

    for ext in ['cogs.modqueue_stream', 'cogs.registration', 'cogs.inbox_stream', 'cogs.modmail_stream',
                'cogs.object_stream', 'cogs.admin']:
        bot.load_extension(ext)

    bot.logger.info('Successfully loaded all cogs')

    atexit.register(close_bot)

    bot.logger.info('Successfully registered atexit function')


@bot.command()
async def test(ctx):
    await ctx.send("I'm alive!")


def dump_data():
    bot.logger.info("Dumping bot data")
    with open('./data/channel_config.json', 'w') as fp:
        json.dump(bot.channel_config, fp)
    with open('./data/verified_users.json', 'w') as fp:
        json.dump(bot.verified_users, fp)
    bot.logger.info("Finished dumping bot data")


def close_bot():
    bot.dump_data()


if __name__ == '__main__':
    try:
        setup()
        bot.run(Auth.DISCORD_TOKEN)
    finally:
        close_bot()
