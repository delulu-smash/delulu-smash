from __future__ import annotations

import time
from typing import Any

from ssbu.logging import logger

__all__ = ["log", "timeit", "toggle_logger"]

# TODO: see if still need
LOG_SCOPES = [
    "ssbu",
    # NOTE: below needed for apps like streamlit
    # as when run `streamlit run app.py`, __name__ = "__main__"
    "__main__",
]


def timeit(func: Any) -> Any:
    """
    Will log execution time of function

    ```python
    TODO: add example
    ```
    """

    # NOTE: below is from: https://loguru.readthedocs.io/en/stable/resources/recipes.html#logging-entry-and-exit-of-functions-with-a-decorator
    # NOTE: not annotating here as internal function and doesn't help much
    def wrapped(*args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug(
            "(exec in {:f} s) {}(args={}, kwargs={})",
            end - start,
            func.__name__,
            args,
            kwargs,
        )
        return result

    return wrapped


def log(func: Any) -> Any:
    """
    Will log input and output values (along with execution time)

    ```python
    # TODO: add example
    ```
    """

    # NOTE: below is from: https://loguru.readthedocs.io/en/stable/resources/recipes.html#logging-entry-and-exit-of-functions-with-a-decorator
    # NOTE: not annontating here as internal function and doesn't help much
    def wrapped(*args, **kwargs):  # noqa: ANN202
        start = time.time()
        name = func.__name__
        logger_ = logger
        logger_.debug("enter: {}(args={}, kwargs={})", name, args, kwargs)
        result = func(*args, **kwargs)
        end = time.time()
        logger_.debug(
            "exit: (exec in {:f} s) {}(args={}, kwargs={}) -> {}",
            end - start,
            name,
            args,
            kwargs,
            result,
        )
        return result

    return wrapped


def _enable_logger() -> None:
    for log_scope in LOG_SCOPES:
        logger.enable(log_scope)


def _disable_logger() -> None:
    for log_scope in LOG_SCOPES:
        logger.disable(log_scope)


def toggle_logger(enable: bool) -> None:
    """Allows easily toggling between enabling/disabling of logger"""
    if enable:
        _enable_logger()
    else:
        _disable_logger()
