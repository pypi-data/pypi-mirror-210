import multiprocessing
from contextlib import contextmanager
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Callable, Optional, cast

import requests
from elm_framework_helpers.ccxt.models.orderbook import Orderbook
from reactivex import Observable
from reactivex.abc import DisposableBase
from elm_framework_helpers.websockets import models


from ..models import BookConfig
from .framework import get_framework

logger = getLogger(__name__)

@contextmanager
def cryptodotcom_sockets(
    add_token: Callable[
        [Observable[Any]],
        Callable[[models.EnhancedWebsocket], Observable[models.EnhancedWebsocket]],
    ],
    add_token_http: Callable[[requests.models.Request], requests.models.Request],
    books: Optional[tuple[BookConfig]] = None,
    load_markets: bool = False
):
    context = get_framework(
        add_token, add_token_http, books, load_markets
    )

    context.all_subscriptions.add(
        cast(DisposableBase, context.public_socket_connection.connect(scheduler=context.scheduler))
    )
    context.all_subscriptions.add(
        cast(DisposableBase, context.private_socket_connection.connect(scheduler=context.scheduler))
    )
    yield context

    context.all_subscriptions.dispose()
