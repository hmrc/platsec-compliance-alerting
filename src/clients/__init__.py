from typing import Callable, TypeVar

from botocore.exceptions import BotoCoreError, ClientError

from src.data.exceptions import AwsClientException

T = TypeVar("T")


def boto_try(func: Callable[[], T], except_msg: str) -> T:
    try:
        return func()
    except (BotoCoreError, ClientError) as err:
        raise AwsClientException(f"{except_msg}: {err}") from None
