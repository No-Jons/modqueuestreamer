import discord
import praw

from discord.ext import commands, tasks
from utils.self_deleting_message import SelfDeletingMessage
from utils.moderation import Moderation
from utils.checks import Checks


class ObjStream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.approve = "<:approve:769073700465016872>"
        self.remove = "<:remove:769073700452171776>"
        self.ignore_reports = "🔇"
        self.mod = Moderation(self.bot)
        self.checks = Checks(self.bot)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("Started streaming objects")
        try:
            self.read_queue.start()
            self.update_cache.start()
            self.dump_bot_data.start()
        except RuntimeError:
            pass

    @tasks.loop(seconds=10.0)
    async def read_queue(self):
        for obj in self.bot.event_queue.queue:
            try:
                message = await obj["channel"].send(embed=obj["embed"])
                await message.add_reaction(self.approve)
                await message.add_reaction(self.remove)
                await message.add_reaction(self.ignore_reports)
                self.bot.event_queue.remove(obj)
                self.bot.obj_cache.add({"obj" : obj["obj"], "message" : message})
            except discord.Forbidden:
                self.bot.logger.error("Invalid permissions, not able to send messages...")
        self.bot.logger.debug("Executed task read_queue")

    @tasks.loop(minutes=10.0)
    async def update_cache(self):
        for obj in self.bot.obj_cache.queue:
            try:
                await self.bot.obj_cache.update(obj["obj"], obj["message"])
            except discord.HTTPException:
                self.bot.logger.error(f"Could not update message {obj['message'].id}")
        self.bot.logger.info("Executed task update_cache")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == 767842408758771742 or not self.bot.verified_users.get(str(payload.user_id)):
            return
        for item in self.bot.obj_cache.queue:
            if payload.message_id == item["message"].id:
                channel = item["message"].channel
                obj = item["obj"]
                break
        else:
            return
        redditor_invoked = self.bot.reddit.redditor(self.bot.verified_users[str(payload.user_id)])
        if not self.checks.user_is_mod_silent(redditor_invoked, obj.subreddit.display_name):
            return
        if str(payload.emoji) == self.ignore_reports:
            await self.mod.ignore_reports(obj, channel)
            return
        elif str(payload.emoji) == self.approve:
            await self.mod.approve(obj, channel)
            return
        elif str(payload.emoji) == self.remove:
            selection = None
            removal_reasons = self.mod.get_removal_reasons(obj.subreddit)
            if removal_reasons is not None and isinstance(obj, praw.reddit.models.Submission):
                # If there are any removal reasons and is not a comment
                embed = discord.Embed(title="Removal reasons:", color=discord.Color.red())
                idx = 1
                for i in removal_reasons:
                    embed.add_field(name=str(idx), value=i.title)
                    idx += 1
                embed.set_footer(
                    text="To select a removal reason, send another message "
                         "containing the # of the reason you want to select.\n\"none\" = no reason for removal\n"
                         "\"cancel\" = cancel action"
                )
                reaction_user = self.bot.get_user(payload.user_id)
                selection = await SelfDeletingMessage(self.bot, embed=embed, limit=idx,
                                                      exceptions=["none", "cancel"]).send_and_wait_for_message(
                    channel, reaction_user
                )
            if str(selection).lower() == "none":
                await self.mod.remove(obj, channel)
                return
            removal_reason = removal_reasons[selection - 1]
            await self.mod.remove(obj, channel, removal_reason)
            return

    @tasks.loop(minutes=30.0)
    async def dump_bot_data(self):
        self.bot.dump_data()


def setup(bot):
    bot.add_cog(ObjStream(bot))
