
from src.pagerduty_notifier import CLIENT, CLIENT_URL, PagerDutyNotifier, PagerDutyPayload


API_URL="https://pagerduty/api"
ROUTING_KEY="pagerduty-routing-key"

PAYLOAD={
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

def test_build_payload() -> None:
    pagerduty_payload = PagerDutyPayload(
        summary="DISK at 99% on machine prod-datapipe03.example.com",
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
    pagerduty_notifier = PagerDutyNotifier(api_url=API_URL, routing_key=ROUTING_KEY)

    assert PAYLOAD == pagerduty_notifier._build_event_payload(payload=pagerduty_payload)
