import dataclasses
import time
from typing import Any, Literal

from bittrade_huobi_websocket.models import endpoints


@dataclasses.dataclass(frozen=True)
class RequestMessage:
    method: Literal["GET", "POST"]
    endpoint: endpoints.HuobiEndpoints | str
    params: dict[str, Any] = dataclasses.field(default_factory=dict)
    nonce: int = dataclasses.field(default_factory=lambda: int(1e3 * time.time()))
    id: int = 0
