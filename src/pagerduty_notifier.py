from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

CLIENT = "platsec-compliance-alerting"
CLIENT_URL = f"https://github.com/hmrc/{CLIENT}"

@dataclass
class PagerDutyPayload:
    summary: str
    source: str
    component: str
    event_class: str
    timestamp: str
    custom_details: Dict[str, Any] # = {}
    group: str = None
    severity: str = "critical"


class PagerDutyNotifier:
    def __init__(self, api_url: str, routing_key: str) -> None:
        self.api_url = api_url
        self.routing_key = routing_key

    def _build_event_payload(self, payload: PagerDutyPayload) -> Dict[str, Any]:
        return {
          "payload": {
              "summary": payload.summary,
              "timestamp": payload.timestamp,
              "source": payload.source,
              "component": payload.component,
              "class": payload.event_class,
              "group": payload.group,
              "severity": payload.severity,
              "custom_details": payload.custom_details,
          },
          "routing_key": self.routing_key,
          "event_action": "trigger",
          "client": CLIENT,
          "client_url": CLIENT_URL,
          "links": [],
          "images": [],
        }
        