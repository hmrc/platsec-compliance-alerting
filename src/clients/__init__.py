from json import JSONDecodeError
from typing import Callable

from botocore.exceptions import BotoCoreError, ClientError

from src import T
from src.data.exceptions import AwsClientException


def boto_try(func: Callable[[], T], except_msg: str) -> T:
    try:
        return func()
    except (BotoCoreError, ClientError, JSONDecodeError, TypeError) as err:
        raise AwsClientException(f"{except_msg}: {err}") from None
