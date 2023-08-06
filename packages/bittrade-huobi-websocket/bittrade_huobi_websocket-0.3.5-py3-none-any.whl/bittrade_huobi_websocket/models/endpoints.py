from enum import Enum


class HuobiEndpoints(Enum):
    # v1 endpoints
    ACCOUNT_ACCOUNT_HISTORY = "/v1/account/history"
    ACCOUNT_ACCOUNTS = "/v1/account/accounts"
    ACCOUNT_INFO = "/v1/api/account"
    ASSET_TRANSFER = "/v1/account/transfer"
    CANCEL_ORDER = "/v1/order/orders/{}/submitcancel"
    ORDER_DETAILS = "/v1/order/orders/{}"
    CANCEL_ORDER_BATCH = "/v1/order/orders/batchCancelOpenOrders"
    CREATE_ORDER = "/v1/order/orders/place"
    GET_ALL_OPEN_ORDERS = "/v1/order/openOrders"
    GET_ACCOUNT_BALANCE = "/v1/account/accounts/{}/balance"
    MARKET_DEPTH = "/market/depth"
    MARKET_KLINE = "/market/kline"
    MARKET_TRADE = "/market/trade"
    ORDER_HISTORY = "/v1/api/order_history"
    ORDER_INFO = "/v1/api/order_info"
    TICKER_DETAIL = "/v1/market/detail"

    # v2 endpoints
    V2_ACCOUNT_BALANCE = "/v2/account/balance"
    V2_GET_UID = "/v2/user/uid"
    V2_ORDER_CREATE = "/v2/order/orders/place"
    V2_ORDER_CANCEL = "/v2/order/orders/{order_id}/submitcancel"
    V2_ORDER_DETAILS = "/v2/order/orders/{order_id}"
    V2_ORDER_MATCH_RESULTS = "/v2/order/matchresults"
    V2_ORDER_HISTORY = "/v2/order/history"
    V2_WITHDRAW_CREATE = "/v2/account/withdraw"
    V2_WITHDRAW_DETAILS = "/v2/account/withdraw/{withdraw_id}"
    V2_WITHDRAW_HISTORY = "/v2/account/withdraw/history"
    V2_DEPOSIT_ADDRESS = "/v2/account/deposit/address"
    V2_DEPOSIT_HISTORY = "/v2/account/deposit/history"
