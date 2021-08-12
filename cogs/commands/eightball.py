import logging
import random

from discord.ext import commands
from discord.ext.commands import Cog, Context, Bot
from tools import embeds, record


log = logging.getLogger(__name__)


class EightBall(Cog):
    """EightBall cog."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.before_invoke(record.record_usage)
    @commands.command(name="8ball", aliases=["EightBall"])
    async def do_8ball(self, ctx: Context, *, question: str):
        """
        The Magic 8 Ball Oracle has answer to all the questions.
        Simply give it a yes or no question
        """

        log.info(f"{ctx.author} has gave a question to the 8ball gods: {question}.")

        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        embed = embeds.MakeEmbed(
            ctx=ctx,
            title="Magic 8 Ball",
            image_url="https://cdn.discordapp.com/attachments/757466211218096258/799387685088526406/s8b.png",
        )
        embed.add_field(name="Question:", value=question, inline=False)
        embed.add_field(name="Answer:", value=random.choice(responses), inline=False)
        await ctx.reply(embed=embed)


def setup(bot: Bot) -> None:
    """Load the EightBall cog."""
    bot.add_cog(EightBall(bot))
    log.info("Cog loaded: EightBall")
