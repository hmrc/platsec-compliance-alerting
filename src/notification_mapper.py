from typing import List, Set, Optional
import json

from src.clients.aws_org_client import AwsOrgClient
from src.data.account import Account
from src.data.finding import Finding
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.slack_message import SlackMessage


class NotificationMapper:
    def do_map(
        self, notifications: Set[Finding], mappings: Set[NotificationMappingConfig], org_client: AwsOrgClient
    ) -> List[SlackMessage]:
        return sorted(
            [
                SlackMessage(
                    channels=sorted(NotificationMapper._find_channels(notification, mappings)),
                    header=self.build_header(org_client, notification.region_name, notification.account),
                    title=notification.item,
                    text=NotificationMapper._create_message_text(notification),
                    color=notification.severity,
                )
                for notification in notifications
            ],
            key=lambda msg: (msg.header, msg.title),
        )

    @staticmethod
    def _convert_text_to_slack_block_kit(account_name: str, account_id: str, region: str, team_handle: str) -> str:
        output_block_kit = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"{account_name} ({account_id}), {region} @{team_handle}"},
        }

        return json.dumps(output_block_kit)

    def build_header(self, org_client: AwsOrgClient, region_name: Optional[str], account: Optional[Account]) -> str:
        if region_name is None:
            region_name = ""
        if account is None:
            return ""
        else:
            account = org_client.get_account(account_id=account.identifier)
            slack_header = NotificationMapper._convert_text_to_slack_block_kit(
                account.name, account.identifier, region_name, account.slack_handle.lstrip("@")
            )
            return slack_header
            # return f"{account.name} ({account.identifier}) {region_name} {account.slack_handle.lstrip('@')}"

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
