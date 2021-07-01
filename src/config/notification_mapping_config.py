from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, FrozenSet, List

from src.data.account import Account
from src.data.exceptions import NotificationMappingException


@dataclass(unsafe_hash=True)
class NotificationMappingConfig:
    channel: str
    account: Optional[Account]
    items: Optional[FrozenSet[str]]

    def __init__(self, channel: str, account: Optional[str] = None, items: Optional[List[str]] = None):
        self.channel = channel
        self.account = Account(identifier=account) if account else None
        self.items = frozenset(items or {})

    @staticmethod
    def from_dict(notification_mapping: Dict[str, Any]) -> NotificationMappingConfig:
        try:
            return NotificationMappingConfig(**notification_mapping)._validate()
        except TypeError as err:
            raise NotificationMappingException(err) from None

    def _validate(self) -> NotificationMappingConfig:
        if (self.account and not self.items) or (self.items and not self.account):
            return self
        raise NotificationMappingException("mapping config requires a channel and only one of [account|items]")
