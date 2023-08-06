from typing import Optional, cast
from bittrade_huobi_websocket.models import RequestMessage, endpoints
from reactivex import compose, operators, empty, throw, just, concat
from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory
from bittrade_huobi_websocket.models.rest import (
    CancelOrdersBatchParams,
    CancelOrdersBatchData,
)
from bittrade_huobi_websocket.operators.stream.response_messages import extract_http_data


@http_factory
def cancel_orders_batch_http_factory(params: Optional[CancelOrdersBatchParams]=None):
    # URL contains the order id for some odd reason - ignore the below issue
    return RequestMessage(
        "POST",
        endpoints.HuobiEndpoints.CANCEL_ORDER_BATCH,
        params=params.to_dict() if params else {},
    )

def until_all_closed():
    return compose(
        extract_http_data(),
        operators.flat_map(
            lambda x: just(x) if x["next-id"] != -1 else concat(
                just(x), 
                throw(StopIteration())
            )
        ),
        operators.repeat(),
        operators.catch(lambda exc, src: (
            empty() if type(exc) == StopIteration else throw(exc)
        ))
    )
