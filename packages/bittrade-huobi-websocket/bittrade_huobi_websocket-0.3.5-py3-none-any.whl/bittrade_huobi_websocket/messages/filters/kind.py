from reactivex import operators
from typing import TYPE_CHECKING, Callable
from reactivex import Observable
from bittrade_huobi_websocket.models import UserFeedMessage, ResponseMessage


def _is_channel_message(channel: str):
    def channel_message_filter(x: UserFeedMessage):
        return x.get("action", "") == "push" and x.get("ch", "") == channel

    return channel_message_filter


def keep_channel_messages(
    channel: str,
) -> Callable[[Observable[ResponseMessage]], Observable[UserFeedMessage]]:
    return operators.filter(_is_channel_message(channel))
