from unittest import TestCase

from src.config.notification_filter_config import NotificationFilterConfig
from src.findings_filter import FindingsFilter

from tests.test_types_generator import finding

item_1 = finding(item="item_1", findings={"finding 1"})
item_2 = finding(item="item_2", findings={"finding 2"})
item_3 = finding(item="item_3")
item_4 = finding(item="item_4", findings={"finding 3"})

item_2_filter = NotificationFilterConfig("item_2", "a reason")
item_4_filter = NotificationFilterConfig("item_4", "some reason")


class TestFindingsFilter(TestCase):
    def test_filter(self) -> None:
        notifications = {item_1, item_2, item_3, item_4}
        filters = {item_2_filter, item_4_filter}
        self.assertEqual({item_1}, FindingsFilter().do_filter(notifications, filters))

    def test_empty_filters(self) -> None:
        notifications = {item_1, item_2, item_4}
        self.assertEqual(notifications, FindingsFilter().do_filter(findings=notifications, filters=set()))

    def test_empty_notifications(self) -> None:
        filters = {item_2_filter, item_4_filter}
        self.assertEqual(set(), FindingsFilter().do_filter(findings=set(), filters=filters))
