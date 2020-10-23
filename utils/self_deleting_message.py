import discord
import asyncio


from utils.etc import is_int


class SelfDeletingMessage:
    def __init__(self, bot, content: str = "", embed: discord.Embed = None, emojis: list = None, limit: int = None,
                 exceptions: list = []):
        if not (content or embed):
            raise ValueError("Either content or embed is required")
        self.bot = bot
        self.content = content
        self.embed = embed
        self.emojis = emojis
        self.limit = limit
        self.exceptions = exceptions

    async def send_and_wait_for_reaction(self, channel: discord.TextChannel, author: discord.Member):
        message = await channel.send(content=self.content, embed=self.embed)
        try:
            r, u = await self.bot.wait_for('reaction_add',
                                           check=lambda r, u: ((r.emoji in self.emojis) if self.emojis else True)
                                                                and u.id == author.id,
                                           timeout=60)
        except asyncio.TimeoutError:
            await message.delete()
            return
        await message.delete()
        return r.emoji

    async def send_and_wait_for_message(self, channel: discord.TextChannel, author: discord.Member):
        message = await channel.send(content=self.content, embed=self.embed)
        try:
            m = await self.bot.wait_for('message',
                                        check=lambda m: m.author.id == author.id and (is_int(m.content) <= self.limit or
                                                                                      m.content.lower() in self.exceptions),
                                        timeout=60)
        except asyncio.TimeoutError:
            await message.delete()
            return
        await message.delete()
        await m.delete()
        return is_int(m.content) or m.content

    async def send_and_delete_after(self, channel: discord.TextChannel, seconds: float = 10.0):
        message = await channel.send(content=self.content, embed=self.embed)
        await asyncio.sleep(seconds)
        await message.delete()
