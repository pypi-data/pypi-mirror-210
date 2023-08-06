import dataclasses
from decimal import Decimal
from typing import Any, Literal, Optional, TypedDict
from enum import Enum


class CancelOrderState(Enum):
    CLOSED = -1
    CREATED = 1
    SUBMITTED = 3
    PARTIAL_FILLED = 4
    PARTIALLY_CANCELLED = 5
    FILLED = 6
    CANCELLED = 7
    CANCELLING = 10


@dataclasses.dataclass
class CancelOrderParams:
    order_id: str
    symbol: str

    def to_dict(self):
        params_dict = dataclasses.asdict(self)
        params_dict["order-id"] = params_dict.pop("order_id")
        return {k: v for k, v in params_dict.items() if v}


CancelOrderResponse = TypedDict(
    "OrderStateResponse", {"err-code": str, "order-state": int}
)
