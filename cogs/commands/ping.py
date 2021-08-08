from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context
from tools.record import record_usage

import logging

log = logging.getLogger(__name__)


class Ping(Cog):
    """Ping"""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.before_invoke(record_usage)
    @commands.command(name="ping")
    async def ping(self, ctx: Context):
        """Ping tool lets you see if the bot is responding and give you the latency"""
        log.info(
            f"{ctx.author} pinged the bot with a latency of {round(self.bot.latency * 1000)}ms."
        )
        await ctx.send(f"🏓Pong! {round(self.bot.latency * 1000)}ms")


def setup(bot: Bot) -> None:
    """Load the Ping cog."""
    bot.add_cog(Ping(bot))
    log.info("Cog loaded: Ping")
