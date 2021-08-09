import logging
from typing import Union

import discord

log = logging.getLogger(__name__)


class PageMenu(discord.ui.View):
    def __init__(
        self, authorized_user: Union[discord.User, discord.Member] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.authorized_user = authorized_user
        self.value: str = None

    def __authorized__(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> bool:
        """Returns True if interaction is authorized"""
        if self.authorized_user and self.authorized_user.id != interaction.user.id:
            log.trace(
                f"Button `{button.label}.{self.__class__.__name__}` pressed by wrong user {interaction.user=}"
            )
            return False

        log.trace(
            f"Button `{button.label}.{self.__class__.__name__}` pressed by user {interaction.user=}"
        )
        return True

    @discord.ui.button(label="First", style=discord.ButtonStyle.blurple)
    async def first(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.__authorized__(button, interaction):
            return
        self.value = "first"
        self.stop()

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.__authorized__(button, interaction):
            return
        self.value = "back"
        self.stop()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.__authorized__(button, interaction):
            return
        self.value = "next"
        self.stop()

    @discord.ui.button(label="Last", style=discord.ButtonStyle.blurple)
    async def last(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.__authorized__(button, interaction):
            return
        self.value = "last"
        self.stop()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.__authorized__(button, interaction):
            return
        self.value = "close"
        self.stop()
