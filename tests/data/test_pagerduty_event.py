from tests.test_types_generator import _pagerduty_event, _pagerduty_payload


def test_pagerduty_event_to_dict() -> None:
    payload = _pagerduty_payload(source="111122223333", component="component-a")
    event = _pagerduty_event(payload=payload, service="pd-service")
    expected = {
        "payload": {
            "summary": "A description of the event",
            "timestamp": "2022-06-03T06:27:57Z",
            "source": "111122223333",
            "component": "component-a",
            "class": "eventTypeCode",
            "group": "EC2",
            "severity": "critical",
            "custom_details": {"account": "", "region": "a-region"},
        },
        "routing_key": "pd-service-routing-key",
        "event_action": "trigger",
        "client": "platsec-compliance-alerting",
        "client_url": "https://github.com/hmrc/platsec-compliance-alerting",
        "links": [],
        "images": [],
    }
    assert expected == event.to_dict()
