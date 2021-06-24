from unittest import TestCase

from contextlib import redirect_stderr
from io import StringIO

import httpretty
import json

from src.slack_notifier import SlackMessage, SlackNotifier, SlackNotifierConfig, SlackNotifierException


@httpretty.activate
class TestSlackNotifier(TestCase):
    def setUp(self) -> None:
        self.slack_message = SlackMessage(["channel-a", "channel-b"], "a-header", "a-title", "a-text", "#c1e7c6")
        self.api_url = "https://fake-api-url.com/"
        self.slack_notifier = SlackNotifier(SlackNotifierConfig("user", "token", self.api_url))

    def test_send_message(self) -> None:
        self._register_slack_api_success()
        self.slack_notifier.send_message(self.slack_message)
        self._assert_headers_correct()
        self._assert_payload_correct()

    def test_send_messages(self) -> None:
        self._register_slack_api_success()
        self._register_slack_api_failure(500)
        self._register_slack_api_success()
        messages = [
            SlackMessage(["channel"], "success-header-1", "title", "text"),
            SlackMessage(["channel"], "failure-header", "title", "text"),
            SlackMessage(["channel"], "success-header-2", "title", "text"),
        ]
        with redirect_stderr(StringIO()) as err:
            self.slack_notifier.send_messages(messages)
        self._assert_message_request_sent("success-header-1")
        self._assert_message_request_sent("success-header-2")
        self._assert_message_request_sent("failure-header")
        self.assertIn("failure-header", err.getvalue().strip())
        self.assertIn("500", err.getvalue().strip())
        self.assertNotIn("success-header-1", err.getvalue().strip())
        self.assertNotIn("success-header-2", err.getvalue().strip())

    def test_request_failure(self) -> None:
        self._register_slack_api_failure(403)
        with self.assertRaisesRegex(SlackNotifierException, "403"):
            self.slack_notifier.send_message(self.slack_message)

    def test_slack_failure(self) -> None:
        self._register_slack_api_failure(200)
        with self.assertRaisesRegex(SlackNotifierException, "'channel-a', 'channel-b'"):
            self.slack_notifier.send_message(self.slack_message)

    def _register_slack_api_success(self) -> None:
        httpretty.register_uri(
            httpretty.POST,
            self.api_url,
            body=json.dumps({"successfullySentTo": ["channel-a", "channel-b"]}),
            status=200,
        )

    def _register_slack_api_failure(self, status: int) -> None:
        httpretty.register_uri(
            httpretty.POST,
            self.api_url,
            body=json.dumps({"errors": [{"code": "error", "message": "statusCode: 404, msg: 'channel_not_found'"}]}),
            status=status,
        )

    def _assert_headers_correct(self) -> None:
        headers = httpretty.last_request().headers.items()
        self.assertIn(("Content-Type", "application/json"), headers)
        self.assertIn(("Authorization", "Basic dXNlcjp0b2tlbg=="), headers)  # base64 of "user:token"

    def _assert_payload_correct(self) -> None:
        self.assertEqual(
            {
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
            },
            json.loads(httpretty.last_request().body),
        )

    def _assert_message_request_sent(self, msg_header: str) -> None:
        self.assertIn(msg_header, [req.parsed_body["messageDetails"]["text"] for req in httpretty.latest_requests()])
