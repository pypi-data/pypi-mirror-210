import dataclasses
from typing import Callable, Optional, cast
from bittrade_huobi_websocket.models import RequestMessage, endpoints, HttpResponse

from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory
from bittrade_huobi_websocket.operators.stream import response_messages
from bittrade_huobi_websocket.models.rest.get_all_open_orders import AllOpenOrdersParams, AllOpenOrdersResponse, AllOpenOrder
from reactivex import operators, compose, Observable, just, throw, empty, from_callable, defer


@http_factory
def get_all_open_orders_http_factory(params: AllOpenOrdersParams):
    return RequestMessage(
        "GET", endpoints.HuobiEndpoints.GET_ALL_OPEN_ORDERS, params=params.to_dict()
    )

def load_all_open_orders(get_all_open_orders_http: Callable[[AllOpenOrdersParams], Observable[AllOpenOrdersResponse]], params: AllOpenOrdersParams) -> Observable[list[AllOpenOrder]]:
    all_orders: list[AllOpenOrder] = []

    current_params = dataclasses.replace(params)
    
    def add_to_all(x: list[AllOpenOrder]):
        nonlocal all_orders, current_params
        # When we loop, the first item is the last item of the previous loop
        if len(all_orders) > 0 and x[0]["id"] == all_orders[-1]["id"]:
            x = x[1:]
        if len(x) == 0:
            return
        all_orders += x
        current_params = dataclasses.replace(current_params, from_order_id = str(x[-1]["id"]), direct="next")
    
    def call(_s):
        return get_all_open_orders_http(current_params)
    
    return defer(call).pipe(
        response_messages.extract_http_data(),
        operators.do_action(add_to_all),
        operators.flat_map(lambda x: empty() if len(x) == params.size else throw(StopIteration())),
        operators.repeat(),
        operators.catch(lambda exc, _src: throw(exc) if not type(exc) == StopIteration else just(all_orders))
    )