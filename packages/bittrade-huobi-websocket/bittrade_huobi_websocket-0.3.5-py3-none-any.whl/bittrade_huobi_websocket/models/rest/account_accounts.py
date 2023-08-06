from typing import TypedDict


class AccountInfo(TypedDict):
    id: int
    type: str
    subtype: str
    state: str


class AccountResponse(TypedDict):
    status: str
    data: list[AccountInfo]
