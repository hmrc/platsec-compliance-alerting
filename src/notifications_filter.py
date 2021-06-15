from typing import Dict, List, Set

from src.notification import Notification


class NotificationsFilter:
    def do_filter(self, notifications: Set[Notification], filters: List[Dict[str, str]]) -> Set[Notification]:
        filtered = set()
        undesired_buckets = [f["bucket"] for f in filters]
        for notification in notifications:
            if notification.bucket not in undesired_buckets:
                filtered.add(notification)
        return filtered
