from typing import Any, Callable, Optional, cast
from reactivex import Observable, operators, compose
from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory
from bittrade_huobi_websocket.models import RequestMessage, endpoints
from bittrade_huobi_websocket.operators.stream import response_messages
from bittrade_huobi_websocket.models.rest import account_account_history


@http_factory
def get_account_account_history_http_factory(params: account_account_history.AccountHistoryParams):
    return RequestMessage(
        "GET", endpoints.HuobiEndpoints.ACCOUNT_ACCOUNT_HISTORY, params=params.to_dict()
    )

def map_to_account_history() -> Callable[[Observable[dict]], Observable[Any]]:
    return compose(
        response_messages.extract_http_data(),
        operators.map(lambda x: cast(account_accounts.AccountList, x)),
    )
