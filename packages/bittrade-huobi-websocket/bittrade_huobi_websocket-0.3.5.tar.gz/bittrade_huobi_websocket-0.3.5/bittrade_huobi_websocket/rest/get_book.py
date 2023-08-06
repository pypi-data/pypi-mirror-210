from decimal import Decimal
from typing import Any, Callable

from bittrade_huobi_websocket.connection.http import prepare_request, send_request

from bittrade_huobi_websocket.models.rest import market_depth
from bittrade_huobi_websocket.models import endpoints
from bittrade_huobi_websocket.models.request import RequestMessage
from reactivex import operators, compose, Observable
from elm_framework_helpers.unified.models.book import TopPrices


def get_book_http(params: market_depth.MarketDepthParams):
    return send_request(
        prepare_request(
            RequestMessage(
                method="GET",
                endpoint=endpoints.HuobiEndpoints.MARKET_DEPTH,
                params={
                    "symbol": params.symbol,
                    "depth": params.depth.value,
                    "type": params.type.value,
                },
            )
        )
    )


def map_to_market_response() -> Callable[
    [Observable[dict]], Observable[market_depth.MarketDepthResponse]
]:
    return compose(operators.map(lambda x: market_depth.MarketDepthResponse(**x)))


def map_to_raw_orderbook() -> Callable[[Observable[dict]], Observable[Any]]:
    return compose(
        map_to_market_response(),
        operators.map(lambda x: x.tick),
    )


def map_top_prices() -> Callable[[Observable[dict]], Observable[Any]]:
    def map_top_prices_(x: market_depth.RawOrderbook):
        return TopPrices(Decimal(str(x["bids"][0][0])), Decimal(str(x["asks"][0][0])))

    return compose(map_to_raw_orderbook(), operators.map(map_top_prices_))
