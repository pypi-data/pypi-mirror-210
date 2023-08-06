import dataclasses
from decimal import Decimal
from typing import Any, Literal, Optional, TypedDict
from enum import Enum


@dataclasses.dataclass
class CancelOrdersBatchParams:
    account_id: str = ""
    symbol: list[str] = dataclasses.field(default_factory=list)
    side: Literal["buy", "sell", ""] = ""
    size: int = 100

    def to_dict(self):
        params_dict = dataclasses.asdict(self)
        params_dict["account-id"] = params_dict.pop("account_id")
        params_dict["symbol"] = ",".join(params_dict.pop("symbol"))
        return {k: v for k, v in params_dict.items() if v}


CancelOrdersBatchData = TypedDict(
    "CancelOrdersBatchData", {"success-count": int, "failed-count": int, "next-id": int}
)
