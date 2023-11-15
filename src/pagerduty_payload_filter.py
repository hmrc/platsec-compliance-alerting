from typing import Set
from src.data.finding import Finding

from src.config.notification_filter_config import NotificationFilterConfig
from src.data.pagerduty_payload import PagerDutyPayload


class PagerDutyPayloadFilter:
    @staticmethod
    def do_filter(payloads: Set[PagerDutyPayload], filters: Set[NotificationFilterConfig]) -> Set[PagerDutyPayload]:
        return {n for n in payloads if n.component not in [f.item for f in filters]}
