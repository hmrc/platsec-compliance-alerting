from dataclasses import dataclass
from typing import Any, Dict, List

from src.data.notification import Notification
from src.data.pagerduty_payload import PagerDutyPayload


@dataclass(unsafe_hash=True)
class PagerDutyEvent(Notification):
    payload: PagerDutyPayload
    routing_key: str
    event_action: str
    client: str
    client_url: str
    links: List[Dict[str, str]] = None
    images: List[Dict[str, str]] = None
    service: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "payload": self.payload.to_dict(),
            "routing_key": self.routing_key,
            "event_action": self.event_action,
            "client": self.client,
            "client_url": self.client_url,
            "links": self.links,
            "images": self.images,
        }
