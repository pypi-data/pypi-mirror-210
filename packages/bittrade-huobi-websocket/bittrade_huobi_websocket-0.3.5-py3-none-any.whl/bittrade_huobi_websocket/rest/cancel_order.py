from typing import Optional, cast
from bittrade_huobi_websocket.models import RequestMessage, endpoints
from reactivex import compose, operators, empty, throw, just
from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory
from bittrade_huobi_websocket.models.rest import (
    CancelOrderParams,
    CancelOrderState,
    CancelOrderResponse,
)


@http_factory
def cancel_order_http_factory(params: CancelOrderParams):
    # URL contains the order id for some odd reason - ignore the below issue
    return RequestMessage(
        "POST",
        endpoints.HuobiEndpoints.CANCEL_ORDER.value.format(params.order_id),
        params=params.to_dict(),
    )


def _is_already_closed(exc: CancelOrderResponse, _src):
    if exc["err-code"] == "order-orderstate-error" and exc["order-state"] not in [
        CancelOrderState.SUBMITTED.value
    ]:
        return just(exc["order-state"])
    return throw(exc)


def ignore_already_closed():
    return compose(operators.catch(_is_already_closed))
