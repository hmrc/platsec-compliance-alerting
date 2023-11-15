from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, FrozenSet, List

from src.data.exceptions import NotificationMappingException


@dataclass(unsafe_hash=True)
class NotificationMappingConfig:
    channel: str
    pagerduty_service: Optional[str]
    accounts: FrozenSet[str]
    items: FrozenSet[str]
    compliance_item_types: FrozenSet[str]

    def __init__(
        self,
        channel: str,
        pagerduty_service: Optional[str] = None,
        accounts: Optional[List[str]] = None,
        items: Optional[List[str]] = None,
        compliance_item_types: Optional[List[str]] = None,
    ):
        self.channel = channel
        self.pagerduty_service = pagerduty_service
        self.accounts = frozenset(accounts or {})
        self.items = frozenset(items or {})
        self.compliance_item_types = frozenset(compliance_item_types or {})

    @staticmethod
    def from_dict(notification_mapping: Dict[str, Any]) -> NotificationMappingConfig:
        try:
            return NotificationMappingConfig(**notification_mapping)
        except TypeError as err:
            raise NotificationMappingException(err) from None
