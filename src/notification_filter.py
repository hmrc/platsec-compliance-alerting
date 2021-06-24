from typing import Set

from src.data.notification import Notification
from src.config.notification_filter_config import NotificationFilterConfig


class NotificationFilter:
    @staticmethod
    def do_filter(notifications: Set[Notification], filters: Set[NotificationFilterConfig]) -> Set[Notification]:
        return {n for n in notifications if n.findings and n.item not in [f.item for f in filters]}
