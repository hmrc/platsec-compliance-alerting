from typing import List, Set, Optional

from src.clients.aws_org_client import AwsOrgClient
from src.data.account import Account
from src.data.findings import Findings
from src.config.notification_mapping_config import NotificationMappingConfig
from src.slack_notifier import SlackMessage


class NotificationMapper:
    def do_map(
        self, notifications: Set[Findings], mappings: Set[NotificationMappingConfig], org_client: AwsOrgClient
    ) -> List[SlackMessage]:
        return sorted(
            [
                SlackMessage(
                    channels=sorted(NotificationMapper._find_channels(notification, mappings)),
                    header=self.build_header(org_client, notification.account),
                    title=notification.item,
                    text=NotificationMapper._create_message_text(notification),
                    color="#ff4d4d",
                )
                for notification in notifications
            ],
            key=lambda msg: (msg.header, msg.title),
        )

    def build_header(self, org_client: AwsOrgClient, account: Optional[Account]) -> str:
        if account is None:
            return ""
        else:
            account = org_client.get_account(account_id=account.identifier)
            return f"{account.name} ({account.identifier}) {account.slack_handle}"

    @staticmethod
    def _find_channels(notification: Findings, mappings: Set[NotificationMappingConfig]) -> Set[str]:
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
    def _create_message_text(notification: Findings) -> str:
        findings = "\n".join(sorted(notification.findings))
        if notification.description:
            return f"{notification.description}\n\n{findings}"
        else:
            return findings
