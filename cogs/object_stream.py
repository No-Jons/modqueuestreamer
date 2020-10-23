import discord

from discord.ext import commands, tasks
from utils.self_deleting_message import SelfDeletingMessage
from utils.checks import Checks


class ObjStream(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.approve = "<:approve:769073700465016872>"
        self.remove = "<:remove:769073700452171776>"
        self.checks = Checks(self.bot)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.logger.info("Started streaming objects")
        try:
            self.read_queue.start()
            self.update_cache.start()
            self.dump_bot_data.start()
            self.refresh_reddit_connection.start()
        except RuntimeError:
            pass

    @tasks.loop(seconds=10.0)
    async def read_queue(self):
        for obj in self.bot.event_queue.queue:
            try:
                message = await obj["channel"].send(embed=obj["embed"])
                await message.add_reaction(self.approve)
                await message.add_reaction(self.remove)
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
            self.bot.logger.info("Cannot perform action on message item, not found in cache")
            return
        redditor_invoked = self.bot.reddit.redditor(self.bot.verified_users[str(payload.user_id)])
        if not self.checks.user_is_mod_silent(redditor_invoked, obj.subreddit.display_name):
            return
        if str(payload.emoji) == self.approve:
            obj.mod.approve()
            await SelfDeletingMessage(self.bot, content=f"Modqueue item {obj.id} approved!").send_and_delete_after(channel)
            self.bot.logger.info(f"Approved post {obj.id}")
            return
        elif str(payload.emoji) == self.remove:
            removal_reasons = obj.subreddit.mod.removal_reasons
            try:
                removal_reasons[0]
            except IndexError:
                removal_reasons = None
            if removal_reasons is not None:  # If there are any removal reasons
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
                if selection.lower() == 'cancel':
                    return
                elif selection.lower() == 'none':
                    obj.mod.remove()
                    await SelfDeletingMessage(self.bot, content=f"Modqueue item {obj.id} removed!"
                                              ).send_and_delete_after(channel)
                    self.bot.logger.info(f"Removed item {obj.id}")
                    return
                removal_reason = removal_reasons[selection - 1]
            else:
                obj.mod.remove()
                await SelfDeletingMessage(self.bot, content=f"Modqueue item {obj.id} removed!").send_and_delete_after(
                    channel)
                self.bot.logger.info(f"Removed item {obj.id}")
                return
            obj.mod.remove(reason_id=removal_reason.id)
            if removal_reasons and removal_reason.message:
                obj.mod.send_removal_message(
                    type='public',
                    message=f"Hello, /u/{obj.author}!\n"
                            f"Unfortunately, your post has been removed for the following reason(s):\n"
                            f"##**{removal_reason.title}**:\n"
                            f"{removal_reason.message}\n\n"
                            f"If you feel this removal was in error, feel free to "
                            f"[contact the mods](https://www.reddit.com/message/compose/?to=%2Fr%2F{obj.subreddit})."
                )
            await SelfDeletingMessage(self.bot, content=f"Modqueue item {obj.id} removed!").send_and_delete_after(channel)
            self.bot.logger.info(f"Removed item {obj.id}")
            return

    @tasks.loop(minutes=30.0)
    async def dump_bot_data(self):
        self.bot.dump_data()

    @tasks.loop(minutes=30.0)
    async def refresh_reddit_connection(self):
        self.bot.reddit = self.bot.create_reddit_connection()


def setup(bot):
    bot.add_cog(ObjStream(bot))
