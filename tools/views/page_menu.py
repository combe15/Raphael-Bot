import logging

import discord

log = logging.getLogger(__name__)


class PageMenu(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value: str = None

    @discord.ui.button(label="First", style=discord.ButtonStyle.blurple)
    async def first(self, button: discord.ui.Button, interaction: discord.Interaction):

        log.trace("Got First page_menu button")
        self.value = "first"
        self.stop()

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):

        log.trace("Got Back page_menu button")
        self.value = "back"
        self.stop()

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):

        log.trace("Got Next page_menu button")
        self.value = "next"
        self.stop()

    @discord.ui.button(label="Last", style=discord.ButtonStyle.blurple)
    async def last(self, button: discord.ui.Button, interaction: discord.Interaction):

        log.trace("Got Last page_menu button")
        self.value = "last"
        self.stop()

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):

        log.trace("Got Close page_menu button")
        self.value = "close"
        self.stop()
