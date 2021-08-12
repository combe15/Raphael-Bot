from typing import Union, Type, TypeVar

from discord import Embed
import discord
from discord.ext.commands import Context

CT = TypeVar("CT", bound="MoreColors")


class MoreColors(discord.Color):
    """Represents a Discord role color. This class is similar
    to a (red, green, blue) :class:`tuple`.

    Attributes
    ------------
    value: :class:`int`
        The raw integer colour value.
    """

    def __init__(self, value: int):
        super().__init__(value)

    @classmethod
    def reddit(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xFF5700``."""
        return cls(0xFF5700)

    @classmethod
    def orange_red(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xFF450``."""
        return cls(0xFF450)

    @classmethod
    def upvote(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xFF8B60``."""
        return cls(0xFF8B60)

    @classmethod
    def neutral(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xC6C6C6``."""
        return cls(0xC6C6C6)

    @classmethod
    def downvote(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x9494FF``."""
        return cls(0x9494FF)

    @classmethod
    def light_bg(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xEFF7FF``."""
        return cls(0xEFF7FF)

    @classmethod
    def header(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0xCEE3F8``."""
        return cls(0xCEE3F8)

    @classmethod
    def ui_text(cls: Type[CT]) -> CT:
        """A factory method that returns a :class:`Colour` with a value of ``0x336699``."""
        return cls(0x336699)


class MakeEmbed(Embed):
    """Constructs a General Discord embed.

    Certain properties return an ``EmbedProxy``, a type
    that acts similar to a regular :class:`dict` except using dotted access,
    e.g. ``embed.author.icon_url``. If the attribute
    is invalid or empty, then a special sentinel value is returned,
    :attr:`Embed.Empty`.

    For ease of use, all parameters that expect a :class:`str` are implicitly
    casted to :class:`str` for you.

    Attributes
    -----------
    title: :class:`str`
        The title of the embed.
        This can be set during initialization.
    description: :class:`str`
        The description of the embed.
        This can be set during initialization.
    ctx: :class:`Context`
        Discord context object, needed for author and timestamps.
        Defaults to None.
    color: Union[:class:`MoreColors`, :class:`int`]
        The color code of the embed.
        This can be set during initialization.
    image_url: :class:`str`
        URL for the thumbnail image of embed.
        Defaults to None.
    author: :class:`bool`
        Whether or not you wish to set the author of embed.
        Defaults to True.
    """

    def __init__(
        self,
        title: str = None,
        description: str = None,
        ctx: Context = None,
        color: Union["MoreColors", int] = MoreColors.dark_theme(),
        image_url: str = None,
        author: bool = True,
        **kwarg,
    ) -> Embed:
        super().__init__(**kwarg)

        self.colour = color

        if author and ctx:
            self.set_author(icon_url=ctx.author.avatar.url, name=str(ctx.author))

        if image_url:
            self.set_thumbnail(url=image_url)

        if ctx:
            # Created_at value is not always at the same location.
            try:
                self.timestamp = ctx.message.created_at
            except AttributeError:
                self.timestamp = ctx.created_at


async def error_message(description: str, ctx: Context, author: bool = True):
    """Send basic error message

    Note:
        You must await this function

    Args:
        description (str): Error description.
        ctx (Context): Discord context object, needed for author and timestamps.
        author (bool, optional): Whether or not you wish to set the author of embed. Defaults to True.
    """
    await ctx.send(
        embed=MakeEmbed(
            title="ERROR",
            description=f"📢 **{description}**",
            ctx=ctx,
            color=MoreColors.dark_red(),
            author=author,
        ),
        delete_after=30,
    )


def error_embed(
    title: str, description: str, ctx: Context, author: bool = True
) -> Embed:
    """Make a basic Error message embed

    Args:
        title (str): Name of error.
        description (str): Error description.
        ctx (Context): Discord context object, needed for author and timestamps.
        author (bool, optional): Whether or not you wish to set the author of embed. Defaults to True.

    Returns:
        Embed: discord embed object.
    """
    return MakeEmbed(
        title=f"ERROR: {title}",
        description=f"📢 **{description}**",
        ctx=ctx,
        color=MoreColors.red(),
        author=author,
    )


async def warning_message(ctx: Context, description: str, author: bool = True):
    """Send a basic warning message

    Note:
        You must await this function

    Args:
        description (str): Warning description
        ctx (Context): Discord context object, needed for author and timestamps.
        author (bool, optional): Whether or not you wish to set the author of embed. Defaults to True.
    """
    await ctx.send(
        embed=MakeEmbed(
            title="WARNING",
            description=f"📢 **{description}**",
            ctx=ctx,
            color=MoreColors.dark_gold(),
            author=author,
        ),
        delete_after=30,
    )
