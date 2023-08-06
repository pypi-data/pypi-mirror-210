from logging import getLogger
import os
from typing import Any, Optional

from reactivex import ConnectableObservable
from reactivex.abc import SchedulerBase
from reactivex.operators import publish

from bittrade_huobi_websocket.connection.reconnect import retry_with_backoff
from bittrade_huobi_websocket.connection.generic import raw_websocket_connection

logger = getLogger(__name__)

USER_URL = os.getenv('HUOBI_USER_WEBSOCKET', 'wss://api.huobi.pro/ws/v2')


def private_websocket_connection(
    *, reconnect: bool = True, scheduler: Optional[SchedulerBase] = None
) -> ConnectableObservable[Any]:
    """You need to add your token to the EnhancedWebsocket
    An example implementation can be found in `examples/private_subscription.py`"""
    connection = raw_websocket_connection(url=USER_URL, scheduler=scheduler)
    if reconnect:
        connection = connection.pipe(retry_with_backoff())

    return connection.pipe(publish())


__all__ = [
    "private_websocket_connection",
]
