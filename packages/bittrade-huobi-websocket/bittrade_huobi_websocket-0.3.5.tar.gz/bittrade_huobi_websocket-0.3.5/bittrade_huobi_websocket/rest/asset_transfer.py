from typing import Any, Callable, Optional, cast
from reactivex import Observable, operators, compose
from bittrade_huobi_websocket.models.rest.asset_transfer import AssetTransferRequest
from bittrade_huobi_websocket.rest.http_factory_decorator import http_factory
from bittrade_huobi_websocket.models import RequestMessage, endpoints
from bittrade_huobi_websocket.operators.stream import response_messages
from bittrade_huobi_websocket.models.rest import account_accounts


@http_factory
def asset_transfer_http_factory(request: AssetTransferRequest):
    return RequestMessage(
        "POST", endpoints.HuobiEndpoints.ASSET_TRANSFER, params=request.to_dict()
    )
