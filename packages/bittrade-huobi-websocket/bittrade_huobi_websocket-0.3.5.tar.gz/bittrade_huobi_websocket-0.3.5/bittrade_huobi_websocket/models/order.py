from enum import Enum
from pydantic.dataclasses import dataclass
import dataclasses
from typing import Literal, Optional, TypedDict, Protocol


# For sending
class OrderType(str, Enum):
    buy_market = "buy-market"
    sell_market = "sell-market"
    market = "market"
    limit = "limit"
    stop_loss = "stop-loss"
    take_profit = "take-profit"
    stop_loss_limit = "stop-loss-limit"
    take_profit_limit = "take-profit-limit"
    settle_position = "settle-position"
    buy_limit_maker = "buy-limit-maker"
    sell_limit_maker = "sell-limit-maker"


OrderDetailsTypedDict = TypedDict(
    "OrderDetailsTypedDict",
    {
        "id": int,
        "symbol": str,
        "account-id": int,
        "client-order-id": str,
        "amount": str,
        "price": str,
        "created-at": int,
        "updated-at": int,
        "type": str,
        "field-amount": str,
        "field-cash-amount": str,
        "field-fees": str,
        "finished-at": int,
        "source": str,
        "state": str,
        "canceled-at": int,
    },
)


class OrderSide(str, Enum):
    buy = "BUY"
    sell = "SELL"


class OrderStatus(str, Enum):
    new = "submitted"
    pending = "submitted"
    rejected = "rejected"
    active = "ACTIVE"
    canceled = "canceled"
    filled = "filled"


class OrderDict(TypedDict):
    aggressor: str
    execAmt: str
    lastActTime: int
    remainAmt: str
    orderPrice: str
    orderSize: int
    orderSource: str
    eventType: str
    symbol: str
    type: str
    orderId: int
    clientOrderId: str
    orderStatus: str
    tradePrice: str
    tradeVolume: str


class HasOrderType(TypedDict):
    type: str


def get_order_side(x: HasOrderType):
    return "buy" if is_buy_order(x) else "sell"


def _is_side_order(x: HasOrderType, side: Literal["sell", "buy"]):
    return x["type"].startswith(side)


def is_buy_order(x: HasOrderType):
    return _is_side_order(x, "buy")


def is_sell_order(x: HasOrderType):
    return _is_side_order(x, "sell")


__all__ = [
    "OrderStatus",
    "OrderType",
    "OrderSide",
    "OrderDict",
    "get_order_side",
    "is_buy_order",
    "is_sell_order",
]
