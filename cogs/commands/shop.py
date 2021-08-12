import logging

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Context, Bot, BucketType
import requests

import constants
from tools import embeds, record
from tools.bank import Bank


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
        brief=f"Add your own emoji to the server.\nCost: {BUY_EMOJI:,} :coin:",
        description=f"Use this command to add your own emoji to the server.\nCost: {BUY_EMOJI:,} :coin:",
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
        if (bal := Bank(ctx.author)) < BUY_EMOJI:
            await embeds.warning_message(
                ctx=ctx,
                description=f"Insufficient funds, you need {BUY_EMOJI} :coin:\nYour balance: {bal:,}",
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

        Bank(ctx.author).subtract(BUY_EMOJI, f"Created emoji {emote}")
        log.info(
            f"Emote.buy: {ctx.author.name}'s money was taken out of their account'"
        )

        embed = embeds.MakeEmbed(
            ctx=ctx,
            title=f"Emoji Purchased `:{emote.name}:`",
            description=f"{BUY_EMOJI:,} :coin: removed from your account\n",
            image_url=emote.url,
        )
        await ctx.reply(embed=embed)

    @commands.cooldown(3, 86400, type=BucketType.member)  # 1 day = 86400 seconds
    @emote.command(
        name="delete",
        aliases=["remove"],
        brief=f"remove an emoji from the server.\nCost: {DELETE_EMOJI:,} :coin:",
        description=f"Use this command to remove an emoji from the server.\nCost: {DELETE_EMOJI:,} :coin:",
    )
    async def delete(self, ctx: Context, emote: discord.Emoji) -> None:
        """Remove an emoji from the server."""
        if emote.guild.id != ctx.guild.id:
            await embeds.error_message(
                ctx=ctx, description="This emoji is not from this server."
            )
            log.info(f"{ctx.author.name} tried to delete a emote not from the server.")
            return

        if (bal := Bank(ctx.author)) < DELETE_EMOJI:
            await embeds.warning_message(
                ctx=ctx,
                description=f"Insufficient funds, you need {DELETE_EMOJI} :coin:\nYour balance: {bal:,}",
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

        Bank(ctx.author).subtract(DELETE_EMOJI, f"Removed emoji {emote}")
        log.info(
            f"Emote.delete: {ctx.author.name}'s money was taken out of their account'"
        )

        embed = embeds.MakeEmbed(
            ctx=ctx,
            title="Emoji deleted",
            description=f"{DELETE_EMOJI:,} :coin: removed from your account",
            image_url=emote.url,
        )
        await ctx.reply(embed=embed)

    @commands.cooldown(3, 86400, type=BucketType.member)  # 1 day = 86400 seconds
    @emote.command(
        name="rename",
        aliases=["name"],
        brief=f"rename an emoji from the server.\nCost: {RENAME_EMOJI:,} :coin:",
        description=f"Use this command to rename an emoji from the server.\nCost: {RENAME_EMOJI:,} :coin:",
    )
    async def rename(self, ctx: Context, emote: discord.Emoji, new_name: str) -> None:
        """Rename an emoji from the server."""
        if emote.guild.id != ctx.guild.id:
            await embeds.error_message(
                ctx=ctx, description="This emoji is not from this server."
            )
            log.info(f"{ctx.author.name} tried to rename a emote not from the server.")
            return

        if (bal := Bank(ctx.author)) < RENAME_EMOJI:
            await embeds.warning_message(
                ctx=ctx,
                description=f"Insufficient funds, you need {RENAME_EMOJI} :coin:\nYour balance: {bal:,}",
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

        Bank(ctx.author).subtract(RENAME_EMOJI, f"Renamed emoji {emote}")
        log.info(
            f"Emote.rename: {ctx.author.name}'s money was taken out of their account'"
        )

        embed = embeds.MakeEmbed(
            ctx=ctx,
            title="Emoji renamed",
            description=f"{RENAME_EMOJI:,} :coin: removed from your account",
            image_url=emote.url,
        )
        await ctx.reply(embed=embed)


def setup(bot: Bot) -> None:
    """Load the Shop cog."""
    bot.add_cog(Shop(bot))
    log.info("Cog loaded: Shop")
