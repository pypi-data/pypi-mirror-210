from typing import Callable, cast
from reactivex import Observable, compose, operators
from elm_framework_helpers.websockets.operators import connection_operators
from bittrade_huobi_websocket.models.response_message import ResponseMessage, HttpResponse, UserFeedMessage

def keep_messages_only():
    return compose(
        connection_operators.keep_messages_only(),
        operators.map(lambda x: cast(ResponseMessage, x))
    )

def keep_response_messages_only():
    def is_response(x: ResponseMessage):
        return x.id != -1

    return operators.filter(is_response)


def exclude_response_messages():
    def is_response(x: ResponseMessage):
        return x.id == -1

    return operators.filter(is_response)


def extract_data() -> Callable[
    [Observable[UserFeedMessage]], Observable[list | dict]
]:
    return operators.map(lambda x: x["data"])

def extract_http_data() -> Callable[
    [Observable[HttpResponse]], Observable[list | dict]
]:
    return operators.map(lambda x: (
        x["data"]
    ))
