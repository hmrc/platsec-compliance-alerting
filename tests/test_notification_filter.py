from unittest import TestCase

from src.config.notification_filter_config import NotificationFilterConfig
from src.notification_filter import NotificationFilter

from tests.test_types_generator import notification

item_1 = notification(item="item_1", findings={"finding 1"})
item_2 = notification(item="item_2", findings={"finding 2"})
item_3 = notification(item="item_3")
item_4 = notification(item="item_4", findings={"finding 3"})

item_2_filter = NotificationFilterConfig("item_2", "a reason")
item_4_filter = NotificationFilterConfig("item_4", "some reason")


class TestNotificationFilter(TestCase):
    def test_filter(self) -> None:
        notifications = {item_1, item_2, item_3, item_4}
        filters = {item_2_filter, item_4_filter}
        self.assertEqual({item_1}, NotificationFilter().do_filter(notifications, filters))

    def test_empty_filters(self) -> None:
        notifications = {item_1, item_2, item_4}
        self.assertEqual(notifications, NotificationFilter().do_filter(notifications=notifications, filters=set()))

    def test_empty_notifications(self) -> None:
        filters = {item_2_filter, item_4_filter}
        self.assertEqual(set(), NotificationFilter().do_filter(notifications=set(), filters=filters))
