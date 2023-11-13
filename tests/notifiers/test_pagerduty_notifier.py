
import os
from unittest.mock import Mock, patch
from src.config.config import Config
from src.config.pagerduty_notifier_config import PagerDutyNotifierConfig
from src.notifiers.pagerduty_notifier import CLIENT, CLIENT_URL, PagerDutyNotifier, PagerDutyPayload


API_URL="https://pagerduty/api"
ROUTING_KEY="pagerduty-routing-key"

PAGERDUTY_EVENT={
  "payload": {
    "summary": "DISK at 99% on machine prod-datapipe03.example.com",
    "timestamp": "2015-07-17T08:42:58.315",
    "severity": "critical",
    "source": "prod-datapipe03.example.com",
    "component": "mysql",
    "group": "prod-datapipe",
    "class": "disk",
    "custom_details": {
      "free space": "1%",
      "ping time": "1500ms",
      "load avg": 0.75
    }
  },
  "routing_key": ROUTING_KEY,
  "event_action": "trigger",
  "client": CLIENT,
  "client_url": CLIENT_URL,
  "links": [],
  "images": []
}

def test_build_pagerduty_event() -> None:
    pagerduty_notifier_config = PagerDutyNotifierConfig(
        service="pd-service",
        routing_key=ROUTING_KEY,
        api_url=API_URL
    )
    pagerduty_payload = PagerDutyPayload(
        description="DISK at 99% on machine prod-datapipe03.example.com",
        timestamp="2015-07-17T08:42:58.315",
        source="prod-datapipe03.example.com",
        component="mysql",
        group="prod-datapipe",
        event_class="disk",
        custom_details={
            "free space": "1%",
            "ping time": "1500ms",
            "load avg": 0.75
        }
    )
    mock_config = Mock(
        get_pagerduty_notifier_config=Mock(return_value=pagerduty_notifier_config),
        get_notification_filters=Mock(),
        get_notification_mappings=Mock(),
        org_client=Mock(),
    )
    pagerduty_notifier = PagerDutyNotifier(mock_config)

    assert PAGERDUTY_EVENT == pagerduty_notifier._build_event(payload=pagerduty_payload).to_dict()
