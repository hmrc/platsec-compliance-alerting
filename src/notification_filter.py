from typing import List, Set

from src.data.notification import Notification
from src.config.notification_filter_config import NotificationFilterConfig


class NotificationFilter:
    @staticmethod
    def do_filter(notifications: Set[Notification], filters: List[NotificationFilterConfig]) -> Set[Notification]:
        return {n for n in notifications if n.findings and n.bucket not in [f.bucket for f in filters]}
