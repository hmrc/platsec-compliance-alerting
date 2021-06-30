from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from src.data.exceptions import FilterConfigException


@dataclass(frozen=True)
class NotificationFilterConfig:
    item: str
    reason: str

    @staticmethod
    def from_dict(filter_config: Dict[str, str]) -> NotificationFilterConfig:
        try:
            return NotificationFilterConfig(**filter_config)
        except TypeError as err:
            raise FilterConfigException(err) from None
