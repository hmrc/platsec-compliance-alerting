import json
import logging
from typing import Any
from unittest.mock import Mock

import httpretty
import pytest
from src.config.notification_filter_config import NotificationFilterConfig
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.exceptions import PagerDutyNotifierException
from src.notifiers.pagerduty_notifier import PagerDutyNotifier
from tests.test_types_generator import _pagerduty_payload, _pagerduty_event


API_URL = "https://pagerduty/api"
ROUTING_KEY = "pagerduty-routing-key"


def _register_pagerduty_api_success() -> None:
    httpretty.register_uri(
        httpretty.POST,
        API_URL,
        body=json.dumps({"status": "success", "message": "Event processed", "dedup_key": "srv01/HTTP"}),
        status=200,
    )


def _register_slack_api_failure(status: int) -> None:
    httpretty.register_uri(
        httpretty.POST,
        API_URL,
        body=json.dumps(
            {
                "status": "Unrecognized object",
                "message": "Event object format is unrecognized",
                "errors": ["JSON parse error"],
            }
        ),
        status=status,
    )


def __assert_payload_correct(source: str, component: str, routing_key: str) -> None:
    assert (source, component, routing_key) in [
        (req.parsed_body["payload"]["source"], req.parsed_body["payload"]["component"], req.parsed_body["routing_key"])
        for req in httpretty.latest_requests()
    ]


def test_apply_filters() -> None:
    filters = {NotificationFilterConfig(item="dynamodb-resource-id", reason="good reason")}
    mock_config = Mock(get_notification_filters=Mock(return_value=filters))

    payload_1 = _pagerduty_payload(source="111122223333", component="mysql-resource-id")
    payload_2 = _pagerduty_payload(source="444455556666", component="dynamodb-resource-id")

    expected = {payload_1}
    actual = PagerDutyNotifier(mock_config).apply_filters(payloads={payload_1, payload_2})

    assert expected == actual


def test_apply_mappings() -> None:
    mappings = {NotificationMappingConfig(channel="central", pagerduty_service="service-0")}
    mock_config = Mock(
        get_notification_mappings=Mock(return_value=mappings),
        ssm_client=Mock(get_parameter=Mock(return_value="service-0-routing-key")),
    )

    payload_1 = _pagerduty_payload(source="111122223333", component="mysql-resource-id")
    payload_2 = _pagerduty_payload(source="444455556666", component="dynamodb-resource-id")

    expected = [
        _pagerduty_event(payload=payload_1, service="service-0"),
        _pagerduty_event(payload=payload_2, service="service-0"),
    ]
    actual = PagerDutyNotifier(mock_config).apply_mappings(payloads={payload_1, payload_2})

    assert expected == actual


@httpretty.activate  # type: ignore
def test_send_pagerduty_event_success(caplog: Any) -> None:
    _register_pagerduty_api_success()

    pagerduty_event = _pagerduty_event(
        payload=_pagerduty_payload(source="111122223333", component="mysql-resource-id"), service="pd-service"
    )
    mock_config = Mock(get_pagerduty_api_url=Mock(return_value=API_URL))
    PagerDutyNotifier(mock_config).send_pagerduty_event(pagerduty_event=pagerduty_event)

    __assert_payload_correct(source="111122223333", component="mysql-resource-id", routing_key="pd-service-routing-key")


@httpretty.activate  # type: ignore
def test_send_pagerduty_event_failure() -> None:
    _register_slack_api_failure(500)

    pagerduty_event = _pagerduty_event(
        payload=_pagerduty_payload(source="111122223333", component="mysql-resource-id"), service="pd-service"
    )
    mock_config = Mock(get_pagerduty_api_url=Mock(return_value=API_URL))

    with pytest.raises(PagerDutyNotifierException):
        PagerDutyNotifier(mock_config).send_pagerduty_event(pagerduty_event=pagerduty_event)


def test_handle_response() -> None:
    response = {"errors": ["error-1", "error-2"]}
    with pytest.raises(PagerDutyNotifierException):
        PagerDutyNotifier(Mock())._handle_response(response=response, service="the-service")

    response = {"exclusions": ["exclusion-1", "exclusion-2"]}
    with pytest.raises(PagerDutyNotifierException):
        PagerDutyNotifier(Mock())._handle_response(response=response, service="the-service")


@httpretty.activate  # type: ignore
def test_send_multiple_pagerduty_event_success() -> None:
    _register_pagerduty_api_success()

    pagerduty_events = [
        _pagerduty_event(
            payload=_pagerduty_payload(source="111122223333", component="mysql-resource-id"), service="pd-service"
        ),
        _pagerduty_event(
            payload=_pagerduty_payload(source="111122223333", component="dynamodb-resource-id"), service="pd-service"
        ),
    ]

    mock_config = Mock(get_pagerduty_api_url=Mock(return_value=API_URL))
    PagerDutyNotifier(mock_config).send(pagerduty_events=pagerduty_events)

    __assert_payload_correct(source="111122223333", component="mysql-resource-id", routing_key="pd-service-routing-key")
    __assert_payload_correct(
        source="111122223333", component="dynamodb-resource-id", routing_key="pd-service-routing-key"
    )


@httpretty.activate  # type: ignore
def test_send_multiple_pagerduty_event_failure(caplog: Any) -> None:
    _register_slack_api_failure(500)

    pagerduty_events = [
        _pagerduty_event(
            payload=_pagerduty_payload(source="111122223333", component="mysql-resource-id"), service="pd-service"
        ),
        _pagerduty_event(
            payload=_pagerduty_payload(source="111122223333", component="dynamodb-resource-id"), service="pd-service"
        ),
    ]
    mock_config = Mock(get_pagerduty_api_url=Mock(return_value=API_URL))

    with caplog.at_level(logging.ERROR):
        PagerDutyNotifier(mock_config).send(pagerduty_events=pagerduty_events)

    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "ERROR"
    assert "unable to event to pagerduty service pd-service" in caplog.text
