import logging
import datetime

import discord
from discord.ext import commands
from discord import Guild, Emoji, Role


log = logging.getLogger(__name__)


class GuildUpdates(commands.Cog):
    """ Guild event handler cog. """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_available(self, guild: Guild) -> None:
        """ Event Listener which is called when a guild becomes available.

        Args:
            guild (Guild): The Guild that has become available.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_available
        """
        log.info(f'{guild.name} has has become available.')

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild: Guild) -> None:
        """ Event Listener which is called when a guild becomes unavailable.

        Args:
            guild (Guild): The Guild that has become unavailable.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_unavailable
        """
        log.info(f'{guild.name} has has become unavailable.')

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        """ Event Listener which is called whenever a guild channel is created.

        Args:
            channel (discord.abc.GuildChannel): The guild channel that was created.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_channel_create
        """
        log.info(f'{channel.name} has has been created in {channel.guild}.')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        """ Event Listener which is called whenever a guild channel is deleted.

        Args:
            channel (discord.abc.GuildChannel): The guild channel that was deleted.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_channel_delete
        """
        log.info(f'{channel.name} has has been deleted in {channel.guild}.')

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel: discord.abc.GuildChannel, last_pin: datetime.datetime) -> None:
        """ Event Listener which is called whenever a message is pinned or unpinned from a guild channel.

        Args:
            channel (discord.abc.GuildChannel): The guild channel that had its pins updated.
            last_pin (datetime.datetime): The latest message that was pinned as a naive datetime in UTC. Could be None.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_channel_pins_update
        """
        log.info(f'{channel.name} updated its pin: {last_pin}.')

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel) -> None:
        """ Event Listener which is called whenever a guild channel is updated. e.g. changed name, topic, permissions.

        Args:
            before (discord.abc.GuildChannel): The updated guild channel’s old info.
            after (discord.abc.GuildChannel): The updated guild channel’s new info.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_channel_update
        """

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild: Guild, before: Emoji, after: Emoji) -> None:
        """ Event Listener which is called when a Guild adds or removes Emoji.

        Args:
            guild (Guild): The guild who got their emojis updated.
            before (Emoji): A list of emojis before the update.
            after (Emoji): A list of emojis after the update.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_emojis_update
        """

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild: Guild) -> None:
        """ Event Listener which is called whenever an integration is created, modified, or removed from a guild.

        Args:
            guild (Guild): The guild that had its integrations updated.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_integrations_update
        """

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        """ Event Listener which is called when a Guild is either created by the Bot or when the Bot joins a guild.

        Args:
            guild (Guild): The guild that was joined.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_join
        """
        log.info(f'{guild.name} has a joined a new guild')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        """ Event Listener which is called when a Guild is removed from the Client.

        Args:
            guild (Guild): The guild that got removed.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_remove
        """

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: Role) -> None:
        """ Event Listener which is called when a Guild creates a new Role.

        Args:
            role (Role): The role that was created.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_role_create
        """

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: Role) -> None:
        """ Event Listener which is called when a Guild deletes a Role.

        Args:
            role (Role): The role that was deleted.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_role_delete
        """

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: Role, after: Role) -> None:
        """ Event Listener which is called when a Role is changed guild-wide.

        Args:
            before (Role): The updated role’s old info.
            after (Role): The updated role’s updated info.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_role_update
        """

    @commands.Cog.listener()
    async def on_guild_update(self, before: Guild, after: Guild) -> None:
        """ Event Listener which is called when a Guild updates.

        Args:
            before (Guild): The guild prior to being updated.
            after (Guild): The guild after being updated.

        Note:
            This requires Intents.guilds to be enabled.

        For more information:
            https://discordpy.readthedocs.io/en/stable/api.html#discord.on_guild_update
        """


def setup(bot: commands.Bot) -> None:
    """ Load the guild_updates cog. """
    bot.add_cog(GuildUpdates(bot))
    log.info("Cog loaded: guild_updates")
