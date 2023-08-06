from typing import Callable, cast
from bittrade_huobi_websocket.models import RequestMessage, endpoints, HttpResponse
from bittrade_huobi_websocket.models.rest.get_account_balance import Account, Balance
from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory
from reactivex import operators, compose, Observable
from bittrade_huobi_websocket.operators.stream import response_messages
from returns import maybe


@http_factory
def get_account_balance_http_factory(account_id: str):
    return RequestMessage(
        "GET",
        endpoints.HuobiEndpoints.GET_ACCOUNT_BALANCE.value.format(account_id),
    )

def find_by_instrument(account: Account, currency: str) -> maybe.Maybe[Balance]:
    for balance in account["list"]:
        if balance.get("currency", "") == currency:
            return maybe.Some(balance)
    else:
        return maybe.Nothing
    
def to_account():
    return compose(
        response_messages.extract_http_data(),
        operators.map(lambda x: cast(Account, x)),
    )

def for_instrument(currency: str) -> Callable[[Observable[Account]], Observable[maybe.Maybe[Balance]]]:
    return operators.map(lambda x : find_by_instrument(x, currency))