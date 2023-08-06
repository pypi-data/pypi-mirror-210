from typing import Callable
from reactivex import Observable, compose
from bittrade_huobi_websocket.models import (
    EnhancedWebsocket,
    ResponseMessage,
)

from bittrade_huobi_websocket.operators.stream.response_messages import extract_data
from bittrade_huobi_websocket.models import OrderDict

from bittrade_huobi_websocket.channels.subscribe import subscribe_to_channel



def _subscribe_trades(
    messages: Observable[ResponseMessage],
    instrument: str,
    mode: str,
):
    channel = f"trade.clearing#{instrument}#{mode}"
    return subscribe_to_channel(messages, channel)


def subscribe_trades(
    all_messages: Observable[ResponseMessage],
    symbol: str,
    mode: str,
) -> Callable[[Observable[EnhancedWebsocket]], Observable[OrderDict]]:
    """Unparsed orders (only extracted result array)"""
    return compose(
        _subscribe_trades(all_messages, symbol, mode),
        extract_data(),  # type: ignore
    )


__all__ = ["subscribe_trades"]
