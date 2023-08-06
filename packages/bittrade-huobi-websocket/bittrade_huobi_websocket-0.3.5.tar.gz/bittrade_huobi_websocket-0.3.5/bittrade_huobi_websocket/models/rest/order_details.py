from typing import TypedDict

OrderDetails = TypedDict("OrderDetails", {
    "id": int,
    "symbol": str,
    "account-id": int,
    "client-order-id": str,
    "amount": str,
    "price": str,
    "created-at": int,
    "type": str,
    "field-amount": str,
    "field-cash-amount": str,
    "field-fees": str,
    "finished-at": int,
    "source": str,
    "state": str,
    "canceled-at": int,
})