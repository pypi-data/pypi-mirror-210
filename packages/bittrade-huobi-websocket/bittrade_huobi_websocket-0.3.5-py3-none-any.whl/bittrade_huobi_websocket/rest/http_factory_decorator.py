import functools
from typing import Any, Callable, ParamSpec, TypeVar, TypedDict, cast
import requests
from bittrade_huobi_websocket import models
from bittrade_huobi_websocket.connection import http
from reactivex import Observable

P = ParamSpec("P")


# TODO this typing does not work, it does not allow us to define the sub type of the response's result
R = TypeVar("R", bound=models.HttpResponse)

def http_factory(fn: Callable[P, models.RequestMessage]):
    @functools.wraps(fn)
    def factory(add_token: Callable[[requests.models.Request], requests.models.Request]):
        def inner(*args: P.args, **kwargs: P.kwargs):
            request = fn(*args, **kwargs)
            return cast(Observable[R], http.send_request(
                add_token(http.prepare_request(request))
            ))
        return inner
    return factory
