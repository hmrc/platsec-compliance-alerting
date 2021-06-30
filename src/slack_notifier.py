from base64 import b64encode
from logging import getLogger
from typing import Any, Dict, List

import requests

from dataclasses import dataclass


@dataclass
class SlackMessage:
    channels: List[str]
    header: str
    title: str
    text: str
    color: str

    def __init__(self, channels: List[str], header: str, title: str, text: str, color: str = "#36a64f"):
        self.channels = list(filter(None, channels))
        self.header = header
        self.title = title
        self.text = text
        self.color = color


@dataclass
class SlackNotifierConfig:
    username: str
    token: str
    api_url: str


class SlackNotifierException(Exception):
    pass


class SlackNotifier:
    def __init__(self, config: SlackNotifierConfig):
        self._logger = getLogger(self.__class__.__name__)
        self._username = config.username
        self._token = config.token
        self._api_url = config.api_url

    def send_messages(self, messages: List[SlackMessage]) -> None:
        for message in messages:
            try:
                self.send_message(message)
            except SlackNotifierException as ex:
                self._logger.error(f"unable to send message: {message}. Cause: {ex}")

    def send_message(self, message: SlackMessage) -> None:
        try:
            self._handle_response(self._send(message), message.channels) if message.channels else None
        except requests.RequestException as ex:
            raise SlackNotifierException(f"unable to send message to channels {message.channels}: {ex}") from None

    @staticmethod
    def _handle_response(response: Dict[str, Any], channels: List[str]) -> None:
        errors = response.get("errors")
        exclusions = response.get("exclusions")
        if errors or exclusions:
            raise SlackNotifierException(
                f"unable to send message to channels {channels}. Errors: {errors}. Exclusions: {exclusions}"
            )

    def _send(self, message: SlackMessage) -> Dict[str, Any]:
        response = requests.post(
            url=self._api_url,
            headers=self._build_headers(),
            json=self._build_payload(message),
            timeout=10,
        )
        response.raise_for_status()
        return dict(response.json())

    def _build_headers(self) -> Dict[str, str]:
        credentials = b64encode(f"{self._username}:{self._token}".encode("utf-8")).decode("utf-8")
        return {"Content-Type": "application/json", "Authorization": f"Basic {credentials}"}

    @staticmethod
    def _build_payload(message: SlackMessage) -> Dict[str, Any]:
        return {
            "channelLookup": {
                "by": "slack-channel",
                "slackChannels": message.channels,
            },
            "messageDetails": {
                "text": message.header,
                "attachments": [
                    {
                        "color": message.color,
                        "title": message.title,
                        "text": message.text,
                    }
                ],
            },
        }
