import asyncio
import functools
import logging
import math

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context, BucketType
import requests
import dataset

from tools import embeds, database, record
from tools.bank import Bank
import constants
from tools.pagination import LinePaginator

log = logging.getLogger(__name__)

# TODO implement logging

FINNHUB_URL = constants.Finnhub.url
FINNHUB_TOKEN = constants.Finnhub.token

BROKERAGE_FEE_PERCENTAGE = 0.04


class Share:
    """This class is currently not in use. A future update will move towards object-oriented. Here be dragons."""

    def __init__(self, name: str):
        self.name = name.upper()
        self.value = self.__value()

    def __str__(self):
        """Return the Stock Ticker"""
        return self.name.upper()

    def __value(self) -> float:
        """Current Value of the stock"""
        return round((self.__stock_price()["c"] * 100), 6)

    def __stock_price(self) -> list:
        """Call API for current stock price"""
        stock = requests.utils.quote(self.name)
        try:
            r = requests.get(
                f"{FINNHUB_URL}/api/v1/quote?symbol={stock}&token={FINNHUB_TOKEN}"
            )
            return r.json()
        except Exception as e:
            log.error(e)

    def stock_query1(self) -> list:
        """Call API for Searching a stock"""
        query = requests.utils.quote(self.name)
        try:
            r = requests.get(
                f"{FINNHUB_URL}/api/v1/search?q={query}&token={FINNHUB_TOKEN}"
            )
            return r.json()
        except Exception as e:
            log.error(e)


class Stonks(Cog):
    """Stonks"""

    def __init__(self, bot: Bot):
        self.bot = bot

    def stock_price(self, stock: str) -> list:
        stock = requests.utils.quote(stock)
        try:
            r = requests.get(
                f"{FINNHUB_URL}/api/v1/quote?symbol={stock}&token={FINNHUB_TOKEN}"
            )
            return r.json()
        except Exception as e:
            log.error(e)

    @functools.lru_cache(maxsize=None)
    def stock_query(self, query: str) -> list:
        query = requests.utils.quote(query)
        try:
            r = requests.get(
                f"{FINNHUB_URL}/api/v1/search?q={query}&token={FINNHUB_TOKEN}"
            )
            return r.json()
        except Exception as e:
            log.error(e)

    @functools.lru_cache(maxsize=None)
    def get_symbols(self, mic: str) -> list:
        # download a all the symbols from a particular exchange identified by it's mic
        # https://en.wikipedia.org/wiki/Market_Identifier_Code
        r = requests.get(
            f"https://finnhub.io/api/v1/stock/symbol?exchange=US&mic={mic}&token={FINNHUB_TOKEN}"
        )

        # we only want the actual symbol and nothing else from the data
        return [x["symbol"] for x in r.json()]

    @functools.lru_cache(maxsize=None)
    def get_crypto_symbols(self, exchange: str) -> list:
        # Download a all the symbols from a particular crypto exchange.
        r = requests.get(
            f"https://finnhub.io/api/v1/crypto/symbol?exchange={exchange}&token={FINNHUB_TOKEN}"
        )

        # we only want the actual symbol and nothing else from the data
        return [x["symbol"] for x in r.json()]

    def can_trade(self, symbol: str) -> bool:
        # We want to know if this is a stock or something else like crypto.
        stock_type = self.stock_query(symbol)["result"]
        stock = list(filter(lambda x: x["symbol"] == symbol, stock_type))

        if not stock:
            all_symbols = []
            for exchange in [
                "KRAKEN",
                "ZB",
                "BITMEX",
                "KUCOIN",
                "POLONIEX",
                "HITBTC",
                "OKEX",
                "BITFINEX",
                "GEMINI",
                "BITTREX",
                "BINANCE",
                "COINBASE",
                "HUOBI",
                "FXPIG",
            ]:
                all_symbols.append(
                    [
                        item.partition(":")[2]
                        for item in self.get_crypto_symbols(exchange.lower())
                    ]
                )

            # Check to see if our crypto is in the list of symbols we pulled from the exchanges.
            return symbol in all_symbols

        if stock[0]["type"] == "Common Stock":
            symbol_set_1 = self.get_symbols("XNYS")  # NYSE
            symbol_set_2 = self.get_symbols("XNAS")  # All NASDAQ Exchanges
            symbol_set_3 = self.get_symbols("XASE")  # AMEX
            symbol_set_4 = self.get_symbols("ARCX")  # NYSE Arca

            all_symbols = symbol_set_1 + symbol_set_2 + symbol_set_3 + symbol_set_4

            # Check to see if our symbol is in the list of symbols we pulled from the exchanges.
            return symbol in all_symbols

        # Return true if not a stock
        return True

    @commands.before_invoke(record.record_usage)
    @commands.cooldown(rate=20, per=60, type=BucketType.default)
    @commands.cooldown(rate=8, per=600, type=BucketType.user)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=True)
    @commands.command(
        name="stocks", aliases=["stock", "stonk", "stonks", "stinks", "stink"]
    )
    async def stock_market(self, ctx: Context, *stonks: str):
        """Viewer of the active USA stock market and its value in coin"""

        if stonks == ():
            await ctx.send_help(ctx.command)
            return

        stonk_dict = {}
        message = []

        async with ctx.channel.typing():
            for stonk in stonks[:5]:
                stonk_dict[stonk.upper()] = self.stock_price(stonk.upper())

        embed = embeds.make_embed(
            ctx=ctx,
            title="STONKS:",
            description="Trading for :coin:\n $0.01 = 1 :coin:",
            image_url="https://cdn.discordapp.com/attachments/653793817299910689/766603822579580938/pepedeal.png",
        )
        for stonk in stonk_dict:
            ticker = stonk_dict.get(stonk)
            if "error" in ticker:
                embed.add_field(name=stonk, value=ticker["error"], inline=False)
                continue
            if not self.can_trade(stonk.upper()):
                stonk += " - Not Tradeable"
            if ticker["t"] != 0:
                message = (
                    f"```py\n"
                    f"Price: {round(ticker['c'] * 100, 6):,}\n"
                    f"High:  {round((ticker['h']  - ticker['c']) * 100, 2):+,}\n"
                    f"Low:   {round((ticker['l']  - ticker['c']) * 100, 2):+,}\n"
                    f"Open:  {round((ticker['o']  - ticker['c']) * 100, 2):+,}\n"
                    f"Close: {round((ticker['pc'] - ticker['c']) * 100, 2):+,}```"
                    f"https://finance.yahoo.com/quote/{stonk}"
                )
            else:
                message = "No results, check your stock name"
            embed.add_field(name=stonk, value=message, inline=False)

        embed.set_footer(text=f"BROKERAGE FEE: {BROKERAGE_FEE_PERCENTAGE*100:.1f}%")
        await ctx.send(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.cooldown(rate=20, per=60, type=BucketType.default)
    @commands.cooldown(rate=4, per=600, type=BucketType.user)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(
        name="stock_buy", aliases=["stonk_buy", "stonks_buy", "stocks_buy"]
    )
    async def buy_stock(self, ctx: Context, stonk: str, number_of_stonks: int):
        """Invest in the stock market"""

        if not self.can_trade(stonk.upper()):
            await embeds.warning_message(
                ctx, "This stock is not listed on a tradeable exchange."
            )
            return

        stonk = (stonk.upper(), self.stock_price(stonk.upper()))

        if "error" in stonk[1]:
            embeds.error_embed(
                ctx, "An error occurred, please try again:\n" + stonk[1]["error"]
            )
            return

        if stonk[1]["t"] == 0:
            await embeds.warning_message(ctx, "No results, check your stock name!")
            return

        if int(stonk[1]["c"] * 100) < 1:
            await embeds.warning_message(
                ctx,
                "As your financial advisor, I can't allow you to buy stocks less than 1 :coin:",
            )
            return

        purchase_price = round(number_of_stonks * stonk[1]["c"] * 100, 6)

        if purchase_price > (bal := float(Bank(ctx.author))):
            await embeds.error_message(
                ctx=ctx,
                description="You do not have enough coin.\n"
                f"Amount needed: **`{round(purchase_price,2):,.2f}`** :coin:\n"
                f"Current balance: **`{bal:,}`**` :coin:",
            )
            return

        with dataset.connect(
            database.get_db(), engine_kwargs={"pool_recycle": 300}
        ) as db:
            try:
                Bank(ctx.author).subtract(
                    purchase_price,
                    f"Buying **{number_of_stonks:,}** shares of **{stonk[0]}**",
                )

                db["stonks"].insert(
                    dict(
                        author_id=ctx.author.id,
                        stonk=stonk[0],
                        amount=number_of_stonks,
                        investment_cost=(-1 * purchase_price),
                        timestamp=ctx.message.created_at,
                    )
                )
            except Exception as e:
                await embeds.error_message(
                    "An error occurred: notify <@396570271265325058>", ctx
                )
                log.error("something happend", exc_info=e)
                db.rollback()
                return

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Stock purchased: {stonk[0]}",
            description=f"Purchased **{number_of_stonks:,}** share(s) of {stonk[0]}\n"
            f"Costing **`{round(purchase_price,2):,.2f}`** :coin:",
            image_url="https://cdn.discordapp.com/attachments/653793817299910689/766603822579580938/pepedeal.png",
            color=constants.Colours.bright_green,
        )
        embed.set_footer(text=f"BROKERAGE FEE: {BROKERAGE_FEE_PERCENTAGE*100:.1f}%")
        await ctx.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.cooldown(rate=20, per=60, type=BucketType.default)
    @commands.cooldown(rate=4, per=600, type=BucketType.user)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(
        name="stock_sell", aliases=["stonk_sell", "stonks_sell", "stocks_sell"]
    )
    async def sell_stock(self, ctx: Context, stonk: str, number_of_stonks: int):
        """Disinvest in the stock market"""

        def check(m):
            return (
                m.content.lower() == "confirm"
                and m.channel == ctx.channel
                and m.author == ctx.author
            )

        stonk = (stonk.upper(), self.stock_price(stonk.upper()))

        if "error" in stonk[1]:
            embeds.error_embed(
                ctx, "An error occurred, please try again:\n" + stonk[1]["error"]
            )
            return

        if stonk[1]["t"] == 0:
            await embeds.warning_message(ctx, "No results, check your stock name")
            return

        sell_price = round(number_of_stonks * stonk[1]["c"] * 100, 6)

        with dataset.connect(
            database.get_db(), engine_kwargs={"pool_recycle": 300}
        ) as db:
            try:
                statement = f"""
                    SELECT stonk, Sum(amount) totalstonks
                    FROM stonks
                    WHERE author_id = {ctx.author.id} AND stonk = '{stonk[0]}'
                    GROUP BY stonk"""
                result = db.query(statement)

                for x in result:
                    result = x
                if result["totalstonks"] is None:
                    await embeds.warning_message(
                        ctx, f"You do not own any **`{stonk[0]}`** stock"
                    )
                    return

                if result["totalstonks"] < number_of_stonks:
                    await embeds.warning_message(
                        ctx,
                        f"You do not own enough **`{stonk[0]}`** stock.\n{result['totalstonks']:,} shares owned",
                    )
                    return

                fee = math.ceil((sell_price) * BROKERAGE_FEE_PERCENTAGE)

                rep = await ctx.reply(
                    embed=embeds.make_embed(
                        ctx=ctx,
                        title="Confirm sell",
                        description=f"Type **`Confirm`** to sell your **`{number_of_stonks}`** "
                        f"shares for **`{sell_price:,.2f}`** :coin:.\n"
                        f"The Brokerage fee is: **`{fee:,.0f}`** :coin:",
                    ),
                    delete_after=45,
                )

                try:
                    msg = await self.bot.wait_for("message", timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    await rep.reply("Sell timed out, canceled", delete_after=15)
                    return

                Bank(ctx.author).add(
                    sell_price - fee,
                    f"Selling **{number_of_stonks:,}** shares of **{stonk[0]}**",
                )

                db["stonks"].insert(
                    dict(
                        author_id=ctx.author.id,
                        stonk=stonk[0],
                        amount=(-1 * number_of_stonks),
                        investment_cost=(sell_price),
                        timestamp=ctx.message.created_at,
                    )
                )
            except Exception as e:
                await embeds.error_message(
                    "An error occurred: notify <@396570271265325058>", ctx
                )
                log.error("something happend", exc_info=e)
                db.rollback()
                return

        embed = embeds.make_embed(
            ctx=ctx,
            title=f"Stock Sold: {stonk[0]}",
            description=f"Sold **{number_of_stonks:,}** share(s) of {stonk[0]}\n"
            f"For **`{sell_price:.2f}`** :coin:",
            image_url="https://cdn.discordapp.com/attachments/653793817299910689/766603822579580938/pepedeal.png",
            color=constants.Colours.bright_green,
        )
        embed.set_footer(text=f"BROKERAGE FEE: {BROKERAGE_FEE_PERCENTAGE*100:.1f}%")
        await msg.reply(embed=embed)

    @commands.before_invoke(record.record_usage)
    @commands.cooldown(rate=5, per=60, type=BucketType.default)
    @commands.cooldown(rate=1, per=300, type=BucketType.user)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(name="portfolio", aliases=["port", "stock_list"])
    async def list_stock(self, ctx: Context, user: discord.User = None):
        """List All your stocks."""

        user = user or ctx.author

        embed = embeds.make_embed(
            ctx=ctx,
            title="Portfolio",
            image_url="https://compote.slate.com/images/926e5009-c10a-48fe-b90e-fa0760f82fcd.png"
            "?width=1200&rect=680x453&offset=0x30",
        )

        if user != ctx.author:
            embed.title = f"{user.name}'s Portfolio"

        with dataset.connect(
            database.get_db(), engine_kwargs={"pool_recycle": 300}
        ) as db:
            # Find all stock from user and combine like stock purchases.
            statement = statement = f"""
                SELECT stonk, Sum(amount) totalstonks
                FROM stonks
                WHERE author_id = {user.id}
                GROUP BY stonk"""
            result = db.query(statement)

        port = []
        investment = 0
        async with ctx.channel.typing():
            for count, x in enumerate(result):
                # have to sleep due to rate limits on API
                if 1 + count % 10 == 0:
                    asyncio.sleep(10)
                stonk = x["stonk"]
                stonk_amount = x["totalstonks"]
                # don't need to lookup any stocks that user doesn't have any of.
                if stonk_amount <= 0:
                    continue
                result = self.stock_price(x["stonk"])
                if "error" in result:
                    embeds.error_embed(
                        ctx, "An error occurred, please try again:\n" + result["error"]
                    )
                    return
                price = round(stonk_amount * result["c"] * 100, 6)
                investment += price
                port.append(
                    f"[{stonk}](https://finance.yahoo.com/quote/{stonk})\n"
                    f" Shares:**` {stonk_amount:>7,} `** Value:**` {price:>10,.0f}`**"
                )
        embed.title += f": {investment:,.0f} :coin:"
        embed.set_footer(text=f"BROKERAGE FEE: {BROKERAGE_FEE_PERCENTAGE*100:.1f}%")
        await LinePaginator.paginate(
            port, ctx, embed, max_size=2000, restrict_to_user=ctx.author
        )

    @commands.before_invoke(record.record_usage)
    @commands.cooldown(rate=1, per=300, type=BucketType.user)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(
        name="stock_history",
        aliases=["stonk_history", "stonks_history", "stocks_history"],
    )
    async def stock_history(self, ctx: Context, user: discord.User = None):
        """Displays Buy and Sell history of a user."""

        BUY = constants.Emojis.buy
        SELL = constants.Emojis.sell

        user = user or ctx.author

        embed = embeds.make_embed(
            ctx=ctx,
            title="Stock History",
            image_url="https://compote.slate.com/images/926e5009-c10a-48fe-b90e-fa0760f82fcd.png"
            "?width=1200&rect=680x453&offset=0x30",
        )

        with dataset.connect(
            database.get_db(), engine_kwargs={"pool_recycle": 300}
        ) as db:
            # Find all stock from user and combine like stock purchases.
            statement = statement = f"""
                SELECT stonk, amount, investment_cost
                FROM stonks
                WHERE author_id = {user.id}
                ORDER BY id DESC
                LIMIT 100"""
            result = db.query(statement)

        port = []
        async with ctx.channel.typing():
            for x in result:
                stonk = x["stonk"]
                amount = abs(int(x["amount"]))
                cost = abs(int(x["investment_cost"]))

                if x["amount"] > 0:
                    icon = BUY
                else:
                    icon = SELL

                port.append(
                    f"{icon}[{stonk}](https://finance.yahoo.com/quote/{stonk})\n"
                    f"Shares:**` {amount:>7,} `** Value:**`{cost:>10,}`**"
                )
        embed.set_footer(text=f"BROKERAGE FEE: {BROKERAGE_FEE_PERCENTAGE*100:.1f}%")
        await LinePaginator.paginate(
            port, ctx, embed, max_size=1000, restrict_to_user=ctx.author
        )

    @commands.before_invoke(record.record_usage)
    @commands.cooldown(rate=1, per=20, type=BucketType.user)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(
        name="stock_lookup", aliases=["stonk_lookup", "stonks_lookup", "stocks_lookup"]
    )
    async def stock_lookup(self, ctx: Context, query: str):
        """Search for best-matching symbols based on your query."""

        embed = embeds.make_embed(
            ctx=ctx,
            title="Stock History",
            image_url="https://compote.slate.com/images/926e5009-c10a-48fe-b90e-fa0760f82fcd.png"
            "?width=1200&rect=680x453&offset=0x30",
        )

        port = []
        async with ctx.channel.typing():
            result = self.stock_query(query)
            for x in result["result"]:
                description = x["description"]
                displaySymbol = x["displaySymbol"]
                symbol = x["symbol"]
                type = x["type"]

                port.append(
                    f"""Description: **{description}**
                        DisplaySymbol: {displaySymbol}
                        Symbol: `{symbol}`
                        Type: {type}"""
                )
        embed.set_footer(text=f"BROKERAGE FEE: {BROKERAGE_FEE_PERCENTAGE*100:.1f}%")
        await LinePaginator.paginate(port, ctx, embed, restrict_to_user=ctx.author)

    @commands.before_invoke(record.record_usage)
    @commands.is_owner()
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(name="market")
    async def market(self, ctx: Context):
        """List All stocks in market with their value."""

        embed = embeds.make_embed(
            ctx=ctx,
            title="Market",
            image_url="https://compote.slate.com/images/926e5009-c10a-48fe-b90e-fa0760f82fcd.png"
            "?width=1200&rect=680x453&offset=0x30",
        )

        with dataset.connect(
            database.get_db(), engine_kwargs={"pool_recycle": 300}
        ) as db:
            # Find all stock from user and combine like stock purchases.
            statement = """
                SELECT stonk, Sum(amount) totalstonks
                FROM stonks
                GROUP BY stonk"""
            result = db.query(statement)

        port = []
        investment = 0
        async with ctx.channel.typing():
            for count, x in enumerate(result):
                # have to sleep due to rate limits on API
                await asyncio.sleep(1)
                stonk = x["stonk"]
                stonk_amount = x["totalstonks"]
                # don't need to lookup any stocks that user doesn't have any of.
                if stonk_amount <= 0:
                    continue
                while True:
                    try:
                        value = self.stock_price(x["stonk"])["c"]
                        break
                    except:
                        await asyncio.sleep(1)
                        continue
                price = round(value * 100, 6)
                investment += price * stonk_amount
                port.append(
                    f"[{stonk}](https://finance.yahoo.com/quote/{stonk})"
                    f" Shares:**` {stonk_amount:>7,} `** Value:**` {stonk_amount*price:>10,.0f}`**"
                )
        embed.title += f": {investment:,.0f} :coin:"
        embed.set_footer(text=f"BROKERAGE FEE: {BROKERAGE_FEE_PERCENTAGE*100:.1f}%")
        await LinePaginator.paginate(
            port, ctx, embed, max_size=2000, restrict_to_user=ctx.author
        )

    @commands.before_invoke(record.record_usage)
    @commands.cooldown(rate=1, per=300, type=BucketType.user)
    @commands.max_concurrency(number=1, per=BucketType.user, wait=False)
    @commands.command(name="Transaction", aliases=["t"])
    async def transaction(self, ctx: Context):
        """List latest transactions in stock market."""

        embed = embeds.make_embed(
            ctx=ctx,
            title="Transactions",
            image_url="https://compote.slate.com/images/926e5009-c10a-48fe-b90e-fa0760f82fcd.png"
            "?width=1200&rect=680x453&offset=0x30",
        )

        with dataset.connect(
            database.get_db(), engine_kwargs={"pool_recycle": 300}
        ) as db:
            # Find all stock from user and combine like stock purchases.
            statement = statement = """
                SELECT author_id, stonk, amount, investment_cost
                FROM stonks
                ORDER BY "timestamp" DESC
                LIMIT 250"""
            result = db.query(statement)

        port = []
        async with ctx.channel.typing():
            for transaction in result:
                if transaction["amount"] > 0:
                    icon = constants.Emojis.buy
                else:
                    icon = constants.Emojis.sell

                port.append(
                    f"{icon} S:**` {abs(transaction['amount']):>7,} `** V:**` "
                    f"{abs(transaction['investment_cost']):>10,.0f}`**"
                    f"[{transaction['stonk']}](https://finance.yahoo.com/quote/{transaction['stonk']})"
                    f" <@{transaction['author_id']}>\n"
                )
        await LinePaginator.paginate(
            port, ctx, embed, max_size=2000, restrict_to_user=ctx.author, linesep=""
        )


def setup(bot: Bot) -> None:
    """Load the Stonks cog."""
    bot.add_cog(Stonks(bot))
    log.info("Cog loaded: Stonks")
