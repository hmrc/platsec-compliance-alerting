from typing import List, Set, Optional

from src.clients.aws_org_client import AwsOrgClient
from src.data.account import Account
from src.data.finding import Finding
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.slack_message import SlackMessage
from src.config.config import Config


class NotificationMapper:
    def do_map(
        self, notifications: Set[Finding], mappings: Set[NotificationMappingConfig], org_client: AwsOrgClient
    ) -> List[SlackMessage]:
        return sorted(
            [
                SlackMessage(
                    channels=sorted(NotificationMapper._find_channels(notification, mappings)),
                    heading=self.build_heading(org_client, notification.region_name, notification.account),
                    title=notification.item,
                    text=NotificationMapper._create_message_text(notification),
                    color=notification.severity,
                    emoji=Config.get_slack_emoji(),
                    source=Config.get_service_name(),
                )
                for notification in notifications
            ],
            key=lambda msg: (msg.heading, msg.title),
        )

    def build_heading(self, org_client: AwsOrgClient, region_name: Optional[str], account: Optional[Account]) -> str:
        if region_name is None:
            region_name = ""
        if account is None:
            return ""
        else:
            account = org_client.get_account(account_id=account.identifier)
            return f"{account.name} ({account.identifier}) {region_name} {account.slack_handle}"

    @staticmethod
    def _find_channels(notification: Finding, mappings: Set[NotificationMappingConfig]) -> Set[str]:
        return {
            mapping.channel
            for mapping in mappings
            if (not mapping.items or notification.item in mapping.items)
            and (not mapping.accounts or (notification.account and notification.account.identifier in mapping.accounts))
            and (
                not mapping.compliance_item_types or notification.compliance_item_type in mapping.compliance_item_types
            )
        }

    @staticmethod
    def _create_message_text(notification: Finding) -> str:
        findings = "\n".join(sorted(notification.findings))
        if notification.description:
            return f"{notification.description}\n\n{findings}"
        else:
            return findings
