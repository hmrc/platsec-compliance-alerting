from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, List

from src.data.exceptions import NotificationMappingException


@dataclass(unsafe_hash=True)
class NotificationMappingConfig:
    channel: str
    buckets: FrozenSet[str]

    def __init__(self, channel: str, buckets: List[str]):
        self.channel = channel
        self.buckets = frozenset(buckets)

    @staticmethod
    def from_dict(notification_mapping: Dict[str, Any]) -> NotificationMappingConfig:
        try:
            return NotificationMappingConfig(**notification_mapping)
        except TypeError as err:
            raise NotificationMappingException(err) from None
