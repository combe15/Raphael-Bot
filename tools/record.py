import logging
from discord.ext.commands import Context

# Enabling logs
log = logging.getLogger(__name__)


async def record_usage(self, ctx: Context):
    """ Recording useage of command

    Args:
        ctx (Context): Discord context object
    """
    log.info(f"{ctx.author} issued command @ {ctx.guild} in {ctx.channel}:  {ctx.message.clean_content}")