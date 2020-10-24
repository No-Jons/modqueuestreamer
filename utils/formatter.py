import praw
import discord

from datetime import datetime


def format_msg(obj, approved=False, removed=False):
    if approved:
        color = discord.Color.green()
        prefix = "Approved -"
        footer_suffix = f"- Approved by /u/{obj.approved_by}"
    elif removed:
        color = discord.Color.red()
        prefix = "Removed -"
        footer_suffix = f"- Removed for {obj.removal_reason or 'no reason provided'}"
    else:
        color = discord.Color.orange()
        prefix = ""
        footer_suffix = ""
    if isinstance(obj, praw.reddit.models.Submission):
        obj_type = "Submission"
        url = obj.url
    else:  # type can be inferred to be a comment
        obj_type = "Comment"
        url = f"https://www.reddit.com/{obj.permalink}"
    embed = discord.Embed(title=f"{prefix} Modqueue item {obj}",
                          description=obj_type,
                          url=url,
                          color=color)
    author_name = str(obj.author) if obj.author else "[deleted]"
    embed.add_field(name="Author", value=f"[u/{author_name}](https://www.reddit.com/user/{author_name})")
    if obj.user_reports:
        user_reports = obj.user_reports
        if len(user_reports) >= 5:
            user_reports = obj.user_reports[:5]
        embed.add_field(name=f"User Reports ({len(obj.user_reports)}):",
                        value="".join([f"{i[1]}: {i[0]}\n" if len(i[0]) <= 80 else f"{i[1]}: {i[0][:80]}..."
                                       for i in user_reports]))
    if obj.mod_reports:
        mod_reports = obj.mod_reports
        if len(mod_reports) >= 5:
            mod_reports = obj.mod_reports[:5]
        embed.add_field(name=f"Mod Reports ({len(obj.mod_reports)}):",
                        value="".join([f"{i[1]}: {i[0]}\n" if len(i[0]) <= 80 else f"{i[1]}: {i[0][:80]}..."
                                       for i in mod_reports]))
    embed.set_footer(text=f"/r/{obj.subreddit} - {obj.fullname} {footer_suffix}")
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
