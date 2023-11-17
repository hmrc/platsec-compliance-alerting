from logging import getLogger
from typing import Any, Dict, List, Set

import requests
from src.config.config import Config
from src.data.exceptions import PagerDutyNotifierException
from src.data.pagerduty_event import PagerDutyEvent
from src.data.pagerduty_payload import PagerDutyPayload

from src.notifiers.notifier import Notifier
from src.pagerduty_notification_mapper import PagerDutyNotificationMapper
from src.pagerduty_payload_filter import PagerDutyPayloadFilter


class PagerDutyNotifier(Notifier[PagerDutyEvent, PagerDutyPayload]):
    def __init__(self, config: Config) -> None:
        self.config = config
        self._logger = getLogger(self.__class__.__name__)
        self._notifier_config = config.get_pagerduty_notifier_config()
        self._filters_config = config.get_notification_filters()
        self._mappings_config = config.get_notification_mappings()

    def apply_filters(self, payloads: Set[PagerDutyPayload]) -> Set[PagerDutyPayload]:
        return PagerDutyPayloadFilter().do_filter(payloads, self.config.get_notification_filters())

    def apply_mappings(self, payloads: Set[PagerDutyPayload]) -> List[PagerDutyEvent]:
        return PagerDutyNotificationMapper(ssm_client=self.config.ssm_client).do_map(
            payloads, self.config.get_notification_mappings()
        )

    def send(self, pagerduty_events: List[PagerDutyEvent]) -> None:
        self._logger.debug("Sending the following events: %s", pagerduty_events)
        for event in pagerduty_events:
            try:
                self.send_pagerduty_event(event)
            except PagerDutyNotifierException as ex:
                self._logger.error(f"unable to send event: {event}. Cause: {ex}")

    @staticmethod
    def _handle_response(response: Dict[str, Any], service: str) -> None:
        errors = response.get("errors")
        exclusions = response.get("exclusions")
        if errors or exclusions:
            raise PagerDutyNotifierException(
                f"unable to send event to pagerduty service {service}. Errors: {errors}. Exclusions: {exclusions}"
            )

    def _send(self, pagerduty_event: PagerDutyEvent) -> Dict[str, Any]:
        response = requests.post(
            url=self._notifier_config.api_url,
            headers=self._build_headers(),
            json=pagerduty_event.to_dict(),
            timeout=10,
        )
        response.raise_for_status()
        return dict(response.json())

    def send_pagerduty_event(self, pagerduty_event: PagerDutyEvent) -> None:
        try:
            self._handle_response(
                self._send(pagerduty_event), pagerduty_event.service
            ) if pagerduty_event.service else None
        except requests.RequestException as ex:
            raise PagerDutyNotifierException(
                f"unable to event to pagerduty service {pagerduty_event.service}: {ex}"
            ) from None

    def _build_headers(self) -> Dict[str, str]:
        return {"Accept": "application/json", "Content-Type": "application/json"}
