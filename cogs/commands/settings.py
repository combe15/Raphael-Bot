import traceback
import logging
import glob
import re

import discord
from discord.ext import commands


log = logging.getLogger(__name__)


class Utilities(commands.Cog):
    """ Utilities """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_result = None

    @commands.is_owner()
    @commands.command(name="disable")
    async def disable_command(self, ctx: commands.Context, name_of_command: str):
        """ disable specified command """
        command = self.bot.get_command(name_of_command)
        if command is None:
            await ctx.reply(f"Command {name_of_command}, was not found.")
        else:
            command.enabled = False
            await ctx.reply(f"Command {command}, has been disabled")

    @commands.is_owner()
    @commands.command(name="enable")
    async def enable_command(self, ctx: commands.Context, name_of_command: str):
        """ enable specified command """
        command = self.bot.get_command(name_of_command)
        if command is None:
            await ctx.reply(f"Command {name_of_command}, was not found.")
        else:
            command.enabled = True
            await ctx.reply(f"Command {command}, has been enabled")

    @commands.is_owner()
    @commands.command(name="reload")
    async def reload_cog(self, ctx: commands.Context, name_of_cog: str = None):
        """ Reloads specified cog or all cogs. """

        regex = r"(?<=<).*(?=\..* object at 0x.*>)"
        if name_of_cog is not None and name_of_cog in ctx.bot.cogs:
            # Reload cog if it exists.
            cog = re.search(regex, str(ctx.bot.cogs[name_of_cog]))
            try:
                self.bot.reload_extension(cog.group())
                
            except commands.ExtensionError as e:
                await ctx.message.add_reaction("❌")
                await ctx.reply(f'{e.__class__.__name__}: {e}')
            
            else:
                await ctx.message.add_reaction("✔")
                await ctx.reply(f"Reloaded `{cog.group()}` module!")
        
        elif name_of_cog is None:
            # Reload all the cogs in the folder named cogs.
            # Skips over any cogs that start with '__' or do not end with .py.
            cogs = []
            try:
                for cog in glob.iglob("cogs/**/[!^_]*.py", recursive=True):
                    if "\\" in cog:  # Pathing on Windows.
                        self.bot.reload_extension(cog.replace("\\", ".")[:-3])
                    else:  # Pathing on Linux.
                        self.bot.reload_extension(cog.replace("/", ".")[:-3])
            except commands.ExtensionError as e:
                await ctx.message.add_reaction("❌")
                await ctx.reply(f'{e.__class__.__name__}: {e}')

            else:
                await ctx.message.add_reaction("✔")
                await ctx.reply("Reloaded all modules!")

        else:
            await ctx.message.add_reaction("❌")
            await ctx.reply("Module not found, check spelling, it's case sensitive")

def setup(bot: commands.Bot) -> None:
    """Load the Utilities cog."""
    bot.add_cog(Utilities(bot))
    log.info("Cog loaded: Utilities")
