from typing import Set

from src.notification import Notification
from src.notification_mapping import NotificationMapping
from src.slack_notification import SlackNotification


class NotificationMapper:
    def do_map(self, notifications: Set[Notification], mappings: Set[NotificationMapping]) -> Set[SlackNotification]:
        return {SlackNotification(n, self._find_channels(n.bucket, mappings)) for n in notifications}

    @staticmethod
    def _find_channels(bucket: str, mappings: Set[NotificationMapping]) -> Set[str]:
        return {mapping.channel for mapping in mappings if bucket in mapping.buckets}.union({"central"})
