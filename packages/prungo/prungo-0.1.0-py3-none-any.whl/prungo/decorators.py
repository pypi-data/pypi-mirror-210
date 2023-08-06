import logging
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

from prungo.models import logger_type

P = ParamSpec("P")
T = TypeVar("T")


def log_call(log: logger_type = logging.getLogger("util"), /):
    """log to default logger whenever decorated function is called"""

    def decorator(method: Callable[P, T], /):
        @wraps(method)
        def func(*args: P.args, **kwargs: P.kwargs):
            log_text = f" {method.__name__} "
            log.info(f"{log_text :-^50}")
            return method(*args, **kwargs)

        return func

    return decorator
