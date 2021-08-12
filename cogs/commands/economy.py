import logging

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context

from tools import embeds, record
from tools.bank import Bank

log = logging.getLogger(__name__)


class Economy(Cog):
    """Economy"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="balance", aliases=["bal"])
    async def balance(self, ctx: Context, user: discord.User = None) -> None:
        """Display a player's balance."""

        user = user or ctx.author

        embed = embeds.MakeEmbed(
            ctx=ctx,
            image_url="https://cdn.iconscout.com/icon/free/png-128/bank-1850789-1571030.png",
        )

        if user is ctx.author:
            embed.title = "Your Balance"
            embed.description = f"{Bank(ctx.author):,.2f} :coin:"

        else:
            embed.title = "Their Balance"
            embed.description = f"{user.mention} has {Bank(user):,.2f} :coin:"

        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="pay", aliases=["payment", "give"])
    async def payment(self, ctx: Context, user: discord.User, amount: int) -> None:
        """Pay a Player."""

        if user == ctx.author:
            await embeds.error_message(
                ctx=ctx,
                description="So you are trying to pay yourself, what did you win?",
            )
            return

        elif amount == 0:
            await embeds.error_message(
                ctx=ctx,
                description="You have to pay something, or else what was the point?",
            )
            return

        elif amount < 0:
            await embeds.error_message(
                ctx=ctx, description="No, negative payment isn't valid!"
            )
            return

        elif Bank(ctx.author) <= amount:
            await embeds.error_message(
                ctx=ctx, description="You cannot pay what you do not have."
            )
            return

        Bank(ctx.author).subtract(amount, f"Payment to {user.name}")
        Bank(user).add(amount, f"Payment from {user.name}")

        embed = embeds.MakeEmbed(
            ctx=ctx,
            title="Payment",
            description=f"{ctx.author.mention} has paid {user.mention}\n*Amount*={amount:,} :coin:",
        )
        embed.set_thumbnail(
            url="https://cdn.iconscout.com/icon/free/png-128/bank-1850789-1571030.png"
        )
        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="set_balance", aliases=["set_bal", "setbal"])
    @commands.is_owner()
    async def set_balance(
        self, ctx: Context, user: discord.User = None, amount: float = 0
    ) -> None:
        """Overide a user's balance."""
        if isinstance(user, int):
            amount = user
            user = ctx.author

        embed = embeds.MakeEmbed(
            ctx=ctx,
            title="Setting Player's Balance",
            description=f"{user.mention}'s balance has been set to {amount:,.2f} :coin:"
            f"from {(bank := Bank(user)):,.2f} :coin:",
        )
        embed.set_thumbnail(
            url="https://cdn.iconscout.com/icon/free/png-128/bank-1850789-1571030.png"
        )
        bank.set(amount)
        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="give_balance", aliases=["give_bal", "givebal", "addbal"])
    @commands.is_owner()
    async def give_balance(
        self, ctx: Context, user: discord.User, amount: float, reason: str = ""
    ) -> None:
        """Add money to a user's account."""

        bank = Bank(user).add(amount, reason)
        embed = embeds.MakeEmbed(
            ctx=ctx,
            title="Giving Player Money",
            description=f"{user.mention}'s been given {amount:,}:coin:\n"
            f"New balance {bank:,.2f}:coin:",
        )
        if reason:
            embed.add_field(text="Reason", value=reason)
        embed.set_thumbnail(
            url="https://cdn.iconscout.com/icon/free/png-128/bank-1850789-1571030.png"
        )
        await ctx.reply(embed=embed)


def setup(bot: Bot) -> None:
    """Load the Economy cog."""
    bot.add_cog(Economy(bot))
    log.info("Cog loaded: Economy")
