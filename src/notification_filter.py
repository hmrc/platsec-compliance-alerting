from typing import List, Set

from src.notification import Notification
from src.notification_filter_config import NotificationFilterConfig


class NotificationFilter:
    def do_filter(self, notifications: Set[Notification], filters: List[NotificationFilterConfig]) -> Set[Notification]:
        return {n for n in notifications if n.bucket not in [f.bucket for f in filters]}
