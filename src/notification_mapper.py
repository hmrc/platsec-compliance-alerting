from typing import List, Set

from src.data.notification import Notification
from src.config.notification_mapping_config import NotificationMappingConfig
from src.slack_notifier import SlackMessage


class NotificationMapper:
    def do_map(
        self, notifications: Set[Notification], mappings: Set[NotificationMappingConfig], central_channel: str
    ) -> List[SlackMessage]:
        return sorted(
            [
                SlackMessage(
                    channels=sorted(self._find_channels(notification.item, mappings).union({central_channel})),
                    header=f"{notification.account.name} ({notification.account.identifier})",
                    title=notification.item,
                    text="\n".join(sorted(notification.findings)),
                    color="#ff4d4d",
                )
                for notification in notifications
            ],
            key=lambda msg: (msg.header, msg.title),
        )

    @staticmethod
    def _find_channels(item: str, mappings: Set[NotificationMappingConfig]) -> Set[str]:
        return {mapping.channel for mapping in mappings if item in mapping.items}
