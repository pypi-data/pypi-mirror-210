from decimal import Decimal
from typing import NamedTuple, TypedDict, TypeAlias


class OrderbookEntryNamedTuple(NamedTuple):
    price: Decimal
    quantity: Decimal


class RawOrderbook(TypedDict):
    ts: int
    version: int
    bids: list[list[float]]
    asks: list[list[float]]


