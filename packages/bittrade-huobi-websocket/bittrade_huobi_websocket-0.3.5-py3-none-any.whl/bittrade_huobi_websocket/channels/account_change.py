from decimal import Decimal
from typing import Callable, Literal, cast
from reactivex import Observable, compose, operators
import reactivex
from bittrade_huobi_websocket.models import (
    EnhancedWebsocket,
    ResponseMessage,
)

from bittrade_huobi_websocket.operators.stream.response_messages import extract_data
from bittrade_huobi_websocket.models.user_balance import (
    AccountAssetBalance,
    AccountUpdateData,
    is_initial_data,
)

from bittrade_huobi_websocket.channels.subscribe import subscribe_to_channel
from copy import deepcopy


def _subscribe_account_change(
    messages: Observable[ResponseMessage],
    mode: Literal[0, 1, 2] = 0,
):
    channel = f"accounts.update#{mode}"
    return subscribe_to_channel(messages, channel)


def subscribe_account_change(
    all_messages: Observable[ResponseMessage],
    mode: Literal[0, 1, 2] = 2,
) -> Callable[[Observable[EnhancedWebsocket]], Observable[AccountUpdateData]]:
    """Unparsed orders (only extracted result array)"""
    return compose(
        _subscribe_account_change(all_messages, mode),
        extract_data(),  # type: ignore
    )


def update_account_asset_balances(
    balances: dict[tuple[int, str], AccountAssetBalance], update: AccountUpdateData
) -> dict[tuple[int, str], AccountAssetBalance]:
    key = update["accountId"], update["currency"]
    balances = deepcopy(balances)
    if key not in balances and not is_initial_data(update):
        raise Exception("Initial data should be present")
    balances[key] = update_account_asset_balance(update, balances.get(key, None))
    return balances


def update_account_asset_balance(
    update: AccountUpdateData, previous_balance: AccountAssetBalance | None
) -> AccountAssetBalance:
    return AccountAssetBalance(
        currency=update["currency"],
        accountType=update["accountType"],
        accountId=update["accountId"],
        balance=Decimal(update["balance"])
        if "balance" in update
        else previous_balance.balance,
        available=Decimal(update["available"])
        if "available" in update
        else previous_balance.available,
    )


def only_for_account(account_id: int):
    return operators.filter(lambda x: x["accountId"] == account_id)


def to_single_account_asset_balances(
    account_id: int,
) -> Callable[
    [Observable[AccountUpdateData]],
    Observable[dict[str, AccountAssetBalance]],
]:
    return reactivex.compose(
        only_for_account(account_id),
        operators.scan(update_account_asset_balances, {}),
        operators.map(lambda x: {k[1]: v for k, v in x.items()}),
    )


def to_all_accounts_asset_balances() -> (
    Callable[
        [Observable[AccountUpdateData]],
        Observable[dict[tuple[int, str], AccountAssetBalance]],
    ]
):
    return operators.scan(update_account_asset_balances, {})


__all__ = ["subscribe_account_change", "only_for_account", "to_single_account_asset_balances", "to_all_accounts_asset_balances"]
