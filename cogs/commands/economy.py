import logging
import datetime

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context

from tools import embeds, subby_api, record


log = logging.getLogger(__name__)


class Economy(Cog):
    """ Economy """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name='balance', aliases=['bal'])
    async def balance(self, ctx: Context, member: discord.Member = None) -> None:
        """ Display a player's balance. """

        member = member or ctx.author

        embed = embeds.make_embed(ctx=ctx, image_url='https://subby.dev/i/icons/atm.png')

        if member is ctx.author:
            embed.title="Your Balance"
            embed.description=f"{subby_api.get_balance(ctx.author.id):,.1f} :ramen:"

        else:
            embed.title="Their Balance"
            embed.description=f"{member.mention} has {subby_api.get_balance(member.id):,.1f} :ramen:"

        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name='pay', aliases=['payment', 'give'])
    async def payment(self, ctx: Context, member: discord.Member, amount: int) -> None:
        """ Pay a Player. """

        if member == ctx.author:
            await embeds.error_message(ctx=ctx, description="So you are trying to pay yourself, what did you win?")
            return

        elif amount == 0:
            await embeds.error_message(ctx=ctx, description="You have to pay something, or else what was the point?")
            return

        elif amount < 0:
            await embeds.error_message(ctx=ctx, description="No, negative payment isn't valid!")
            return

        elif subby_api.get_balance(ctx.author.id) <= amount:
            await embeds.error_message(ctx=ctx, description="You cannot pay what you do not have.")
            return

        subby_api.subtract_balance(ctx.author.id, amount)
        subby_api.add_balance(member.id, amount)

        subby_api.record_ledger(ctx.author.id, member.id, amount, f"Member payment")

        embed = embeds.make_embed(
            ctx=ctx, title="Payment", description=f"{ctx.author.mention} has paid {member.mention}\n*Amount*={amount:,} :ramen:")
        embed.set_thumbnail(url="https://subby.dev/i/icons/atm.png")
        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name='set_balance', aliases=['set_bal', 'setbal'])
    @commands.is_owner()
    async def set_balance(self, ctx: Context, user: discord.User = None, amount: float = 0) -> None:
        """ Overide a user's balance. """
        if isinstance(user, int):
            amount = user
            user = ctx.author

        embed = embeds.make_embed(
            ctx=ctx, title="Setting Player's Balance",
            description=f"{user.mention}'s balance has been set to {amount:,.1f} :ramen: from {subby_api.get_balance(user.id):,.1f} :ramen:")
        embed.set_thumbnail(url="https://subby.dev/i/icons/atm.png")
        subby_api.set_balance(user.id, amount)
        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name='give_balance', aliases=['give_bal', 'givebal', 'addbal'])
    @commands.is_owner()
    async def give_balance(self, ctx: Context, user: discord.User, amount: float, reason: str = '') -> None:
        """ Add money to a user's account. """

        subby_api.add_balance(user.id, amount)
        embed = embeds.make_embed(ctx=ctx, title="Giving Player Money",
                            description=f"{user.mention}'s been given {amount:,}:ramen: \nNew balance {subby_api.get_balance(user.id):,.1f}:ramen:")
        if reason:
            embed.add_field(text="Reason", value=reason)
        embed.set_thumbnail(url="https://subby.dev/i/icons/atm.png")
        await ctx.reply(embed=embed)


def setup(bot: Bot) -> None:
    """ Load the Economy cog. """
    bot.add_cog(Economy(bot))
    log.info("Cog loaded: Economy")
