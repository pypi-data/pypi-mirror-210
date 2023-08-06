from os import getenv
from typing import Literal
import requests
import reactivex
from reactivex.disposable import Disposable
from logging import getLogger
from bittrade_huobi_websocket import models

MARKET_URL = getenv("HUOBI_HTTP_MARKET_URL", "https://api.huobi.pro")

session = requests.Session()

logger = getLogger(__name__)


def prepare_request(message: models.RequestMessage) -> requests.models.Request:
    http_method = message.method
    kwargs = {}
    if http_method == "GET":
        kwargs["params"] = message.params
    if http_method == "POST":
        kwargs["json"] = message.params

    # There are (few) cases where the endpoint must be a string; "handle" that below
    try:
        endpoint = message.endpoint.value
    except:
        endpoint = message.endpoint
    return requests.Request(http_method, f"{MARKET_URL}{endpoint}", **kwargs)


def send_request(request: requests.models.Request) -> reactivex.Observable:
    def subscribe(
        observer: reactivex.abc.ObserverBase,
        scheduler: reactivex.abc.SchedulerBase | None = None,
    ) -> reactivex.abc.DisposableBase:
        response = session.send(request.prepare())
        if response.ok:
            body = response.json()
            if (
                "status" in body
                and body["status"] == "ok"
                or "ok" in body
                and body["ok"]
            ):
                observer.on_next(body)
                observer.on_completed()
            else:
                observer.on_error(body)
        else:
            try:
                logger.error(
                    "Error with request %s; request was %s",
                    response.text,
                    response.request.body
                    if request.method == "POST"
                    else response.request.headers,
                )
                response.raise_for_status()
            except Exception as exc:
                observer.on_error(exc)
        return Disposable()

    return reactivex.Observable(subscribe)
