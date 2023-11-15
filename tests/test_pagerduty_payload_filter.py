from src.config.notification_filter_config import NotificationFilterConfig
from src.pagerduty_payload_filter import PagerDutyPayloadFilter

from tests.test_types_generator import _pagerduty_payload

payload_1 = _pagerduty_payload(source="111122223333", component="mysql-resource-id")
payload_2 = _pagerduty_payload(source="444455556666", component="dynamodb-resource-id")

payload_filter = NotificationFilterConfig(item="dynamodb-resource-id", reason="good reason")


def test_do_filter() -> None:
    payloads = {payload_1, payload_2}
    assert {payload_1} == PagerDutyPayloadFilter.do_filter(payloads=payloads, filters={payload_filter})


def test_do_filter_empty_filters() -> None:
    payloads = {payload_1, payload_2}
    assert payloads == PagerDutyPayloadFilter.do_filter(payloads=payloads, filters=set())


def test_do_filter_empty_payloads() -> None:
    assert set() == PagerDutyPayloadFilter.do_filter(payloads=set(), filters={payload_filter})
