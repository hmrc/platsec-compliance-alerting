from typing import Set

from src.data.notification import Notification
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.slack_notification import SlackNotification


class NotificationMapper:
    def do_map(
        self, notifications: Set[Notification], mappings: Set[NotificationMappingConfig], central_channel: str
    ) -> Set[SlackNotification]:
        return {
            SlackNotification(n, self._find_channels(n.bucket, mappings).union({central_channel}))
            for n in notifications
        }

    @staticmethod
    def _find_channels(bucket: str, mappings: Set[NotificationMappingConfig]) -> Set[str]:
        return {mapping.channel for mapping in mappings if bucket in mapping.buckets}
