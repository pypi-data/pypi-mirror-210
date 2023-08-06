from typing import Optional, cast
from bittrade_huobi_websocket.models import RequestMessage, endpoints
from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory


@http_factory
def order_details_http_factory(order_id: str):
    return RequestMessage(
        "GET",
        endpoints.HuobiEndpoints.ORDER_DETAILS.value.format(order_id),
    )

