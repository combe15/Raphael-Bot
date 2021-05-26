import logging

import dataset
import discord
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context, Greedy

import constants
from tools import embeds, database
from tools.record import record_usage

log = logging.getLogger(__name__)


class ModerationCog(Cog):
    """Moderation Cog"""

    def __init__(self, bot):
        self.bot = bot

    async def can_action_user(self, ctx: Context, member: discord.Member) -> bool:
        """Stop mods from doing stupid things."""
        # Stop mods from actioning on the bot.
        if member.id == self.bot.user.id:
            await ctx.reply("You cannot action that user.")
            return False

        # Stop mods from actioning one another, people higher ranked than them or themselves.
        if member.top_role >= ctx.author.top_role:
            await ctx.reply("You cannot action that user.")
            return False

        # Checking if Bot is able to even perform the action
        if member.top_role >= member.guild.me.top_role:
            await ctx.reply(
                "Bot is inferior or equal to that member, thus does not have permission to take action."
            )
            return False

        # Otherwise, the action is probably valid, return true.
        return True

    @commands.has_role("Staff")
    @commands.bot_has_permissions(
        ban_members=True, send_messages=True, embed_links=True
    )
    @commands.before_invoke(record_usage)
    @commands.command(name="ban")
    async def ban_member(self, ctx: Context, member: discord.Member, *, reason: str):
        """Bans member from guild."""

        # Checks if invoker can action that member (self, bot, etc.)
        if not await self.can_action_user(ctx, member):
            return

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Banning member: {member.name}",
            image_url=constants.Icons.user_ban,
            color=constants.Colours.soft_red,
        )
        embed.description = (
            f"{member.mention} was banned by {ctx.author.mention} for:\n{reason}"
        )

        # Info: https://discordpy.readthedocs.io/en/stable/api.html#discord.Guild.ban
        await ctx.guild.ban(user=member, reason=reason, delete_message_days=0)

        # Send user message telling them that they were banned and why.
        try:  # Incase user has DM's Blocked.
            channel = await member.create_dm()
            message = f"You were banned from {ctx.guild} for: {reason}"
            await channel.send(message)
        except:
            embed.add_field(
                name="NOTICE", value="Unable to message member about this action."
            )

        # Add the ban to the mod_log database.
        with dataset.connect(database.get_db()) as db:
            db["mod_logs"].insert(
                dict(
                    user_id=member.id,
                    mod_id=ctx.author.id,
                    timestamp=ctx.message.created_at,
                    reason=reason,
                    type="ban",
                )
            )

        await ctx.reply(embed=embed)

    @commands.has_role("Staff")
    @commands.bot_has_permissions(
        ban_members=True, send_messages=True, embed_links=True
    )
    @commands.before_invoke(record_usage)
    @commands.command(name="unban")
    async def unban_member(self, ctx: Context, user: discord.User, *, reason: str):
        """Unbans user from guild."""

        # Checks if invoker can action that user (self, bot, etc.)
        if not await self.can_action_user(ctx, user):
            return

        embed = embeds.make_embed(
            context=ctx,
            title=f"Unbanning member: {user.name}",
            image_url=constants.Icons.user_unban,
            color=constants.Colours.soft_green,
        )
        embed.description = (
            f"{user.mention} was unbanned by {ctx.author.mention} for:\n{reason}"
        )

        # Info: https://discordpy.readthedocs.io/en/stable/api.html#discord.Guild.unban
        await ctx.guild.unban(user=user, reason=reason)

        # Send user message telling them that they were unbanned and why.
        try:  # Incase user has DM's Blocked.
            channel = await user.create_dm()
            message = f"You were unbanned from {ctx.guild} for: {reason}"
            await channel.send(message)
        except:
            embed.add_field(
                name="NOTICE", value="Unable to message member about this action."
            )

        # Add the unban to the mod_log database.
        with dataset.connect(database.get_db()) as db:
            db["mod_logs"].insert(
                dict(
                    user_id=user.id,
                    mod_id=ctx.author.id,
                    timestamp=ctx.message.created_at,
                    reason=reason,
                    type="unban",
                )
            )

        await ctx.reply(embed=embed)

    @commands.has_role("Staff")
    @commands.bot_has_permissions(
        kick_members=True, send_messages=True, embed_links=True
    )
    @commands.before_invoke(record_usage)
    @commands.command(name="kick")
    async def kick_member(self, ctx: Context, member: discord.Member, *, reason: str):
        """Kicks member from guild."""

        # Checks if invoker can action that user (self, bot, etc.)
        if not await self.can_action_user(ctx, member):
            return

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Kicking member: {member.name}",
            image_url=constants.Icons.user_ban,
            color=constants.Colours.soft_red,
        )
        embed.description = (
            f"{member.mention} was kicked by {ctx.author.mention} for:\n{reason}"
        )

        # Info: https://discordpy.readthedocs.io/en/stable/api.html#discord.Guild.kick
        await ctx.guild.kick(user=member, reason=reason)

        # Send user message telling them that they were kicked and why.
        try:  # Incase user has DM's Blocked.
            channel = await member.create_dm()
            message = f"You were kicked from {ctx.guild} for: {reason}"
            await channel.send(message)
        except:
            embed.add_field(
                name="NOTICE", value="Unable to message member about this action."
            )

        # Add the kick to the mod_log database.
        with dataset.connect(database.get_db()) as db:
            db["mod_logs"].insert(
                dict(
                    user_id=member.id,
                    mod_id=ctx.author.id,
                    timestamp=ctx.message.created_at,
                    reason=reason,
                    type="kick",
                )
            )

        await ctx.reply(embed=embed)

    @commands.has_role("Staff")
    @commands.bot_has_permissions(manage_roles=True, send_messages=True)
    @commands.before_invoke(record_usage)
    @commands.command(name="mute")
    async def mute(self, ctx: Context, member: discord.Member, *, reason: str):
        """Mutes member in guild."""

        # TODO: Implement temp/timed mute functionality

        # Checks if invoker can action that user (self, bot, etc.)
        if not await self.can_action_user(ctx, member):
            return

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Muting member: {member.name}",
            image_url=constants.Icons.user_mute,
            color=constants.Colours.soft_red,
        )
        embed.description = (
            f"{member.mention} was muted by {ctx.author.mention} for:\n{reason}"
        )

        # Adds "Muted" role to member.
        # TODO: Add role name to configuration, maybe by ID?
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.add_roles(role)

        # Send member message telling them that they were muted and why.
        try:  # Incase user has DM's Blocked.
            channel = await member.create_dm()
            message = f"You were muted in {ctx.guild} for: {reason}"
            await channel.send(message)
        except:
            embed.add_field(
                name="NOTICE", value="Unable to message member about this action."
            )

        # Add the mute to the mod_log database.
        with dataset.connect(database.get_db()) as db:
            db["mod_logs"].insert(
                dict(
                    user_id=member.id,
                    mod_id=ctx.author.id,
                    timestamp=ctx.message.created_at,
                    reason=reason,
                    type="mute",
                )
            )

        await ctx.reply(embed=embed)

    @commands.has_role("Staff")
    @commands.bot_has_permissions(manage_roles=True, send_messages=True)
    @commands.before_invoke(record_usage)
    @commands.command(name="unmute")
    async def unmute(self, ctx: Context, member: discord.Member, *, reason: str):
        """Unmutes member in guild."""

        # Checks if invoker can action that member (self, bot, etc.)
        if not await self.can_action_user(ctx, member):
            return

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Unmuting member: {member.name}",
            image_url=constants.Icons.user_unmute,
            color=constants.Colours.soft_green,
        )
        embed.description = (
            f"{member.mention} was unmuted by {ctx.author.mention} for:\n{reason}"
        )

        # Removes "Muted" role from member.
        # TODO: Add role name to configuration, maybe by ID?
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        await member.remove_roles(role)

        # Send member message telling them that they were banned and why.
        try:  # Incase user has DM's Blocked.
            channel = await member.create_dm()
            message = f"You were unmuted in {ctx.guild}. Try to behave in the future!"
            await channel.send(message)
        except:
            embed.add_field(
                name="NOTICE", value="Unable to message member about this action."
            )

        # Add the mute to the mod_log database.
        with dataset.connect(database.get_db()) as db:
            db["mod_logs"].insert(
                dict(
                    user_id=member.id,
                    mod_id=ctx.author.id,
                    timestamp=ctx.message.created_at,
                    reason=reason,
                    type="unmute",
                )
            )

        await ctx.reply(embed=embed)

    @commands.has_role("Staff")
    @commands.bot_has_permissions(send_messages=True)
    @commands.before_invoke(record_usage)
    @commands.command(name="warn")
    async def warn(self, ctx: Context, member: discord.Member, *, reason: str):
        """Sends member a warning DM and logs to database."""

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Warning member: {member.name}",
            image_url=constants.Icons.user_warn,
            color=constants.Colours.soft_orange,
        )
        embed.description = (
            f"{member.mention} was warned by {ctx.author.mention} for:\n{reason}"
        )

        # Send member message telling them that they were warned and why.
        try:  # Incase user has DM's Blocked.
            channel = await member.create_dm()
            message = f"You were warned in {ctx.guild} for: {reason}"
            await channel.send(message)
        except:
            embed.add_field(
                name="NOTICE", value="Unable to message member about this action."
            )

        # Add the warning to the mod_log database.
        with dataset.connect(database.get_db()) as db:
            db["mod_logs"].insert(
                dict(
                    user_id=member.id,
                    mod_id=ctx.author.id,
                    timestamp=ctx.message.created_at,
                    reason=reason,
                    type="warn",
                )
            )

        # Respond to the context that the member was warned.
        await ctx.reply(embed=embed)

    @commands.has_role("Staff")
    @commands.bot_has_permissions(send_messages=True)
    @commands.before_invoke(record_usage)
    @commands.command(name="addnote", aliases=["add_note", "note"])
    async def add_note(self, ctx: Context, member: discord.Member, *, note: str):
        """Adds a moderator note to a member."""

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Noting member: {member.name}",
            image_url=constants.Icons.pencil,
            color=constants.Colours.soft_blue,
        )
        embed.description = (
            f"{member.mention} was noted by {ctx.author.mention}:\n{note}"
        )

        # Add the note to the mod_notes database.
        with dataset.connect(database.get_db()) as db:
            db["mod_notes"].insert(
                dict(
                    user_id=member.id,
                    mod_id=ctx.author.id,
                    timestamp=ctx.message.created_at,
                    note=note,
                )
            )

        # Respond to the context that the message was noted.
        await ctx.reply(embed=embed)

    @commands.has_role("Staff")
    @commands.bot_has_permissions(
        embed_links=True,
        manage_messages=True,
        send_messages=True,
        read_message_history=True,
    )
    @commands.before_invoke(record_usage)
    @commands.command(name="remove", aliases=["rm"])
    async def remove_messages(
        self,
        ctx: Context,
        number_of_messages: Greedy[int] = 10,
        members: Greedy[discord.Member] = None,
        *,
        reason: str,
    ):
        """Remove numbers of messages from most recent or from specific members"""

        # Checking if the given message falls under the selected members, but if no members given, then remove them all.
        def should_remove(message: discord.Message):
            if members is None:
                return True
            elif message.author in members:
                return True
            return False

        embed = embeds.make_embed(
            ctx=ctx,
            title="Removing messages",
            image_url=constants.Icons.message_delete,
            color=constants.Colours.soft_red,
        )

        deleted = await ctx.channel.purge(limit=number_of_messages, check=should_remove)

        if members is None:
            embed.description = f"{ctx.author.mention} removed the previous {len(deleted)} messages for:\n{reason}"
        else:
            embed.description = (
                f"{ctx.author.mention} removed {len(deleted)} message(s) from:\n"
            )
            f"{', '.join([member.mention for member in members])}\n for:\n{reason}"
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Load the ModerationCog cog."""
    bot.add_cog(ModerationCog(bot))
    log.info("Cog loaded: ModerationCog")
