from typing import List, Set

from src.data.findings import Findings
from src.config.notification_mapping_config import NotificationMappingConfig
from src.slack_notifier import SlackMessage


class NotificationMapper:
    def do_map(
        self, notifications: Set[Findings], mappings: Set[NotificationMappingConfig], central_channel: str
    ) -> List[SlackMessage]:
        return sorted(
            [
                SlackMessage(
                    channels=sorted(self._find_channels(notification, mappings).union({central_channel})),
                    header=f"{notification.account.name} ({notification.account.identifier})",
                    title=notification.item,
                    text=NotificationMapper._create_message_text(notification),
                    color="#ff4d4d",
                )
                for notification in notifications
            ],
            key=lambda msg: (msg.header, msg.title),
        )

    def _find_channels(self, notification: Findings, mappings: Set[NotificationMappingConfig]) -> Set[str]:
        return self._item_channels(notification, mappings).union(self._account_channels(notification, mappings))

    @staticmethod
    def _item_channels(notification: Findings, mappings: Set[NotificationMappingConfig]) -> Set[str]:
        return {mapping.channel for mapping in mappings if mapping.items and notification.item in mapping.items}

    @staticmethod
    def _account_channels(notification: Findings, mappings: Set[NotificationMappingConfig]) -> Set[str]:
        return {mapping.channel for mapping in mappings if mapping.account and notification.account == mapping.account}

    @staticmethod
    def _create_message_text(notification: Findings) -> str:
        findings = "\n".join(sorted(notification.findings))
        if notification.description:
            return f"{notification.description}\n\n{findings}"
        else:
            return findings
