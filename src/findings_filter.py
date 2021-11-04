from typing import Set

from src.data.findings import Findings
from src.config.notification_filter_config import NotificationFilterConfig


class FindingsFilter:
    @staticmethod
    def do_filter(findings: Set[Findings], filters: Set[NotificationFilterConfig]) -> Set[Findings]:
        return {n for n in findings if n.findings and n.item not in [f.item for f in filters]}
