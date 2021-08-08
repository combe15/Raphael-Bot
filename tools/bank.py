import logging
from datetime import datetime
from typing import Union

import dataset
import discord

from tools import database

log = logging.getLogger(__name__)


class Bank:
    def __init__(self, user: Union[discord.User, discord.Member, discord.ClientUser]):
        # Note: discord.ClientUser is the bot itself.
        if not isinstance(user, (discord.User, discord.Member, discord.ClientUser)):
            raise TypeError(
                f"Object given was not a User nor Member object.\n\tType given: {type(user)}"
            )
        self.user = user
        self.balance = self.__balance__()

    def __str__(self) -> str:
        """<name>'s balance is $<balance>."""

        return f"{self.user.name}'s balance is **$`{self.balance}`**."

    def __format__(self, format_spec: str) -> str:
        """Returns balance's value as to the specified format."""

        return format(self.balance, format_spec)

    def __get__(self) -> float:
        """Returns balance's value as a float."""

        return float(self.balance)

    def __lt__(self, other) -> bool:
        """Less than"""
        if isinstance(other, int) or isinstance(other, float):
            return self.balance < other
        else:
            raise TypeError

    def __le__(self, other) -> bool:
        """Less than or equal to"""
        if isinstance(other, int) or isinstance(other, float):
            return self.balance <= other
        else:
            raise TypeError

    def __gt__(self, other) -> bool:
        """Greater than"""
        if isinstance(other, int) or isinstance(other, float):
            return self.balance > other
        else:
            raise TypeError

    def __ge__(self, other) -> bool:
        """Greater than or equal to"""
        if isinstance(other, int) or isinstance(other, float):
            return self.balance >= other
        else:
            raise TypeError

    def __float__(self) -> bool:
        return self.balance

    def __balance__(self) -> float:
        """Get the balance of a user."""

        with dataset.connect(database.get_db()) as db:
            # Find last bank transaction.
            statement = statement = f"""
                SELECT opening_balance, transaction_amount
                FROM bank
                WHERE author_id = {self.user.id}
                ORDER BY timestamp
                LIMIT 1
                """
            result = db.query(statement)

        for row in result:
            balance = row["opening_balance"] + row["transaction_amount"]
            break
        else:
            # If there was no result for the user, default balance is given.
            balance = 500

        return float(balance)

    def add(self, amount: float, reason: str = "") -> "Bank":
        """Add to a user's balance."""

        if amount == 0:  # Pointless, do nothing.
            return 0

        self.__record_ledger__(amount, reason)
        self.balance += amount
        return self

    def subtract(self, amount: float, reason: str = "") -> "Bank":
        """Subtract from a user's balance."""

        if amount == 0:  # Pointless, do nothing.
            return 0

        self.__record_ledger__(amount, reason)
        self.balance -= amount
        return self

    def set(self, amount: float, reason: str = "") -> "Bank":
        """Set a user's balance."""

        self.__record_ledger__(amount - self.balance, reason)  # Because math
        self.balance = amount
        return self

    def __record_ledger__(self, amount: float, reason: str = "") -> None:
        with dataset.connect(database.get_db()) as db:
            # Find last bank transaction
            db["bank"].insert(
                dict(
                    author_id=self.user.id,
                    opening_balance=self.balance,
                    transaction_amount=amount,
                    reason=reason,
                    timestamp=datetime.now(),
                )
            )
            db.commit()

    def name(self) -> str:
        """Return bank owner's name."""
        return self.user.name

    def id(self) -> int:
        """Return bank owner's ID."""
        return self.user.id
