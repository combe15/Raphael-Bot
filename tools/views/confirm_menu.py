import logging
from typing import Union

import discord

log = logging.getLogger(__name__)


class ConfirmMenu(discord.ui.View):
    """
    Args:
        authorized_user (Union[discord.User, discord.Member], optional): [Restricts button interaction to user].
            Defaults to None.
        timeout (Optional[float]):
            [Timeout in seconds from last interaction with the UI before no longer accepting input.]
            Default is 120 seconds.
            If None then there is no timeout.
    """

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

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.__authorized__(button, interaction):
            return
        self.value = "confirm"
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):

        if not self.__authorized__(button, interaction):
            return
        self.value = "cancel"
        self.stop()
