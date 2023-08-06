import dataclasses
from typing import Literal, TypedDict
from datetime import datetime

TransactTypes = Literal[
    "trade",
    "etf",
    "transact-fee",
    "fee-deduction",
    "transfer",
    "credit",
    "liquidation",
    "interest",
    "deposit",
    "withdraw",
    "withdraw-fee",
    "exchange",
    "other-types",
    "rebate"
]

@dataclasses.dataclass(frozen=True)
class AccountHistoryParams:
    account_id: str
    currency: str = ""
    transact_types: list[TransactTypes] = dataclasses.field(default_factory=list)
    start_time: datetime | None = None
    end_time: datetime | None = None
    sort: Literal["asc", "desc"] = "asc"
    size: int = 100
    from_id: int = 0

    def to_dict(self) -> dict:
        data = dataclasses.asdict(self)
        if self.start_time:
            data["start-time"] = int(self.start_time.timestamp() * 1000)
            del data["start_time"]
        if self.end_time:
            data["end-time"] = int(self.end_time.timestamp() * 1000)
            del data["end_time"]
        if self.transact_types:
            data["transact-types"] = ",".join(self.transact_types)
        return {k.replace("_", "-"): v for k, v in data.items() if v}

AccountHistoryData = TypedDict("AccountHistoryData", {
    "account-id": int,
    "currency": str,
    "record-id": int,
    "transact-amt": str,
    "transact-type": str,
    "avail-balance": str,
    "acct-balance": str,
    "transact-time": int,
})

AccountHistoryResponse = TypedDict("AccountHistoryResponse", {
    "status": str,
    "data": list[AccountHistoryData],
    "next-id": int,
})
