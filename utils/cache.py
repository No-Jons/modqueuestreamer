import praw

from utils.formatter import format_msg
from utils.queue import Queue


class Cache(Queue):
    def __init__(self, limit: int = 10000):
        super().__init__(limit=limit)
        self._reddit = None
        self.items_updated = 0

    async def update(self, obj, message):
        if isinstance(obj, praw.reddit.models.Submission):
            updated_obj = self._reddit.submission(id=obj.id)
        else:
            updated_obj = self._reddit.comment(id=obj.id)
        embed = format_msg(updated_obj, approved=updated_obj.approved, removed=updated_obj.removed)
        await message.edit(embed=embed)
        obj = self.queue.pop(0)
        if not (updated_obj.approved or updated_obj.removed):
            self.add(obj)
        self.items_updated += 1

    def purge(self, limit: int = 100):
        if len(self) <= 10:
            return
        if limit > len(self):
            limit = len(self) - 2
        self.queue = self.queue[int(limit//2):-(int(limit//2))]

    def update_reddit(self, reddit):
        self._reddit = reddit
