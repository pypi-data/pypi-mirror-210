import dataclasses
from typing import Any, TypedDict
from enum import Enum


@dataclasses.dataclass
class ResponseMessage:
    id: int
    method: str
    code: int
    result: dict[str, Any] = dataclasses.field(default_factory=dict)
    message: str = ""
    original: str = ""
    channel: str = ""

class UserFeedMessage(TypedDict):
    action: str
    ch: str
    data: list | dict


class HttpResponse(TypedDict):
    status: str
    data: list | dict

class HuobiErrorCode(str, Enum):
    INVALID_SYMBOL = "invalid-symbol"
    INVALID_PARAMETERS = "invalid-parameter"
    ACCOUNT_NOT_EXISTS = "account-not-exist"
    INSUFFICIENT_BALANCE = "insufficient-balance"
    UNKNOWN_ERROR = "system-error"

class ErrorDetails(TypedDict):
    ts: int
    status: str
    err_code: HuobiErrorCode
    err_msg: str
