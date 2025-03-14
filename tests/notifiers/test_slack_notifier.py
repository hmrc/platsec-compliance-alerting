import logging
from typing import Any, Dict
from unittest.mock import Mock

import httpretty
import json
import pytest
from src.config.slack_notifier_config import SlackNotifierConfig
from src.data.exceptions import SlackNotifierException

from src.data.slack_message import SlackMessage
from src.notifiers.slack_notifier import SlackNotifier


TEST_COLOUR = "some-colour"
SLACK_MESSAGE = SlackMessage(
    ["channel-a", "channel-b"],
    "a-heading",
    "a-title",
    "a-text",
    "#c1e7c6",
    ":test-emoji:",
    "test-service",
)
TEST_SLACK_API_URL = "https://fake-api-url.com/"
API_V2_KEY = "testapiv2key"
SLACK_EMOJI = ":test-emoji:"
SERVICE_NAME = "test-service"


def _create_slack_notifier() -> SlackNotifier:
    slack_notifier_config = SlackNotifierConfig(
        API_V2_KEY,
        TEST_SLACK_API_URL,
        SLACK_EMOJI,
        SERVICE_NAME,
    )
    return SlackNotifier(Mock(get_slack_notifier_config=Mock(return_value=slack_notifier_config)))


def _register_slack_api_success() -> None:
    httpretty.register_uri(
        httpretty.POST,
        TEST_SLACK_API_URL,
        body=json.dumps({"successfullySentTo": ["channel-a", "channel-b"]}),
        status=200,
    )


def _register_slack_api_failure(status: int) -> None:
    httpretty.register_uri(
        httpretty.POST,
        TEST_SLACK_API_URL,
        body=json.dumps({"errors": [{"code": "error", "message": "statusCode: 404, msg: 'channel_not_found'"}]}),
        status=status,
    )


def _assert_headers_correct() -> None:
    headers = httpretty.last_request().headers.items()
    assert ("Content-Type", "application/json") in headers
    assert ("Authorization", API_V2_KEY) in headers


def _assert_payload_correct() -> None:
    assert {
        "channelLookup": {
            "by": "slack-channel",
            "slackChannels": ["channel-a", "channel-b"],
        },
        "displayName": "test-service",
        "emoji": ":test-emoji:",
        "blocks": [{"text": {"text": "a-heading", "type": "mrkdwn"}, "type": "section"}, {"type": "divider"}],
        "callbackChannel": "team-platsec-alerts",
        "text": "",
        "attachments": [
            {
                "color": "#c1e7c6",
                "text": "a-text",
                "title": "a-title",
            }
        ],
    } == json.loads(httpretty.last_request().body)


def _assert_message_request_sent(msg_heading: list[Dict[str, Any]]) -> None:
    assert msg_heading in [req.parsed_body["blocks"] for req in httpretty.latest_requests()]


@httpretty.activate  # type: ignore
def test_send_message() -> None:
    _register_slack_api_success()
    _create_slack_notifier().send_message(SLACK_MESSAGE)
    _assert_headers_correct()
    _assert_payload_correct()


@httpretty.activate  # type: ignore
def test_send_message_with_no_channel() -> None:
    _register_slack_api_success()
    _create_slack_notifier().send_message(
        SlackMessage(["", ""], "a-heading", "a-title", "a-text", TEST_COLOUR, ":test-emoji:", "test-service")
    )
    assert len(httpretty.latest_requests()) == 0, "Message should not have been sent"


@httpretty.activate  # type: ignore
def test_send_messages(caplog: Any) -> None:
    _register_slack_api_success()
    _register_slack_api_failure(500)
    _register_slack_api_success()
    messages = [
        SlackMessage(["channel"], "success-heading-1", "title", "a-text", TEST_COLOUR, ":test-emoji:", "test-service"),
        SlackMessage(["channel"], "failure-heading", "title", "a-text", TEST_COLOUR, ":test-emoji:", "test-service"),
        SlackMessage(["channel"], "success-heading-2", "title", "a-text", TEST_COLOUR, ":test-emoji:", "test-service"),
        SlackMessage(["channel"], "", "title", "a-text", TEST_COLOUR, ":test-emoji:", "test-service"),
    ]
    with caplog.at_level(logging.INFO):
        _create_slack_notifier().send_messages(messages)

    _assert_message_request_sent(
        [{"text": {"text": "success-heading-1", "type": "mrkdwn"}, "type": "section"}, {"type": "divider"}]
    )
    _assert_message_request_sent(
        [{"text": {"text": "failure-heading", "type": "mrkdwn"}, "type": "section"}, {"type": "divider"}]
    )
    _assert_message_request_sent(
        [{"text": {"text": "success-heading-2", "type": "mrkdwn"}, "type": "section"}, {"type": "divider"}]
    )
    _assert_message_request_sent(
        [{"text": {"text": "Unknown Service", "type": "mrkdwn"}, "type": "section"}, {"type": "divider"}]
    )
    assert "failure-heading" in caplog.text
    assert "500" in caplog.text
    assert "success-heading-1" not in caplog.text
    assert "success-heading-2" not in caplog.text


@httpretty.activate  # type: ignore
def test_request_failure() -> None:
    _register_slack_api_failure(403)

    with pytest.raises(SlackNotifierException) as sne:
        _create_slack_notifier().send_message(SLACK_MESSAGE)

    assert sne.match("403")


@httpretty.activate  # type: ignore
def test_slack_failure() -> None:
    _register_slack_api_failure(200)

    with pytest.raises(SlackNotifierException) as sne:
        _create_slack_notifier().send_message(SLACK_MESSAGE)

    assert sne.match("'channel-a', 'channel-b'")
