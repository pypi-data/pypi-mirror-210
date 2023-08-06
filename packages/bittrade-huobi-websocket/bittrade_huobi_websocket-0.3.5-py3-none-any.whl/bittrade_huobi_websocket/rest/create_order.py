from typing import Any, Callable, Optional, TYPE_CHECKING

import logging
from reactivex import Observable, operators, disposable, just, throw

from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory
from ccxt import huobi
from bittrade_huobi_websocket.models.rest.create_order import (
    OrderCreateParams,
    OrderCreateResponse,
)
from bittrade_huobi_websocket.models import RequestMessage
from bittrade_huobi_websocket.models.endpoints import HuobiEndpoints

logger = logging.getLogger(__name__)


@http_factory
def create_order_http_factory(params: OrderCreateParams):
    return RequestMessage("POST", HuobiEndpoints.CREATE_ORDER, params=params.to_dict())
