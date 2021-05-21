import logging
import random
import asyncio
import time

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context, BucketType

from tools import embeds, record, subby_api
import constants

log = logging.getLogger(__name__)

class Chance(Cog):
    """ Chance """

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(
        embed_links=True,
        read_message_history=True)
    @commands.command(name='roll')
    async def roll(self, ctx: Context, number_of_dice: int = 1, number_of_sides: int = 6):
        """Simulates rolling dice. <number_of_dice> <number_of_sides>"""

        number_of_dice = int(number_of_dice)
        number_of_sides = int(number_of_sides)

        if number_of_dice > 500:
            await embeds.error_message(ctx=ctx, description="Too many dice, try again in smaller batches.")
            return
        dice = [
            int(random.choice(range(1, number_of_sides + 1)))
            for _ in range(number_of_dice)
        ]
        embed = embeds.make_embed(ctx=ctx, description=(', '.join(str(x)
                                                        for x in dice)), title='Rolling Results')
        if number_of_dice > 1:
            embed.set_footer(text=f"Total sum: {sum(dice)}")
        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)    
    @commands.bot_has_permissions(
        embed_links=True,
        read_message_history=True)
    @commands.command(name='flip')
    async def flip(self, ctx: Context):
        """Simulates flipping a coin."""

        coin = [
            str(random.choice(['Heads', 'Tails']))
        ]

        embed = embeds.make_embed(ctx=ctx, description=coin[0], title='Coin Flip Results')
        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(
        manage_messages=True, 
        add_reactions=True,
        embed_links=True,
        external_emojis=True,
        use_external_emojis=True,
        read_message_history=True)
    @commands.guild_only()
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.max_concurrency(number=5, per=BucketType.default, wait=False)
    @commands.command(name='cups', aliases=['cup'])
    async def cups(self, ctx: Context, bet: int = 10):
        """
        There are 3 cups and only one has the prize, you have to guess which one has it
        """
        start_bet = bet
        if bet < 1:
            await embeds.error_message(ctx=ctx, description="Bet must be higher or equal to 1")
            return

        if (bal := subby_api.get_balance(ctx.author.id)) < bet:
            await embeds.error_message(ctx=ctx, description=f"You can\'t bet more than you have\nYour balance: {bal}")
            return

        CUP_EMOJI = constants.Emojis.cup             # [:cup:]
        COIN_EMOJI = constants.Emojis.coin           # [:coin:]
        ONE_EMOJI = constants.Emojis.number_one      # [:one:]
        TWO_EMOJI = constants.Emojis.number_two      # [:two:]
        THREE_EMOJI = constants.Emojis.number_three  # [:three:]
        DELETE_EMOJI = constants.Emojis.trashcan     # [:trashcan:]
        RAMEN_EMOJI = constants.Emojis.ramen         # [:ramen:]
        CROSS_EMOJI = constants.Emojis.cross_mark    # [:x:]

        def check(reaction, user) -> bool:
            """Checks if reaction is from author & is applicable to cup"""

            # Checking if user who used a reaction, was the same user who issued the command
            author_check = user == ctx.author
            # Checking the reaction was to the same message as the slot machine embed
            message_check = reaction.message.id == message.id
            # Checking if the reaction emoji is applicable to the slot machine commands
            reaction_check = str(reaction.emoji) in [
                ONE_EMOJI, TWO_EMOJI, THREE_EMOJI, RAMEN_EMOJI]

            if x := (author_check and message_check and reaction_check):
                # logging the action in case something breaks in the future
                log.trace(
                    f"{ctx.author=} reacted with {reaction.emoji=} in cups")
            return x

        async def default_embed(message: discord.Message, bet: int):
            embed = embeds.make_embed(ctx=ctx, title="Cups",
                                description="Where's the coin? :coin:")
            embed.add_field(
                name=f"{CUP_EMOJI} {CUP_EMOJI} {CUP_EMOJI}", value='​')
            embed.set_footer(
                text=f"Bet: {bet}\nChoices: {ONE_EMOJI} {TWO_EMOJI} {THREE_EMOJI}")
            if message is None:
                return await ctx.reply(embed=embed)
            else:
                await message.edit(embed=embed)

        def check_win(choice: int, elements: list) -> bool:
            return elements[choice - 1] == COIN_EMOJI

        async def spin(bet: int, choice: int) -> int:

            elements = random.choices(choices_config)[
                0]  # picking random option
            log.debug(f"{ctx.author}, options: {elements}")

            if check_win(choice, elements):
                log.trace(
                    f"{ctx.author=} wins in cups with {choice=} {elements=}")
                bet *= 2
                embed = embeds.make_embed(ctx=ctx, title="Cups",
                                    description="**WOOOW!** YOU WON!")
                embed.add_field(name=' '.join(elements),
                                value=f"You won {bet} ramen!")
            else:
                log.trace(
                    f"{ctx.author=} looses it all with {choice=} {elements=}")
                embed = embeds.make_embed(ctx=ctx, title="Cups",
                                    description="Better luck next time")
                embed.add_field(name=(' '.join(elements)),
                                value=f"You lost {bet} ramen.")
                bet = 0

            embed.set_footer(
                text=f"Risking: {bet} 🍜\nChoices: {ONE_EMOJI} {TWO_EMOJI} {THREE_EMOJI}")
            log.trace("cups, Sending embed")
            await message.edit(embed=embed)
            if bet != 0:
                time.sleep(2)
                await default_embed(message, bet)
            return bet

        async def cash_out(message: discord.Message, bet: int, bal: int):
            await message.clear_reactions()
            log.debug(f"clearing reactions")

            if bet != 0:
                emb = embeds.make_embed(ctx=ctx, color='green', title = "Cups",
                            description=f"Awarded {bet} :ramen:")
                subby_api.add_balance(ctx.author.id, bet, True)
                await message.edit(embed=emb)
                if bet > start_bet:
                    subby_api.record_ledger(ctx.author.id, ctx.me.id, bet, "Cups game")
                return
            else:
                subby_api.record_ledger(ctx.author.id, ctx.me.id, start_bet*-1, "Cups game")
                pass

        choices_config = [[COIN_EMOJI,  CROSS_EMOJI, CROSS_EMOJI],
                          [CROSS_EMOJI, COIN_EMOJI,  CROSS_EMOJI],
                          [CROSS_EMOJI, CROSS_EMOJI, COIN_EMOJI]]

        # Calling Subby API to get ramen amount

        bal = subby_api.subtract_balance(ctx.author.id, bet, True)

        message = await default_embed(None, bet)
        # getting the message object for editing and reacting

        # first adding reactions
        for emoji in [ONE_EMOJI, TWO_EMOJI, THREE_EMOJI, RAMEN_EMOJI]:
            await message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this example

                if str(reaction.emoji) == ONE_EMOJI and bet > 0:
                    bet = await spin(bet, choice=1)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == TWO_EMOJI and bet > 0:
                    bet = await spin(bet, choice=2)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == THREE_EMOJI and bet > 0:
                    bet = await spin(bet, choice=3)
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == RAMEN_EMOJI:
                    await cash_out(message=message, bet=bet, bal=bal)
                    return

                else:
                    await message.remove_reaction(reaction, user)

                if bet == 0:
                    await cash_out(message=message, bet=bet, bal=bal)
                    return

            except asyncio.TimeoutError:  # ending the loop if user doesn't react after x seconds
                await cash_out(message=message, bet=bet, bal=bal)
                return

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(
        manage_messages=True, 
        add_reactions=True,
        embed_links=True,
        external_emojis=True,
        use_external_emojis=True,
        read_message_history=True)
    @commands.guild_only()
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.max_concurrency(number=4, per=BucketType.default, wait=False)
    @commands.command(name='connect4', aliases=['4', 'connect'])
    async def connect(self, ctx: Context, bet: int = 0):
        """
        Connect four checkers in a row, pillar, or diaginal first to win.
        """
        # setting global emoji's that will be used in the program
        ONE_EMOJI = constants.Emojis.number_one
        TWO_EMOJI = constants.Emojis.number_two
        THREE_EMOJI = constants.Emojis.number_three
        FOUR_EMOJI = constants.Emojis.number_four
        FIVE_EMOJI = constants.Emojis.number_five
        SIX_EMOJI = constants.Emojis.number_six
        SEVEN_EMOJI = constants.Emojis.number_seven
        RED_CIRCLE = constants.Emojis.red_circle
        YELLOW_CIRCLE = constants.Emojis.yellow_circle
        BLACK_CIRCLE = constants.Emojis.black_circle
        REACTIONS = [ONE_EMOJI, TWO_EMOJI, THREE_EMOJI,
                     FOUR_EMOJI, FIVE_EMOJI, SIX_EMOJI, SEVEN_EMOJI]
        BOTTOM = f":black_large_square:{ONE_EMOJI}{TWO_EMOJI}{THREE_EMOJI}{FOUR_EMOJI}{FIVE_EMOJI}{SIX_EMOJI}{SEVEN_EMOJI}"

        if bet and bet > subby_api.get_balance(ctx.author.id):
            await embeds.error_message(ctx=ctx, description="You do not have enough ramen to bet that much")
            return
        subby_api.subtract_balance(ctx.author.id, bet)

        '''Need to find another player to play against. Polling the server'''
        embed = embeds.make_embed(ctx=ctx, title=f"{ctx.author.display_name} wants to play Connect Four",
                            description="Press play to accept the challenge")
        embed.set_author(icon_url=ctx.author.avatar_url, name=str(ctx.author))
        embed.set_footer(text=f"Bet Amount: **{bet:,}**")
        message = await ctx.reply(embed=embed)

        await message.add_reaction('▶️')
        await message.add_reaction('🛑')

        def check_start(reaction, user) -> bool:
            """Checks if reaction is from author & is applicable to command"""

            # Checking if user who used a reaction, was the same user who issued the command
            author_check = not user.bot
            # Checking the reaction was to the same message as the command embed
            message_check = reaction.message.id == message.id
            # Checking if the reaction emoji is applicable to the command embed
            reaction_check = str(reaction.emoji) in ["▶️", "🛑"]

            if x := (author_check and message_check and reaction_check):
                # logging the action in case something breaks in the future
                log.trace(
                    f"{user.name=} accepted to play connect 4 {reaction.emoji=}")
            return x

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check_start)
                # waiting for a reaction to be added - times out after x seconds, 60 in this example

                if bet == 0 or bet < (bal := subby_api.get_balance(user.id)) and str(reaction.emoji) == '▶️':
                    subby_api.subtract_balance(user.id, bet)
                    players = {RED_CIRCLE: ctx.author,
                               YELLOW_CIRCLE: user}
                    await message.clear_reactions()
                    break
                elif str(reaction.emoji) == '🛑' and ctx.author == user:
                    subby_api.add_balance(ctx.author.id, bet)
                    try:
                        await message.delete()
                    except discord.NotFound:
                        pass
                    return
                elif bet > bal:
                    await embeds.warning_message(ctx, f"Sorry, {user.display_name}, you do not have enough ramen to join in on the bet.", False)
                else:
                    await message.remove_reaction(reaction, user)
            # removes reactions if the user tries to go forward on the last page or
            # backwards on the first page
            except asyncio.TimeoutError:
                subby_api.add_balance(ctx.author.id, bet)
                try:
                    await message.clear_reactions()
                except discord.NotFound:
                    await embeds.warning_message(ctx, "Request message was deleted unexpectedly or can no longer be found\n"
                                                f"{ctx.author.mention}'s money has been returned")
                    log.warning(
                        msg="Connect4, message to play was deleted unexpectedly")
                return
                # ending the loop if user doesn't react after x seconds

        '''Setting up the game'''

        def check_win(board: list, player) -> bool:
            # Check horizontal locations for win
            for column in range(6-3):
                for row in range(7):
                    try:
                        if board[row][column] == player and board[row][column+1] == player and board[row][column+2] == player and board[row][column+3] == player:
                            return True
                    except IndexError:
                        continue

            # Check vertical locations for win
            for column in range(6):
                for row in range(7-3):
                    try:
                        if board[row][column] == player and board[row+1][column] == player and board[row+2][column] == player and board[row+3][column] == player:
                            return True
                    except IndexError:
                        continue

            # Check positively sloped diagonals
            for column in range(6-3):
                for row in range(7-3):
                    try:
                        if board[row][column] == player and board[row+1][column+1] == player and board[row+2][column+2] == player and board[row+3][column+3] == player:
                            return True
                    except IndexError:
                        continue

            # Check negatively sloped diagonals
            for column in range(6-3):
                for row in range(3, 7):
                    try:
                        if board[row][column] == player and board[row-1][column+1] == player and board[row-2][column+2] == player and board[row-3][column+3] == player:
                            return True
                    except IndexError:
                        continue
            return False

        def column(a: list, column: int) -> list:
            result = ""
            for num in range(7):
                try:
                    result += a[num][column]
                except IndexError:
                    result += BLACK_CIRCLE
            return result

        async def print_board(message: discord.Message = None, board: list = [[], [], [], [], [], [], []], turn=YELLOW_CIRCLE, win: bool = False) -> (tuple):
            if turn == YELLOW_CIRCLE and not win:  # This is to show who's turn it is by changing the color of the embed
                color = 0xff0000
            elif turn == RED_CIRCLE and not win:
                color = 0xffff00
            elif turn == YELLOW_CIRCLE:
                color = 0xffff00
            else:
                color = 0xff0000
            embed = discord.Embed(title="Connect Four",
                                  description=f":arrow_forward:{column(board, 5)}\n"
                                  f":arrow_forward:{column(board, 4)}\n"
                                  f":arrow_forward:{column(board, 3)}\n"
                                  f":arrow_forward:{column(board, 2)}\n"
                                  f":arrow_forward:{column(board, 1)}\n"
                                  f":arrow_forward:{column(board, 0)}\n"
                                  f"{BOTTOM}", colour=color)
            embed.set_thumbnail(
                url='https://image.winudf.com/v2/image1/YXMuYW5kcm9pZC5hcHBzLmNvbm5lY3Rmb3VyNl9pY29uXzE1Njk4MzEzODNfMDYz/icon.png?w=170&fakeurl=1')
            if bet:
                embed.set_footer(text=f"bet total: {bet*2:,}")

            if win:
                winner = players.pop(turn)
                loser = players.popitem()[1]

                await message.clear_reactions()
                embed.set_author(
                    icon_url=winner.avatar_url, name=f"{winner.display_name} is the WINNER")
                if bet:
                    embed.add_field(
                        name="WINNINGS", value=f"{bet:,} awarded to {winner.mention}\n"
                        f"{loser.mention} walks away in shame and with their pockets a little lighter")
                    subby_api.add_balance(winner.id, bet*2)
                    # the second player took forever to figure out
                    subby_api.record_ledger(loser.id, winner.id, bet, "Connect Four Game")
            elif (sum(len(row) for row in board)) == 42:
                # If this is true then the game is a tie.
                first = players.pop(turn)
                second = players.popitem()[1]

                await message.clear_reactions()
                embed.set_author(
                    icon_url=ctx.bot.user.avatar_url, name=f"The game is a draw")
                if bet:
                    embed.add_field(
                        name="There was no clear winner", value=f"bet has been refunded to {first.mention} and {second.mention}\n"
                        f"Good game")
                    subby_api.add_balance(first.id, bet)
                    subby_api.add_balance(second.id, bet)

            if turn == RED_CIRCLE and not win and players != {}:
                turn = YELLOW_CIRCLE
                embed.set_author(name=f"{players[turn].display_name}'s Turn",
                                 icon_url="https://www.iconsdb.com/icons/preview/yellow/circle-xxl.png")
            elif turn == YELLOW_CIRCLE and not win and players != {}:
                turn = RED_CIRCLE
                embed.set_author(name=f"{players[turn].display_name}'s Turn",
                                 icon_url="https://www.iconsdb.com/icons/preview/red/circle-xxl.png")

            await message.edit(embed=embed)
            return turn

        board: list = [[], [], [], [], [], [], []]
        turn = await print_board(message=message, board=board)

        for emoji in REACTIONS:
            await message.add_reaction(emoji)

        def check(reaction, user) -> bool:
            """Checks if reaction is from author & is applicable to command"""

            # Checking if user who used a reaction, was the same user who issued the command
            author_check = not user.bot and user == players[turn]
            # Checking the reaction was to the same message as the command embed
            message_check = reaction.message.id == message.id
            # Checking if the reaction emoji is applicable to the command embed
            reaction_check = str(reaction.emoji) in REACTIONS

            if x := (author_check and message_check and reaction_check):
                # logging the action in case something breaks in the future
                log.trace(
                    f"{user.name=} reacted with {reaction.emoji=} in connect 4")
            return x

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=90, check=check)
                # waiting for a reaction to be added - times out after x seconds, 120 in this example

                if str(reaction.emoji) == ONE_EMOJI and len(board[0]) < 6:
                    board[0].append(turn)
                    turn = await print_board(message=message, board=board, turn=turn, win=(win := check_win(board, turn)))
                    await message.remove_reaction(reaction, user)
                    if win:
                        await message.clear_reactions()
                        break

                elif str(reaction.emoji) == TWO_EMOJI and len(board[1]) < 6:
                    board[1].append(turn)
                    turn = await print_board(message=message, board=board, turn=turn, win=(win := check_win(board, turn)))
                    await message.remove_reaction(reaction, user)
                    if win:
                        await message.clear_reactions()
                        break

                elif str(reaction.emoji) == THREE_EMOJI and len(board[2]) < 6:
                    board[2].append(turn)
                    turn = await print_board(message=message, board=board, turn=turn, win=(win := check_win(board, turn)))
                    await message.remove_reaction(reaction, user)
                    if win:
                        await message.clear_reactions()
                        break

                elif str(reaction.emoji) == FOUR_EMOJI and len(board[3]) < 6:
                    board[3].append(turn)
                    turn = await print_board(message=message, board=board, turn=turn, win=(win := check_win(board, turn)))
                    await message.remove_reaction(reaction, user)
                    if win:
                        await message.clear_reactions()
                        break

                elif str(reaction.emoji) == FIVE_EMOJI and len(board[4]) < 6:
                    board[4].append(turn)
                    turn = await print_board(message=message, board=board, turn=turn, win=(win := check_win(board, turn)))
                    await message.remove_reaction(reaction, user)
                    if win:
                        await message.clear_reactions()
                        break

                elif str(reaction.emoji) == SIX_EMOJI and len(board[5]) < 6:
                    board[5].append(turn)
                    turn = await print_board(message=message, board=board, turn=turn, win=(win := check_win(board, turn)))
                    await message.remove_reaction(reaction, user)
                    if win:
                        await message.clear_reactions()
                        break

                elif str(reaction.emoji) == SEVEN_EMOJI and len(board[6]) < 6:
                    board[6].append(turn)
                    turn = await print_board(message=message, board=board, turn=turn, win=(win := check_win(board, turn)))
                    await message.remove_reaction(reaction, user)
                    if win:
                        await message.clear_reactions()
                        break

                else:
                    await message.remove_reaction(reaction, user)

                if (sum(len(row) for row in board)) == 42:
                    return
            
            except asyncio.TimeoutError:  # ending the loop if user doesn't react after x seconds
                if turn == RED_CIRCLE:
                    turn = YELLOW_CIRCLE
                else:
                    turn = RED_CIRCLE
                try:
                    await message.clear_reactions()
                    await print_board(message=message, board=board, turn=turn, win=True)
                except discord.NotFound:  # When the embed for the game has been removed. Refund players
                    await embeds.warning_message(ctx, "Game was deleted unexpectedly or can no longer be found\n"
                                                f"Bet has been refunded for players {players[RED_CIRCLE].mention} and {players[YELLOW_CIRCLE].mention}")
                    subby_api.add_balance(players[RED_CIRCLE].id, bet)
                    subby_api.add_balance(players[YELLOW_CIRCLE].id, bet)
                    log.warning(
                        "Connect4, message to play was deleted unexpectedly")
                break

    @commands.before_invoke(record.record_usage)
    @commands.bot_has_permissions(
        manage_messages=True, 
        add_reactions=True,
        embed_links=True,
        external_emojis=True,
        use_external_emojis=True,
        read_message_history=True)
    @commands.guild_only()
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.max_concurrency(number=2, per=BucketType.default, wait=False)
    @commands.command(name='slot', aliases=['slots', 'slot_machine', 'sm'])
    async def slot_machine(self, ctx: Context, credit: int = 10):
        """Simulates a slot machine"""

        if credit < 1:
            await embeds.error_message(ctx=ctx, description="credits must be higher or equal to 1")
            return

        if (bal := subby_api.get_balance(ctx.author.id)) < credit:
            await embeds.error_message(ctx=ctx, description=f"You do not have enough ramen to bet that much\nYour balance: {bal}")
            return
        
        subby_api.subtract_balance(ctx.author.id, credit, True)

        start_credit = credit

        SEVEN = constants.Emojis.number_seven
        BAR = constants.Emojis.bar
        MELLON = constants.Emojis.mellon
        BELL = constants.Emojis.bell
        PEACH = constants.Emojis.peach
        HONEY = constants.Emojis.honey
        CHERRY = constants.Emojis.cherry
        LEMON = constants.Emojis.lemon
        LEVER = constants.Emojis.lever
        CASH_OUT = constants.Emojis.cash_out
        BOMB = constants.Emojis.bomb
        ONE = constants.Emojis.number_one
        FIVE = constants.Emojis.number_five
        TEN = constants.Emojis.number_ten
        RAMEN = constants.Emojis.ramen

        reel1 = {SEVEN: 1, BAR: 4, MELLON: 2, BELL: 1,PEACH: 9, HONEY: 9, CHERRY: 9, LEMON: 5}
        reel2 = {SEVEN: 1, BAR: 2, MELLON: 2, BELL: 8,PEACH: 3, HONEY: 13, CHERRY: 4, LEMON: 0}
        reel3 = {SEVEN: 1, BAR: 1, MELLON: 8, BELL: 8,PEACH: 3, HONEY: 2, CHERRY: 0, LEMON: 10}

        def check(reaction:str, user) -> bool:
            """Checks if reaction is from author & is applicable to slot machine"""

            # Checking if user who used a reaction, was the same user who issued the command
            author_check = user == ctx.author
            # Checking the reaction was to the same message as the slot machine embed
            message_check = reaction.message.id == message.id
            # Checking if the reaction emoji is applicable to the slot machine commands
            reaction_check = str(reaction.emoji) in [
                LEVER, ONE, FIVE, TEN, CASH_OUT, BOMB]

            if x := (author_check and message_check and reaction_check):
                # logging the action in case something breaks in the future
                log.trace(
                    f"{ctx.author} reacted with {reaction.emoji=} in slot machine")
            return x

        def take_random(reel:dict) -> str:
            return random.choices(list(reel.keys()), weights=list(reel.values()), k=1)[0]

        def check_win(elements: list) -> int:
            points = 0
            element_dict = {}
            for i in elements:  # converting list into dict for ease of comparing
                if i in element_dict:
                    element_dict[i] += 1
                else:
                    element_dict[i] = 1

            if CHERRY in element_dict:
                if element_dict[CHERRY] == 1:
                    points = 2
                else:
                    points = 5
            if HONEY in element_dict:
                if element_dict[HONEY] == 3 or element_dict[HONEY] == 2 and BAR in element_dict:
                    points = 10
            if PEACH in element_dict:
                if element_dict[PEACH] == 3 or element_dict[PEACH] == 2 and BAR in element_dict:
                    points = 14
            if BELL in element_dict:
                if element_dict[BELL] == 3 or element_dict[BELL] == 2 and BAR in element_dict:
                    points = 18
            if MELLON in element_dict:
                if element_dict[MELLON] == 3:
                    points = 100
            if BAR in element_dict:
                if element_dict[BAR] == 3:
                    points = 125
            if SEVEN in element_dict:
                if element_dict[SEVEN] == 3:
                    points = 200
            log.debug(f"{ctx.author=} won {points * bet} in slots!")
            return points * bet

        async def spin(credit: int) -> int:
            # this for loop isn't needed, it just show some flare like the icons are shuffling
            for _ in range(3):
                elements = [
                    take_random(reel1), 
                    take_random(reel2), 
                    take_random(reel3)]  # picking three items

                embed = embeds.make_embed(ctx=ctx, 
                                    title="Slot Machine", 
                                    description=' '.join(elements),
                                    image_url="https://i.imgur.com/SjYv07F.png")

                if _ == 2 and (score := check_win(elements)):
                    credit += score
                    embed = embeds.make_embed(ctx=ctx, 
                                        title="Slot Machine\n"
                                              "🎊🎊WINNER🎊🎊",
                                        description='  '.join(elements) + 
                                                    f'\nYou won {score:,} credits!',
                                        image_url="https://i.imgur.com/SjYv07F.png")
                    log.debug(f"{ctx.author.mention=}, won {score=} with {elements=}")

                log.trace(f"{ctx.author=}, results from spin: {elements=}")

                # Must use actual emoji's here because discord sucks with emoji's in footer
                # Credit: 10  Bet: 3
                # 📍: Spin • 💸: Cash Out
                # 1️⃣, 5️⃣, 🔟: bet amount
                embed.set_footer(text="📍: Spin • 💸: Cash Out\n"
                                      "1️⃣, 5️⃣, 🔟: bet amount")
                embed.add_field(name="Credits", value=f"{credit:,} {RAMEN}", inline=True)
                embed.add_field(name="Bet", value=f"{bet:,} {RAMEN}", inline=True)
                await message.edit(embed=embed)
                time.sleep(0.5)  # sleep because of rate limit

            return credit

        async def change_bet(send=False):
            elements= [SEVEN, SEVEN, SEVEN]
            embed = embeds.make_embed(ctx=ctx, 
                                title="Slot Machine", 
                                description='\t'.join(elements),
                                image_url="https://i.imgur.com/SjYv07F.png")
            log.trace(f"{ctx.author=}, changed bet: {bet=}")
            embed.set_footer(text="📍: Spin • 💸: Cash Out\n"
                                  "1️⃣, 5️⃣, 🔟: bet amount")
            embed.add_field(name="Credits", value=f"{credit:,} {RAMEN}", inline=True)
            embed.add_field(name="Bet", value=f"{bet:,} {RAMEN}", inline=True)
            
            if send:
                return await ctx.reply(embed=embed)
            return await message.edit(embed=embed)

        async def cash_out(credit):
            
            log.debug(f"slot_machine, cash_out: clearing reactions")
            await message.clear_reactions()

            embed = embeds.make_embed(ctx=ctx, title="Cashing Out",
                                description=f"**Credits**: \t**``{credit:,} {RAMEN}``**\n"
                                            f"**Net**: \t**``{credit-start_credit:,}{RAMEN}``**\n"
                                            f"**Bank**: \t**``{subby_api.add_balance(ctx.author.id, credit, True):,} {RAMEN}``**",
                                image_url="https://i.imgur.com/SjYv07F.png")

            log.trace("slot_machine, cash_out: issueing ledger")
            subby_api.record_ledger(ctx.me.id, ctx.author.id, credit-start_credit, "Slot Machine")

            log.trace("slot_machine, cash_out: sending message")
            await message.edit(embed=embed)
        
        bet = 1
        message = await change_bet(True)

        # first adding reactions
        for react in [LEVER, ONE, FIVE, TEN, CASH_OUT]:
            await message.add_reaction(react)

        while True:
            try:
                # This makes sure nobody except the command sender can interact with the "menu"
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                # waiting for a reaction to be added - times out after x seconds, 60 in this example
                
                await message.remove_reaction(reaction, user)
 
                if str(reaction.emoji) == LEVER: # 📍
                    if credit >= bet:
                        credit -= bet
                        credit = await spin(credit)

                    else:
                        pass
                elif str(reaction.emoji) == ONE: # 1️⃣
                    bet = 1
                    await change_bet()
                elif str(reaction.emoji) == FIVE: # 5️⃣
                    bet = 5
                    await change_bet()
                elif str(reaction.emoji) == TEN: # 🔟
                    bet = 10
                    await change_bet()

                elif str(reaction.emoji) == CASH_OUT: # 💸
                    await cash_out(credit)
                    break

                elif str(reaction.emoji) == BOMB: # 💣
                    bal_left = subby_api.get_balance(ctx.author.id)
                    subby_api.subtract_balance(ctx.author.id, bal_left, True)
                    credit += bal_left
                    bet = credit

                    await change_bet()
                    log.warning(
                        f"{ctx.author.mention=} has discovered and used the slot machine ALL IN easter egg")

                if credit == 0:
                    await cash_out(credit)
                    break

            except asyncio.TimeoutError:
                await cash_out(credit)
                break
            except Exception as exception:
                await embeds.error_message(ctx=ctx, description=f"An error occurred, balance refunded\n {exception=}")
                subby_api.add_balance(ctx.author.id, credit, True)

            # ending the loop if user doesn't react after x seconds


def setup(bot: Bot) -> None:
    """ Load the Chance cog. """
    bot.add_cog(Chance(bot))
    log.info("Cog loaded: Chance")
