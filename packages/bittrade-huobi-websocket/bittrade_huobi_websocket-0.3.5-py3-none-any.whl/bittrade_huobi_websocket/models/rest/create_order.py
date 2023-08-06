import dataclasses
from decimal import Decimal
from typing import Any, Literal, Optional
from ccxt import huobi

OrderType = Literal[
    "buy-market",
    "sell-market",
    "buy-limit",
    "sell-limit",
    "buy-ioc",
    "sell-ioc",
    "buy-limit-maker",
    "sell-limit-maker",
    "buy-stop-limit",
    "sell-stop-limit",
    "buy-limit-fok",
    "sell-limit-fok",
    "buy-stop-limit-fok",
    "sell-stop-limit-fok",
]


@dataclasses.dataclass
class OrderCreateParams:
    account_id: str
    amount: str
    price: str
    symbol: str
    type: OrderType
    source: str = "spot-api"
    client_order_id: str = ""
    stop_price: str = ""

    def to_dict(self):
        as_dict = dataclasses.asdict(self)
        del as_dict["account_id"]
        as_dict["account-id"] = self.account_id
        del as_dict["client_order_id"]
        if self.client_order_id:
            as_dict["client-order-id"] = self.client_order_id
        del as_dict["stop_price"]
        if self.stop_price:
            as_dict["stop-price"] = self.stop_price

        return as_dict


@dataclasses.dataclass
class OrderCreateResponse:
    status: str
    data: str
