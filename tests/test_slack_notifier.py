from unittest import TestCase

import httpretty
import json

from src.slack_notifier import SlackMessage, SlackNotifier, SlackNotifierException


@httpretty.activate
class TestSlackNotifier(TestCase):
    def setUp(self) -> None:
        self.slack_message = SlackMessage(["channel-a", "channel-b"], "a-header", "a-text", "a-title", "#c1e7c6")
        self.api_url = "https://fake-api-url.com/"
        self.slack_notifier = SlackNotifier("user", "token", self.api_url)

    def test_send_message(self) -> None:
        self._register_slack_api_success()
        self.slack_notifier.send_message(self.slack_message)
        self._assert_headers_correct()
        self._assert_payload_correct()

    def test_request_failure(self) -> None:
        self._register_slack_api_failure(403)
        with self.assertRaisesRegex(SlackNotifierException, "403"):
            self.slack_notifier.send_message(self.slack_message)

    def test_slack_failure(self) -> None:
        self._register_slack_api_failure(200)
        with self.assertRaisesRegex(SlackNotifierException, r"['channel\-a', 'channel\-b']"):
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
