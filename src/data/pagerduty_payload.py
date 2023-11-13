from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional
from src.data.account import Account

from src.data.payload import Payload


class PagerDutySeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

@dataclass
class PagerDutyPayload(Payload):

    def __init__(
        self,
        description: str,
        source: str,
        component: str,
        event_class: str,
        timestamp: str,
        account: Optional[Account] = None,
        region_name: Optional[str] = None,
        group: str = None,
        custom_details: Dict[str, Any] = {},
        severity: PagerDutySeverity = PagerDutySeverity.CRITICAL,
    ):
        self.summary = description
        self.source = source
        self.component = component
        self.event_class = event_class
        self.timestamp = timestamp
        self.custom_details = custom_details
        self.group = group
        self.severity = severity
        super().__init__(description=description, account=account, region_name=region_name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "timestamp": self.timestamp,
            "source": self.source,
            "component": self.component,
            "class": self.event_class,
            "group": self.group,
            "severity": self.severity,
            "custom_details": self.custom_details if self.custom_details else {"account": self.account_name, "region": self.region_name},
        }