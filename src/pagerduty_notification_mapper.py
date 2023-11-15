from typing import List, Set, Optional

from src.clients.aws_org_client import AwsOrgClient
from src.clients.aws_ssm_client import AwsSsmClient
from src.data.account import Account
from src.data.finding import Finding
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.pagerduty_event import PagerDutyEvent
from src.data.pagerduty_payload import PagerDutyPayload
from src.data.slack_message import SlackMessage

CLIENT = "platsec-compliance-alerting"
CLIENT_URL = f"https://github.com/hmrc/{CLIENT}"
EVENT_ACTION="trigger"
PAGERDUTY_SSM_PARAMETER_STORE_PREFIX = "/pagerduty/"


class PagerDutyNotificationMapper:
    def __init__(self, ssm_client: AwsSsmClient) -> None:
        self.ssm_client = ssm_client

    def do_map(
        self, notifications: Set[PagerDutyPayload], mappings: Set[NotificationMappingConfig],
    ) -> List[PagerDutyEvent]:
        events = [
            PagerDutyEvent(
                payload = notification,
                routing_key = routing_key,
                event_action = "trigger",
                client = CLIENT,
                client_url = CLIENT_URL,
                links = [],
                images = [],
            )
            for notification in notifications
            for routing_key in self._find_routing_keys(notification, mappings)
        ]
        return sorted(events, key=lambda msg: (msg.payload.source, msg.payload.component, msg.routing_key))

    def _pagerduty_ssm_parameter_name(self, service: str) -> str:
        return f"{PAGERDUTY_SSM_PARAMETER_STORE_PREFIX}{service}"

    def _get_pagerduty_service_routing_key(self, service: str) -> str:
        return self.ssm_client.get_parameter(parameter_name=self._pagerduty_ssm_parameter_name(service))

    def _find_routing_keys(self, notification: PagerDutyPayload, mappings: Set[NotificationMappingConfig]) -> Set[str]:
        return {
            self._get_pagerduty_service_routing_key(mapping.pagerduty_service)
            for mapping in mappings
            if (not mapping.accounts or (notification.account and notification.account.identifier in mapping.accounts))
            and (
                not mapping.compliance_item_types or notification.compliance_item_type in mapping.compliance_item_types
            )
        }