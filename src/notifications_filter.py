from typing import Dict, List, Set

from src.notification import Notification


class NotificationsFilter:
    def do_filter(self, notifications: Set[Notification], filters: List[Dict[str, str]]) -> Set[Notification]:
        return {n for n in notifications if n.bucket not in [f["bucket"] for f in filters]}