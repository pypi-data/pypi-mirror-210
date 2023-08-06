from dataclasses import dataclass
from typing import Literal, TypedDict


@dataclass
class AssetTransferRequest:
    from_user: int
    from_account_type: Literal["spot", "margin"]
    from_account: int
    to_user: int
    to_account_type: Literal["spot", "margin"]
    to_account: int
    currency: str
    amount: str

    def to_dict(self):
        return {
            "from-user": self.from_user,
            "from-account-type": self.from_account_type,
            "from-account": self.from_account,
            "to-user": self.to_user,
            "to-account-type": self.to_account_type,
            "to-account": self.to_account,
            "currency": self.currency,
            "amount": self.amount,
        }
