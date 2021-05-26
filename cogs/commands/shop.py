import logging

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Context, Bot, BucketType
import requests

import constants
from tools import embeds, record, subby_api


log = logging.getLogger(__name__)


PREFIX = constants.Bot.prefix
BUY_EMOJI = constants.Shop_emoji.buy_price
DELETE_EMOJI = constants.Shop_emoji.delete_price
RENAME_EMOJI = constants.Shop_emoji.rename_price


class Shop(Cog):
    """Shop: Exchange goods and serives in exchange for money."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.before_invoke(record.record_usage)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_emojis=True, embed_links=True)
    @commands.group(name="emoji", aliases=["emote"])
    async def emote(self, ctx: Context) -> None:
        """
        Members can buy and remove their own emotes!
        You may add any emote of your choosing.

        They may not be offensive, NSFW, or incite violence.

        Staff have the final say on whether or not an emoji stays
        You will not be reimbursed if staff removes your emote."""
        if ctx.invoked_subcommand is None:
            # Send the help command for this group
            await ctx.send_help(ctx.command)

    @emote.command(
        name="buy",
        aliases=["add"],
        brief=f"Add your own emoji to the server.\nCost: {BUY_EMOJI:,} :ramen:",
        description=f"Use this command to add your own emoji to the server.\nCost: {BUY_EMOJI:,} :ramen:",
    )
    async def buy(self, ctx: Context, emote_name: str, image_url: str) -> None:
        """Add your own emoji to the server."""

        # Get guild count of animated and non animated emoji's
        emoji_count = {"non_animated": 0, "animated": 0}
        emojis = ctx.guild.emojis
        for emoji in emojis:
            if emoji.animated:
                emoji_count["animated"] += 1
            else:
                emoji_count["non_animated"] += 1

        log.debug(f"{emoji_count['non_animated']=}, {emoji_count['animated']=}")

        # Check if requested emoji doesn't go over the guild's limit
        if (
            image_url.endswith(".gif")
            and emoji_count["animated"] <= ctx.guild.emoji_limit
        ):
            pass  # do nothing
        elif emoji_count["non_animated"] <= ctx.guild.emoji_limit:
            pass  # do nothing
        else:
            await embeds.error_message(
                ctx=ctx,
                description="Server is at emoji limit. You must delete an emoji to add more.",
            )
            return

        # Check if user can buy emoji
        if (bal := subby_api.get_balance(ctx.author.id)) < BUY_EMOJI:
            await embeds.warning_message(
                ctx=ctx,
                description=f"Insufficient funds, you need {BUY_EMOJI} :ramen:\nYour balance: {bal:,}",
            )
            log.info(
                f"Emote.buy: Error {ctx.author.name} didn't meet funds of {DELETE_EMOJI}, while {bal=}"
            )
            return

        try:
            response = requests.get(image_url, stream=True)
            emote = await ctx.guild.create_custom_emoji(
                name=emote_name, image=response.content
            )
        except discord.Forbidden:
            await embeds.error_message(
                ctx=ctx,
                description="Bot must have the manage_emojis permission to do this.",
            )
            log.info(
                f"Emote.buy: Error {ctx.author.name} bot doesn't have manage_emojis permission."
            )
            return
        except discord.HTTPException as e:
            await embeds.error_message(
                ctx=ctx, description=f"An error occurred creating an emoji.\n {e.text}"
            )
            log.info(f"Emote.buy: Error {ctx.author.name} HTTPException, {e.text}.")
            return

        subby_api.subtract_balance(ctx.author.id, BUY_EMOJI, True)
        subby_api.record_ledger(
            ctx.author.id, ctx.me.id, BUY_EMOJI, f"Created emoji {emote}"
        )
        subby_api.record_emoji(ctx.author.id, emote.name, "purchase", BUY_EMOJI)
        log.info(
            f"Emote.buy: {ctx.author.name}'s money was taken out of their account'"
        )

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Emoji Purchased `:{emote.name}:`",
            description=f"{BUY_EMOJI:,} :ramen: removed from your account\n",
            image_url=emote.url,
        )
        await ctx.reply(embed=embed)

    @commands.cooldown(3, 86400, type=BucketType.member)  # 1 day = 86400 seconds
    @emote.command(
        name="delete",
        aliases=["remove"],
        brief=f"remove an emoji from the server.\nCost: {DELETE_EMOJI:,} :ramen:",
        description=f"Use this command to remove an emoji from the server.\nCost: {DELETE_EMOJI:,} :ramen:",
    )
    async def delete(self, ctx: Context, emote: discord.Emoji) -> None:
        """Remove an emoji from the server."""
        if emote.guild.id != ctx.guild.id:
            await embeds.error_message(
                ctx=ctx, description="This emoji is not from this server."
            )
            log.info(f"{ctx.author.name} tried to delete a emote not from the server.")
            return

        if (bal := subby_api.get_balance(ctx.author.id)) < DELETE_EMOJI:
            await embeds.warning_message(
                ctx=ctx,
                description=f"Insufficient funds, you need {DELETE_EMOJI} :ramen:\nYour balance: {bal:,}",
            )
            log.info(
                f"Emote.delete: Error {ctx.author.name} didn't meet funds of {DELETE_EMOJI}, while {bal=}"
            )
            return

        try:
            await emote.delete(reason=f"{ctx.author.name} paid to delete emoji.")
        except discord.Forbidden:
            await embeds.error_message(
                ctx=ctx,
                description="Bot must have the manage_emojis permission to do this.",
            )
            log.error(
                f"Emote.delete: Error {ctx.author.name} bot doesn't have manage_emojis permission."
            )
            return
        except discord.HTTPException as e:
            await embeds.error_message(
                ctx=ctx, description=f"An error occurred removing an emoji.\n {e.text}"
            )
            log.error(f"Emote.delete: Error {ctx.author.name} HTTPException, {e.text}.")
            return

        subby_api.subtract_balance(ctx.author.id, DELETE_EMOJI, True)
        subby_api.record_ledger(
            ctx.author.id, ctx.me.id, DELETE_EMOJI, f"Removed emoji {emote}"
        )
        subby_api.record_emoji(ctx.author.id, emote.name, "removal", DELETE_EMOJI)
        log.info(
            f"Emote.delete: {ctx.author.name}'s money was taken out of their account'"
        )

        embed = embeds.make_embed(
            ctx=ctx,
            title="Emoji deleted",
            description=f"{DELETE_EMOJI:,} :ramen: removed from your account",
            image_url=emote.url,
        )
        await ctx.reply(embed=embed)

    @commands.cooldown(3, 86400, type=BucketType.member)  # 1 day = 86400 seconds
    @emote.command(
        name="rename",
        aliases=["name"],
        brief=f"rename an emoji from the server.\nCost: {RENAME_EMOJI:,} :ramen:",
        description=f"Use this command to rename an emoji from the server.\nCost: {RENAME_EMOJI:,} :ramen:",
    )
    async def rename(self, ctx: Context, emote: discord.Emoji, new_name: str) -> None:
        """Rename an emoji from the server."""
        if emote.guild.id != ctx.guild.id:
            await embeds.error_message(
                ctx=ctx, description="This emoji is not from this server."
            )
            log.info(f"{ctx.author.name} tried to rename a emote not from the server.")
            return

        if (bal := subby_api.get_balance(ctx.author.id)) < RENAME_EMOJI:
            await embeds.warning_message(
                ctx=ctx,
                description=f"Insufficient funds, you need {RENAME_EMOJI} :ramen:\nYour balance: {bal:,}",
            )
            log.info(
                f"Emote.rename: Error {ctx.author.name} didn't meet funds of {RENAME_EMOJI}, while {bal=}"
            )
            return

        try:
            await emote.edit(
                name=new_name, reason=f"{ctx.author.name} paid to rename emoji."
            )

        except discord.Forbidden:
            await embeds.error_message(
                ctx=ctx,
                description="Bot must have the manage_emojis permission to do this.",
            )
            log.error(
                f"Emote.rename: Error {ctx.author.name} bot doesn't have manage_emojis permission."
            )
            return
        except discord.HTTPException as e:
            await embeds.error_message(
                ctx=ctx, description=f"An error occurred renameing an emoji.\n {e.text}"
            )
            log.error(f"Emote.rename: Error {ctx.author.name} HTTPException, {e.text}.")
            return

        subby_api.subtract_balance(ctx.author.id, RENAME_EMOJI, True)
        subby_api.record_ledger(
            ctx.author.id, ctx.me.id, RENAME_EMOJI, f"Renamed emoji {emote}"
        )
        log.info(
            f"Emote.rename: {ctx.author.name}'s money was taken out of their account'"
        )

        embed = embeds.make_embed(
            ctx=ctx,
            title="Emoji renamed",
            description=f"{RENAME_EMOJI:,} :ramen: removed from your account",
            image_url=emote.url,
        )
        await ctx.reply(embed=embed)


def setup(bot: Bot) -> None:
    """Load the Shop cog."""
    bot.add_cog(Shop(bot))
    log.info("Cog loaded: Shop")
