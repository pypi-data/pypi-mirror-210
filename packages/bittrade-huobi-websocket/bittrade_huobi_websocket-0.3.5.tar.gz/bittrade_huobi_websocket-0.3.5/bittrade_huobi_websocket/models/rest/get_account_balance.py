from typing import TypedDict

class Balance(TypedDict):
    currency: str
    type: str
    balance: str
    seq_num: str

class Account(TypedDict):
    id: int
    type: str
    state: str
    list: list[Balance]
