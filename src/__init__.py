from logging import getLogger
from typing import Any, TypeVar

T = TypeVar("T")


def error(caller: Any, msg: Exception) -> None:
    getLogger(caller.__class__.__name__).error(msg)
