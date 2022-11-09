import base64
import logging
from typing import Any

import httpretty
import json
import pytest

from src.slack_notifier import SlackMessage, SlackNotifier, SlackNotifierConfig, SlackNotifierException

TEST_COLOUR = "some-colour"
SLACK_MESSAGE = SlackMessage(["channel-a", "channel-b"], "a-header", "a-title", "a-text", "#c1e7c6")
API_URL = "https://fake-api-url.com/"
USER = "user"
USER_PASS = "token"
BASIC_AUTH = base64.b64encode(f"{USER}:{USER_PASS}".encode("utf-8")).decode("utf-8")


def _create_slack_notifier() -> SlackNotifier:
    return SlackNotifier(SlackNotifierConfig(USER, USER_PASS, API_URL))


def _register_slack_api_success() -> None:
    httpretty.register_uri(
        httpretty.POST,
        API_URL,
        body=json.dumps({"successfullySentTo": ["channel-a", "channel-b"]}),
        status=200,
    )


def _register_slack_api_failure(status: int) -> None:
    httpretty.register_uri(
        httpretty.POST,
        API_URL,
        body=json.dumps({"errors": [{"code": "error", "message": "statusCode: 404, msg: 'channel_not_found'"}]}),
        status=status,
    )


def _assert_headers_correct() -> None:
    headers = httpretty.last_request().headers.items()
    assert ("Content-Type", "application/json") in headers
    assert ("Authorization", f"Basic {BASIC_AUTH}") in headers  # base64 of "user:token"


def _assert_payload_correct() -> None:
    assert {
        "channelLookup": {
            "by": "slack-channel",
            "slackChannels": ["channel-a", "channel-b"],
        },
        "messageDetails": {
            "text": "a-header",
            "attachments": [
                {
                    "color": "#c1e7c6",
                    "title": "a-title",
                    "text": "a-text",
                }
            ],
        },
    } == json.loads(httpretty.last_request().body)


def _assert_message_request_sent(msg_header: str) -> None:
    assert msg_header in [req.parsed_body["messageDetails"]["text"] for req in httpretty.latest_requests()]


@httpretty.activate  # type: ignore
def test_send_message() -> None:
    _register_slack_api_success()
    _create_slack_notifier().send_message(SLACK_MESSAGE)
    _assert_headers_correct()
    _assert_payload_correct()


@httpretty.activate  # type: ignore
def test_send_message_with_no_channel() -> None:
    _register_slack_api_success()
    _create_slack_notifier().send_message(SlackMessage(["", ""], "a-header", "a-title", "a-text", TEST_COLOUR))
    assert len(httpretty.latest_requests()) == 0, "Message should not have been sent"


@httpretty.activate  # type: ignore
def test_send_messages(caplog: Any) -> None:
    _register_slack_api_success()
    _register_slack_api_failure(500)
    _register_slack_api_success()
    messages = [
        SlackMessage(["channel"], "success-header-1", "title", "text", TEST_COLOUR),
        SlackMessage(["channel"], "failure-header", "title", "text", TEST_COLOUR),
        SlackMessage(["channel"], "success-header-2", "title", "text", TEST_COLOUR),
    ]

    with caplog.at_level(logging.INFO):
        _create_slack_notifier().send_messages(messages)

    _assert_message_request_sent("success-header-1")
    _assert_message_request_sent("success-header-2")
    _assert_message_request_sent("failure-header")
    assert "failure-header" in caplog.text
    assert "500" in caplog.text
    assert "success-header-1" not in caplog.text
    assert "success-header-2" not in caplog.text


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
