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


@dataclass(unsafe_hash=True)
class PagerDutyPayload(Payload):
    def __init__(
        self,
        compliance_item_type: str,  # this gives a way to map pd_service to notification and by extension routing_key
        description: str,
        source: str,
        component: str,
        event_class: str,
        timestamp: str,
        account: Optional[Account] = None,
        region_name: Optional[str] = None,
        group: Optional[str] = None,
        custom_details: Dict[str, Any] = {},
        severity: PagerDutySeverity = PagerDutySeverity.CRITICAL,
    ):
        self.compliance_item_type = compliance_item_type
        self.summary = description
        self.source = source
        self.component = component
        self.event_class = event_class
        self.timestamp = timestamp
        self.custom_details = custom_details
        self.group = group
        self.severity = severity
        super().__init__(description=description, account=account, region_name=region_name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PagerDutyPayload):
            return (
                self.compliance_item_type == other.compliance_item_type
                and self.summary == other.summary
                and self.source == other.source
                and self.component == other.component
                and self.event_class == other.event_class
                and self.timestamp == other.timestamp
                and self.custom_details == other.custom_details
                and self.account == other.account
                and self.region_name == other.region_name
            )
        return False

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"compliance_item_type={self.compliance_item_type}, "
            f"summary={self.summary}, "
            f"source={self.source}, "
            f"component={self.component}, "
            f"event_class={self.event_class}, "
            f"timestamp={self.timestamp}, "
            f"custom_details={self.custom_details}, "
            f"account={self.account}, "
            f"region_name={self.region_name}"
            ")"
        )

    def to_dict(self) -> Dict[str, Any]:
        default_custom_details = {"account": self.account_name, "region": self.region_name}
        return {
            "summary": self.summary,
            "timestamp": self.timestamp,
            "source": self.source,
            "component": self.component,
            "class": self.event_class,
            "group": self.group,
            "severity": self.severity.value,
            "custom_details": self.custom_details if self.custom_details else default_custom_details,
        }
