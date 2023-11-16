from base64 import b64encode
from logging import getLogger
from typing import Any, Dict, List, Set

import requests

from src.config.config import Config
from src.data.exceptions import SlackNotifierException
from src.data.finding import Finding

from src.data.slack_message import SlackMessage
from src.findings_filter import FindingsFilter
from src.notification_mapper import NotificationMapper
from src.notifiers.notifier import Notifier


class SlackNotifier(Notifier[SlackMessage, Finding]):
    def __init__(self, config: Config):
        self._logger = getLogger(self.__class__.__name__)
        self._org_client = config.org_client
        self._notifier_config = config.get_slack_notifier_config()
        self._filters_config = config.get_notification_filters()
        self._mappings_config = config.get_notification_mappings()

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
            url=self._notifier_config.api_url,
            headers=self._build_headers(),
            json=message.to_dict(),
            timeout=10,
        )
        response.raise_for_status()
        return dict(response.json())

    def _build_headers(self) -> Dict[str, str]:
        credentials = b64encode(
            f"{self._notifier_config.username}:{self._notifier_config.token}".encode("utf-8")
        ).decode("utf-8")
        return {"Content-Type": "application/json", "Authorization": f"Basic {credentials}"}

    def apply_filters(self, findings: Set[Finding]) -> Set[Finding]:
        return FindingsFilter().do_filter(findings, self._filters_config)

    def apply_mappings(self, findings: Set[Finding]) -> List[SlackMessage]:
        return NotificationMapper().do_map(findings, self._mappings_config, self._org_client)

    # this method should replace send_messages()
    def send(self, notifications: List[SlackMessage]) -> None:
        self._logger.debug("Sending the following messages: %s", notifications)
        self.send_messages(notifications)
