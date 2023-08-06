from typing import Callable, cast
from reactivex import Observable, compose, operators
from reactivex.operators import flat_map, with_latest_from
from bittrade_huobi_websocket.models import (
    EnhancedWebsocket,
    UserFeedMessage,
    ResponseMessage,
)

from bittrade_huobi_websocket.operators.stream.response_messages import extract_data
from bittrade_huobi_websocket.models import OrderDict

from bittrade_huobi_websocket.channels.subscribe import subscribe_to_channel
from ccxt import huobi

OpenOrdersData = list[OrderDict]


def _subscribe_open_orders(
    messages: Observable[ResponseMessage],
    instrument: str = "",
):
    channel = f"orders#{instrument}"
    return subscribe_to_channel(messages, channel)


def to_ccxt_entries(exchange: huobi):
    def to_open_orders_entries_(message: ResponseMessage):
        return cast(list[dict], exchange.parse_orders(message))

    return to_open_orders_entries_


def subscribe_open_orders(
    all_messages: Observable[ResponseMessage],
    symbol: str,
) -> Callable[[Observable[EnhancedWebsocket]], Observable[OrderDict]]:
    """Unparsed orders (only extracted result array)"""
    return compose(
        _subscribe_open_orders(all_messages, symbol),
        extract_data(),  # type: ignore
    )


__all__ = ["subscribe_open_orders"]
