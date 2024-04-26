import logging
from typing import Any
from unittest.mock import Mock

import httpretty
import json
import pytest
from src.config.slack_notifier_config import SlackNotifierConfig
from src.data.exceptions import SlackNotifierException

from src.data.slack_message import SlackMessage
from src.notifiers.slack_notifier import SlackNotifier


TEST_COLOUR = "some-colour"
SLACK_MESSAGE = SlackMessage(["channel-a", "channel-b"], "a-header", "a-title", "a-text", "#c1e7c6")
TEST_SLACK_API_URL = "https://fake-api-url.com/"
API_V2_KEY = "testapiv2key"


# def helper_expected_block(text):
#     block_header = {"type": "section",
#                     "text": {"type": "mrkdwn", "text": "a-header"}}
#     block_body = {"type": "section", "text": {"type": "mrkdwn", "text": text}}
#     return json.loads(block_header, block_body)


def _create_slack_notifier() -> SlackNotifier:
    slack_notifier_config = SlackNotifierConfig(API_V2_KEY, TEST_SLACK_API_URL)
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
        "displayName": "a-title",
        "emoji": ":this-is-fine:",
        "blocks": ["a-header", '{"type": "section", "text": {"type": "mrkdwn", "text": "a-text"}}'],
        "attachments": [
            {
                "color": "#c1e7c6",
                "title": "a-title",
                "text": "a-text",
            }
        ],
    } == json.loads(httpretty.last_request().body)


def _assert_message_request_sent(msg_header: list[str]) -> None:
    assert msg_header in [req.parsed_body["blocks"] for req in httpretty.latest_requests()]


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

    _assert_message_request_sent(
        ["success-header-1", '{"type": "section", "text": {"type": "mrkdwn", "text": "text"}}']
    )
    _assert_message_request_sent(
        ["success-header-2", '{"type": "section", "text": {"type": "mrkdwn", "text": "text"}}']
    )
    _assert_message_request_sent(["failure-header", '{"type": "section", "text": {"type": "mrkdwn", "text": "text"}}'])
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
