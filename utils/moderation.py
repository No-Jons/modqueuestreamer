from utils.self_deleting_message import SelfDeletingMessage


class Moderation:
    def __init__(self, bot):
        self.bot = bot

    async def ignore_reports(self, obj, channel):
        obj.mod.ignore_reports()
        self.bot.logger.info(f"Ignored reports on item {obj.id}: /r/{obj.subreddit.display_name}")
        await SelfDeletingMessage(self.bot, content=f'Ignored reports on modqueue item {obj.id}!').send_and_delete_after(channel)

    async def approve(self, obj, channel):
        obj.mod.approve()
        self.bot.logger.info(f"Approved item {obj.id}: /r/{obj.subreddit.display_name}")
        await SelfDeletingMessage(self.bot, content=f"Modqueue item {obj.id} approved!").send_and_delete_after(channel)

    async def remove(self, obj, channel, reason=None):
        if reason is None:
            obj.mod.remove()
        else:
            obj.mod.remove(reason_id=reason.id)
            if reason.message:
                obj.mod.send_removal_message(
                    type='public',
                    message=f"Hello, /u/{obj.author}!\n"
                            f"Unfortunately, your post has been removed for the following reason(s):\n---\n"
                            f"##**{reason.title}**:\n"
                            f"    {reason.message}\n---\n"
                            f"If you feel this removal was in error, feel free to "
                            f"[contact the mods](https://www.reddit.com/message/compose/?to=%2Fr%2F{obj.subreddit})."
                )
        self.bot.logger.info(f"Removed item {obj.id}: /r/{obj.subreddit}")
        await SelfDeletingMessage(self.bot, content=f"Modqueue item {obj.id} removed!").send_and_delete_after(channel)

    @staticmethod
    def get_removal_reasons(subreddit):
        removal_reasons = subreddit.mod.removal_reasons  # hacky af solution
        try:
            removal_reasons[0]
        except IndexError:
            return
        return removal_reasons
