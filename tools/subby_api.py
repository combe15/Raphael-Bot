import logging

import discord
import requests

import constants

SUBBY_URL = constants.Subby_api.address
SUBBY_APIKEY = constants.Subby_api.api_key
BOT_ID = int(constants.Bot.id)

SUBBY_PAYLOAD = {"apikey": SUBBY_APIKEY}
REQUEST_TIMEOUT = 15

log = logging.getLogger(__name__)


def get_balance(member_id: discord.Member.id) -> int:
    """Calling Subby API to get ramen amount.

    Args:
        member_id (discord.Member.id): Discord member's ID.

    Raises:
        TypeError: `member_id` must be an int.
        Exception: Retreving credits failed.
        Exception: Subby Broke the API.
        Exception: API Timed out.

    Returns:
        int: Member's balance.
    """
    if not isinstance(member_id, int):
        log.critical(
            f"SUBBY API, get_balance: Given value was not an interger. check your code! {member_id=}"
        )
        raise TypeError("member_id must be an int")

    log.trace(f"SUBBY API, get_balance: issued for {member_id=}")
    url = f"{SUBBY_URL}/economy/user/{member_id}"

    try:
        # This fails quite often, so there is some error checking here.
        response = requests.get(url=url, params=SUBBY_PAYLOAD, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            # Let us know what the HTTP code is when it fails.
            log.trace(f"SUBBY API, get_balance: request {response.status_code=}")
            raise Exception(f"retreving credits failed: {response.status_code}")

        log.trace(f"SUBBY API, get_balance: {response.status_code=} {response.json()=}")

        balance = response.json()["buns"]

    # Catch if the API fails to respond.
    except requests.exceptions.ConnectionError:
        log.trace("SUBBY API, get_balance: ConnectionError")
        raise Exception("Subby Broke the API, Ping him")

    except requests.Timeout:
        raise Exception("Subby API Timed out")

    log.trace(f"SUBBY API, get_balance: {balance=}")
    return balance


def add_balance(member_id: discord.Member.id, amount, edit_house: bool = False) -> int:
    """Calling Subby API to take ramen amount.

    Args:
        member_id (discord.Member.id): Discord member's ID.
        amount ([type]): Amount to add member's account.
        edit_house (bool, optional): Transfer funds to the bot. Defaults to False.

    Raises:
        TypeError: `member_id` must be an int.
        Exception: Adding credits failed.
        Exception: Subby Broke the API.
        Exception: API Timed out.

    Returns:
        int: Member's new balance
    """
    if not isinstance(member_id, int):
        log.critical(
            f"SUBBY API, add_balance: Given value was not an interger. check your code! {member_id=}"
        )
        raise TypeError("member_id must be an int")

    if amount == 0:  # Pointless, do nothing.
        return 0

    log.trace(f"SUBBY API, add_balance: {member_id=} {amount=} {edit_house=}")
    if edit_house:  # For when you want see how well your house bank is doing.
        subtract_balance(member_id=BOT_ID, amount=amount)

    # Need balance so you can add on to whatever the user had previously.
    balance = get_balance(member_id)

    url = f"{SUBBY_URL}/economy/{member_id}/buns/{balance+amount}"
    try:
        # This fails quite often, so there is some error checking here.
        response = requests.post(url=url, params=SUBBY_PAYLOAD, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            log.trace(f"SUBBY API, add_balance: request {response.status_code=}")
            # Let us know what the HTTP code is when it fails.
            raise Exception(
                f"adding credits failed: {response.status_code=} {response.json()=}"
            )
            return

        log.trace(f"SUBBY API, add_balance: {response.json()=}")

    # Catch if the API fails to respond.
    except requests.exceptions.ConnectionError:
        log.trace("SUBBY API, add_balance: ConnectionError")
        raise Exception("Subby Broke the API, Ping him, credits not awarded")

    except requests.Timeout:
        raise Exception("Subby API Timed out")

    return response.json()["buns"]


def subtract_balance(
    member_id: discord.Member.id, amount: int, edit_house: bool = False
) -> int:
    """Calling Subby API to take ramen amount.

    Args:
        member_id (discord.Member.id): Discord member's ID.
        amount (int): Amount to subtract member's account.
        edit_house (bool, optional): Transfer funds to the bot. Defaults to False.

    Raises:
        TypeError: `member_id` must be an int.
        Exception: Subtracting credits failed.
        Exception: Subby Broke the API.
        Exception: API Timed out.

    Returns:
        int: Member's new balance
    """
    if not isinstance(member_id, int):
        log.critical(
            f"SUBBY API, subtract_balance: Given value was not an interger. check your code! {member_id=}"
        )
        raise TypeError("member_id must be an int")

    log.trace(f"SUBBY API, subtract_balance: {member_id=} {amount=} {edit_house=}")
    if amount == 0:  # Pointless, do nothing.
        return 0

    if edit_house:  # For when you want see how well your house bank is doing.
        add_balance(member_id=BOT_ID, amount=amount)

    # Need balance so you can add on to whatever the user had previously.
    balance = get_balance(member_id)

    url = f"{SUBBY_URL}/economy/{member_id}/buns/{balance-amount}"

    try:
        # This fails quite often, so there is some error checking here.
        response = requests.post(url=url, params=SUBBY_PAYLOAD, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            log.trace(f"SUBBY API, subtract_balance: request {response.status_code=}")
            # Let us know what the HTTP code is when it fails
            raise Exception(f"subtracting credits failed: {response.status_code=}")
            return 0

        log.trace(
            f"SUBBY API, subtract_balance: {response.status_code=} {response.json()=}"
        )

    # Catch if the API fails to respond
    except requests.exceptions.ConnectionError:
        log.trace("SUBBY API, subtract_balance: ConnectionError")
        raise Exception("Subby Broke the API, Ping him, credits not taken. lucky...")

    except requests.Timeout:
        raise Exception("Subby API Timed out")

    return response.json()["buns"]


def set_balance(member_id: discord.Member.id, amount: int) -> int:
    """Calling Subby API to set ramen amount.

    Args:
        member_id (discord.Member.id): Discord member's ID.
        amount (int): Amount to set member's account.

    Raises:
        TypeError: `member_id` must be an int.
        Exception: Set credits failed.
        Exception: Subby Broke the API.
        Exception: API Timed out.

    Returns:
        int: Member's new balance.
    """
    if not isinstance(member_id, int):
        log.critical(
            f"SUBBY API, set_balance: Given value was not an interger. check your code! {member_id=}"
        )
        raise TypeError("user must be an int")

    log.trace(f"SUBBY API, set_balance: {member_id=} {amount=}")
    url = f"{SUBBY_URL}/economy/{member_id}/buns/{amount}"

    try:
        # This fails quite often, so there is some error checking here.
        response = requests.post(url=url, params=SUBBY_PAYLOAD, timeout=REQUEST_TIMEOUT)

        if response.status_code != 200:
            log.error(f"SUBBY API, set_balance: request {response.status_code=}")
            # Let us know what the HTTP code is when it fails.
            raise Exception(f"set credits failed: {response.status_code=}")
            return 0

        log.trace(f"SUBBY API, set_balance: {response.status_code=} {response.json()=}")

    # Catch if the API fails to respond.
    except requests.exceptions.ConnectionError:
        log.error("SUBBY API, set_balance: ConnectionError")
        raise Exception("Subby Broke the API, Ping him. balance not given")

    except requests.Timeout:
        raise Exception("Subby API Timed out")

    return response.json()["buns"]


def record_ledger(
    member_sender_id: discord.Member.id,
    member_receiver_id: discord.Member.id,
    amount: int,
    reason: str = "None",
) -> None:
    """Recording transaction history between members with SUBBY API.

    Features:
        If amount is negative, then sender and receiver positions will be swapped.
        If amount is zero, function will do nothing.
        If both sender and receiver are the same, do nothing.

    Args:
        member_sender_id (discord.Member.id): Discord member's ID of sender.
        member_receiver_id (discord.Member.id): Discord member's ID of receiver.
        amount (int): Amount transferred.
        reason (str, optional): [description]. Defaults to "None".

    Raises:
        TypeError: Member ID must be an int.
        Exception: Subby Broke the API.
        Exception: API Timed out.
    """
    if not isinstance(member_sender_id, int) or not isinstance(member_receiver_id, int):
        log.critical(
            "SUBBY API, record_ledger: Given value was not an interger."
            "check your code! {member_sender_id=} OR {member_receiver_id=}"
        )
        raise TypeError("Member ID must be an int.")

    log.trace(
        f"SUBBY API, record_ledger: {member_sender_id=} {member_receiver_id=} {amount=}"
    )

    if amount == 0:  # If amount is zero, function will do nothing.
        return
        log.debug(f"SUBBY API, record_ledger: {amount=} was zero, do nothing")

    if (
        amount < 0
    ):  # If amount is negative, then sender and receiver positions will be swapped.
        x = member_sender_id
        member_sender_id = member_receiver_id
        member_receiver_id = x
        amount = abs(amount)
        log.debug(
            "SUBBY API, record_ledger: sender and receiver swapped places, due to amount being negative"
        )

    if (
        member_sender_id == member_receiver_id
    ):  # If both sender and receiver are the same, do nothing.
        log.info(
            'SUBBY API, record_ledger: "member_sender_id" cannot be the same as "member_receiver_id". '
            f"{member_sender_id=} {member_receiver_id=}"
        )
        return

    url = f"{SUBBY_URL}/economy/transaction/add"
    payload = SUBBY_PAYLOAD
    json = {
        "fromUserID": f"{member_sender_id}",
        "toUserID": f"{member_receiver_id}",
        "amount": f"{amount}",
        "reason": f"{reason}",
    }

    log.trace(f"SUBBY API, record_ledger: {json=}")
    try:
        response = requests.post(
            url=url, json=json, params=payload, timeout=REQUEST_TIMEOUT
        )
        log.debug(
            f"SUBBY API, record_ledger: {response.status_code=} {response.json()=}"
        )

    except requests.exceptions.ConnectionError:
        log.error("SUBBY API, record_ledger: ConnectionError")
        raise Exception("Subby Broke the API, Ping him, credits not awarded")

    except requests.Timeout:
        raise Exception("Subby API Timed out")

    except Exception as exception:
        log.error(f"SUBBY API, record_ledger: {exception=}")
        pass  # This API point is not critical, so no real point in doing anything with it.


def record_emoji(
    member_id: discord.Member.id, emoji_name: str, action: str, cost: int
) -> None:
    """Recording emoji history with SUBBY API.

    Args:
        member_id (discord.Member.id): Discord member's ID.
        emoji_name (str): name of emoji.
        action (str): `purchase` or `removal`.
        cost (int): cost of purchase.

    Raises:
        TypeError: `action` must be `purchase` or `removal`.
        ValueError: `cost` cannot be negative.
        Exception: Subby broke the API.
        Exception: API Timed out.
    """
    if action not in ["purchase", "removal"]:
        log.critical(
            f"SUBBY API, record_emoji: Given value was not approperate. check your code! {action=}"
        )
        raise TypeError("action must be 'purchase' or 'removal'")

    log.trace(f"SUBBY API, record_emoji: {member_id=} {emoji_name=} {action=} {cost=}")

    if (
        cost < 0
    ):  # If amount is negative, then sender and receiver positions will be swapped.
        raise ValueError("{cost=} cannot be negative")
        log.debug(
            "SUBBY API, record_emoji: cost amount is negative when it should never be"
        )

    url = f"{SUBBY_URL}/emojis/log"
    payload = SUBBY_PAYLOAD
    json = {
        "userID": f"{member_id}",
        "emojiName": f"{emoji_name}",
        "action": f"{action}",
        "cost": f"{cost}",
    }

    log.trace(f"SUBBY API, record_emoji: {json=}")
    try:
        response = requests.post(
            url=url, json=json, params=payload, timeout=REQUEST_TIMEOUT
        )
        log.debug(
            f"SUBBY API, record_emoji: {response.status_code=} {response.json()=}"
        )
    except requests.exceptions.ConnectionError:
        log.error("SUBBY API, record_emoji: ConnectionError")
        raise Exception("Subby Broke the API, Ping him, credits not awarded")
    except requests.Timeout:
        raise Exception("Subby API Timed out")
    except Exception as exception:
        log.error(f"SUBBY API, record_emoji: {exception=}")
        pass  # This API point is not critical, so no real point in doing anything with it.
