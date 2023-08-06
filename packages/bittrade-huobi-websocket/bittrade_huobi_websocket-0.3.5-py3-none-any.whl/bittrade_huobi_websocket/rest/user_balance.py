from logging import getLogger
from typing import Callable
from reactivex import Observable, defer, operators, just

def get_user_balance_http_factory():
    return