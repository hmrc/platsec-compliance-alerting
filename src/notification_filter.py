from typing import List, Set

from src.data.notification import Notification
from src.config.notification_filter_config import NotificationFilterConfig


class NotificationFilter:
    def do_filter(self, notifications: Set[Notification], filters: List[NotificationFilterConfig]) -> Set[Notification]:
        return {n for n in notifications if n.bucket not in [f.bucket for f in filters]}
