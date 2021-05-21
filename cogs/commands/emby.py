import logging

import discord
from discord.ext import commands
import requests

import constants
from tools import embeds
from tools.pagination import LinePaginator
from tools.record import record_usage

log = logging.getLogger(__name__)

EMBY_API_KEY = constants.Emby.api_key

PARAMS = (
    ('api_key', EMBY_API_KEY),
)
BASEURL = constants.Emby.address + '/emby/'
#BASEURL = 'https://emby.anichiraku.ru:443/emby/'
'''
EMBY_USER_POLICY = {
    "IsAdministrator": "false",
    "IsHidden": "true",
    "IsHiddenRemotely": "true",
    "IsDisabled": "false",
    "EnableRemoteControlOfOtherUsers": "false",
    "EnableSharedDeviceControl": "false",
    "EnableRemoteAccess": "true",
    "EnableLiveTvManagement": "false",
    "EnableLiveTvAccess": "false",
    "EnablePlaybackRemuxing": "true",
    "EnableContentDeletion": "false",
    "EnableContentDownloading": "true",
    "EnableSyncTranscoding": "false",
    "EnableSubtitleManagement": "false",
    "EnableMediaConversion": "false",
    "EnableAllDevices": "true",
    "EnableAllChannels": "true",
    "EnablePublicSharing": "false",
    "InvalidLoginAttemptCount": 5,
    "EnableMediaPlayback": "true",
    "SimultaneousStreamLimit": 1,
}'''
EMBY_USER_POLICY = constants.Emby.policy

# TODO implement logging

def send_request(method: str, path: str, headers: dict, data: str = '', params: tuple = PARAMS):
    """
    # Sends a GET or POST request to Emby anichiraku server.

    method: str `GET` or `POST` or `DELETE`\n
    path: what comes after the base url of emby server. ``ie emby.com/emby/PATH``
    header

    """
    log.info(
        f"EMBY, send_request: {method=}, {BASEURL + path=}, {headers=}, {data=}, {params=}")

    if method.lower() == 'post':
        response = requests.post(BASEURL + path, headers=headers,
                                 params=params, data=data, timeout=5)
    elif method.lower() == 'get':
        response = requests.get(BASEURL + path, headers=headers,
                                params=params, data=data, timeout=5)
    elif method.lower() == 'delete':
        response = requests.delete(
            BASEURL + path, headers=headers, params=params, data=data, timeout=5)

    error_list = {
        400: "Bad Request. Server cannot process request.",
        401: "Unauthorized. Client needs to authenticate.",
        403: "Forbidden. No permission for the requested operation.",
        404: "Resource not found or unavailable."
    }

    if response.status_code in error_list:
        log.error(
            f"EMBY, send_request: {response.status_code=}: {error_list[response.status_code]}")
        raise Exception(
            f"{response.status_code=}: {error_list[response.status_code]}")
    elif response.status_code >= 500:
        log.error(
            f"EMBY, send_request: {response.status_code=}: {error_list[response.status_code]}")
        raise Exception(f"SERVER ERROR {response.status_code=}: {response.reason=}")
    elif response.status_code >= 204:
        return # nothing, empty response
    else:
        log.debug(f"Everything seems OK :{response.status_code=}")
    log.debug(f"EMBY, send_request: {response.json()=}")
    return response.json()


class Emby(commands.Cog):
    """Emby"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.is_owner()
    @commands.before_invoke(record_usage)
    async def emby(self, ctx):
        if ctx.invoked_subcommand is None:
            # Send the help command for this group
            await ctx.send_help(ctx.command)

    @emby.command(name='adduser')
    @commands.is_owner()
    async def add_user(self, ctx, member: discord.Member):
        """Add a new user in Emby"""
        
        path = "Users/New"
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = f'{{"Name":"{member.name}"}}'
        # response = requests.post(BASEURL + path, headers=headers, params=PARAMS, data=data)
        response = send_request("post", path, headers, data)
        await ctx.send(f"{response}\n{data}")
    
    @emby.command(name='restart')
    @commands.is_owner()
    async def restart(self, ctx):
        """Restart Emby"""
        
        path = "System/Restart"
        headers = {"accept": "*/*"}
        # response = requests.post(BASEURL + path, headers=headers, params=PARAMS)
        response = send_request(method="post", path=path, headers=headers)
        await ctx.send(response)

    @emby.command(name='users', aliases=['list_users', 'listusers'])
    @commands.is_owner()
    async def list_users(self, ctx):
        """Lists all users and their ID"""
        
        path = "Users"
        headers = {
            'accept': 'application/json'
        }
        response = send_request(method="get", path=path, headers=headers)
        users = []
        for page in response:
            users.append(f"**{page['Name']}**: ``{page['Id']}``")
        log.debug(users)

        embed = embeds.make_embed(ctx=ctx, title="List Users", image_url="https://emby.media/resources/logowhite_1881.png")

        await LinePaginator.paginate([line for line in users], ctx, embed, restrict_to_user=ctx.author)
    
    @emby.command(name='user')
    @commands.is_owner()
    async def user(self, ctx, id:str):
        """Lists all users and their ID"""
        
        path = "Users"
        headers = {
            'accept': 'application/json'
        }
        response = send_request(method="get", path=path, headers=headers)
        users = []
        for page in response:
            users.append(f"**{page['Name']}**: ``{page['Id']}``")
        log.debug(users)

        embed = embeds.make_embed(ctx=ctx, title="List Users", image_url="https://emby.media/resources/logowhite_1881.png")

        await LinePaginator.paginate([line for line in users], ctx, embed)

    @emby.command(name='default')
    @commands.is_owner()
    async def default(self, ctx, Id:str):
        """Turns account into default settings"""
        
        path = f"Users/{Id}/Policy"
        headers = {
            'accept': '*/*',
            'Content-Type': 'application/json',
        }
        response = send_request(method="post", path=path, headers=headers, data=EMBY_USER_POLICY)

        log.debug(response.json())

    @emby.command(name='delete')
    @commands.is_owner()
    async def delete(self, ctx, Id:str):
        """Turns account into default settings"""
        
        path = f"Users/{Id}"
        headers = {
            'accept': '*/*',
        }
        response = send_request(method="delete", path=path, headers=headers)

        log.debug(response.json())

def setup(bot):
    bot.add_cog(Emby(bot))
    log.info("Cog loaded: emby")
