from typing import Literal, TypedDict
import dataclasses


@dataclasses.dataclass
class AllOpenOrdersParams:
    account_id: str = ""
    symbol: str = ""
    side: Literal["buy", "sell", ""] = ""
    from_order_id: str = ""
    direct: str = ""
    size: int = 100

    def to_dict(self) -> dict:
        params_dict = dataclasses.asdict(self)
        params_dict["account-id"] = params_dict.pop("account_id")
        params_dict["from"] = params_dict.pop("from_order_id")
        return {k.replace("_", "-"): v for k, v in params_dict.items() if v}


AllOpenOrder = TypedDict(
    "AllOpenOrder",
    {
        "symbol": str,
        "source": str,
        "price": str,
        "created-at": int,
        "amount": str,
        "account-id": int,
        "filled-cash-amount": str,
        "client-order-id": str,
        "filled-amount": str,
        "filled-fees": str,
        "id": int,
        "state": str,
        "type": str,
    },
)


class AllOpenOrdersResponse(TypedDict):
    status: str
    data: list[AllOpenOrder]
