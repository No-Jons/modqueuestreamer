import praw
import discord

from datetime import datetime


def format_msg(obj, obj_from):
    header = f"{obj_from} item {obj}"
    if isinstance(obj, praw.reddit.models.Submission):
        obj_type = "Submission"
    else:  # type can be inferred to be a comment
        obj_type = "Comment"
    embed = discord.Embed(title=header, description=obj_type, url=obj.url, color=discord.Color.orange())
    author_name = str(obj.author) if obj.author else "[deleted]"
    embed.add_field(name="Author", value=f"[u/{author_name}](https://www.reddit.com/user/{author_name})")
    if obj.user_reports:
        reports = str()
        for i in obj.user_reports:
            reports += f"{i[1]}: {i[0]}\n"
        embed.add_field(name="User Reports:", value=reports)
    if obj.mod_reports:
        reports = str()
        for i in obj.mod_reports:
            reports += f"{i[1]}: {i[0]}\n"
        embed.add_field(name="Mod Reports:", value=reports)
    embed.set_footer(text=f"/r/{obj.subreddit} - {obj.fullname}")
    embed.timestamp = datetime.fromtimestamp(obj.created_utc)
    return embed


def format_modmail_msg(obj):
    header = f"New Modmail from {obj.authors[0]}"
    embed = discord.Embed(title=header, description="Modmail", url=f"https://mod.reddit.com/mail/all/{obj.id}",
                          color=discord.Color.green())
    embed.add_field(name="Author:", value=obj.authors[0])
    embed.add_field(name="Subject:", value=obj.subject)
    embed.set_footer(text=f"/r/{obj.owner} - {obj.last_updated}")
    return embed
