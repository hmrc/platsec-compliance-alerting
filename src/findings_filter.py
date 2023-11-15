from typing import Set
from src.data.finding import Finding

from src.config.notification_filter_config import NotificationFilterConfig


class FindingsFilter:
    @staticmethod
    def do_filter(findings: Set[Finding], filters: Set[NotificationFilterConfig]) -> Set[Finding]:
        return {n for n in findings if n.findings and n.item not in [f.item for f in filters]}
