import logging
import discord
from discord.ext import commands
from tools import embeds, record

log = logging.getLogger(__name__)


class PlayerInfo(commands.Cog):
    """PlayerInfo"""

    def __init__(self, bot):
        self.bot = bot

    @commands.before_invoke(record.record_usage)
    @commands.is_owner()
    @commands.command(name="info")
    async def info(self, ctx, member: discord.Member = None):
        """Returns information about a user"""

        member = member or ctx.author

        role_list = " ".join([str(f"•{elm.name}\n") for elm in member.roles[1:]])

        embed = embeds.MakeEmbed(
            ctx=ctx,
            title=f"{member.display_name}'s User Info",
            image_url=member.avatar.url,
            color=embeds.MoreColors.blurple(),
            description="Returning info about selected user",
        )
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Nickname", value=member.nick, inline=False)
        embed.add_field(name="Status", value=member.status, inline=False)
        embed.add_field(name="In Server", value=member.guild, inline=False)
        embed.add_field(name="Joined Server", value=member.joined_at, inline=False)
        embed.add_field(name="Joined Discord", value=member.created_at, inline=False)
        embed.add_field(name="Roles", value=role_list, inline=False)
        # embed.add_field(name='Perms', value=member.guild_permissions, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="count")
    async def count(self, ctx):
        """Returns the current guild member count."""
        await ctx.send(ctx.guild.member_count)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(embed_links=True)
    @commands.command(name="profile_picture", aliases=["pfp"])
    async def pfp(self, ctx, user: discord.User = None):
        """Returns the profile picture of the invoker or the mentioned user."""
        user = user or ctx.author
        embed = embeds.MakeEmbed(
            ctx=ctx, description=f"[{user.name}]({user.avatar.url})"
        )
        embed.set_image(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.guild_only()
    @commands.command(name="perms", aliases=["perms_for", "permissions"])
    async def check_permissions(self, ctx, member: discord.Member = None):
        """A simple command which checks a member's Guild Permissions.
        If member is not provided, the author will be checked."""

        member = member or ctx.author

        # Here we check if the value of each permission is True.
        perms = "\n".join(perm for perm, value in member.guild_permissions if value)

        # And to make it look nice, we wrap it in an Embed.
        embed = embeds.MakeEmbed(
            ctx=ctx,
            title="Permissions for:",
            description=ctx.guild.name,
            colour=member.colour,
        )
        embed.set_author(icon_url=member.avatar.url, name=str(member))

        # \uFEFF is a Zero-Width Space, which basically allows us to have an empty field name.
        embed.add_field(name="\uFEFF", value=perms)

        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.command()
    async def lastMessage(self, ctx, *channel_ids: commands.TextChannelConverter):
        async with ctx.channel.typing():
            f = open("names.csv", "w")
            f.write("Author_ID,Author_Name,Date,Roles\n")

            # Put all members in a dict with server join date as the value.
            server_members = {}
            for user in ctx.guild.members:
                server_members.update({user.id: user.joined_at})

            # Grab a lot of messages to search though.
            for channel in channel_ids:
                fetchMessage = await channel.history(limit=120000).flatten()
                if fetchMessage is None:
                    continue

                # When the message is newer than the previous value, update with the newest value.
                for message in fetchMessage:
                    if message.author.id not in server_members:
                        continue
                    if message.created_at > server_members[message.author.id]:
                        server_members.update({message.author.id: message.created_at})

            # Convet all the IDs to member objects to fill out data easier.
            for ID in server_members:
                member = ctx.guild.get_member(ID)

                role = ""
                for x in member.roles[1:]:
                    role += f"{x.id},"
                try:
                    f.write(f"{member.id},{member},{server_members[ID]},{role}\n")
                except UnicodeEncodeError:
                    f.write(f"{member.id},,{server_members[ID]},{role}\n")
            f.close()
            await ctx.reply("Done!")

    @commands.is_owner()
    @commands.command()
    async def lastContrib(
        self, ctx, channel: commands.TextChannelConverter, *contributors: discord.Member
    ):
        async with ctx.channel.typing():
            f = open("namesContrib.csv", "w")
            f.write("Author_ID,Author_Name,Date\n")

            # Put all members in a dict with server join date as the value.
            server_members = {}
            for user in contributors:
                server_members.update({user.id: "NULL"})

            # Grab a lot of messages to search though.
            fetchMessage = await channel.history(limit=400000).flatten()

            # When the message is newer than the previous value, update with the newest value.
            for message in fetchMessage:
                if message.author.id not in server_members:
                    continue
                if (
                    server_members[message.author.id] == "NULL"
                    or message.created_at > server_members[message.author.id]
                ):
                    server_members.update({message.author.id: message.created_at})

            # Convet all the IDs to member objects to fill out data easier.
            for ID in server_members:
                member = ctx.guild.get_member(ID)

                try:
                    f.write(f"{member.id},{member},{server_members[ID]}\n")
                except UnicodeEncodeError:
                    f.write(f"{member.id},,{server_members[ID]}\n")
            f.close()
            await ctx.reply("Done!")

    @commands.is_owner()
    @commands.bot_has_permissions(read_message_history=True, kick_members=True)
    @commands.command()
    async def purge(self, ctx: commands.context, *members: discord.Member):
        for member in members:
            try:
                await member.kick(reason="Inactivity")
            except Exception as e:
                await ctx.send(
                    f"Member {member.mention} - {member.id} Failed to kick\n{e}"
                )
                continue
        await ctx.send(f"Done!\n Kicked {len(members)} members for inactivity.")


def setup(bot):
    bot.add_cog(PlayerInfo(bot))
    log.info("Cog loaded: PlayerInfo")
