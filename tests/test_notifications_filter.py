from unittest import TestCase

from src.notification import Notification
from src.notifications_filter import NotificationsFilter


class TestNotificationsFilter(TestCase):
    def test_filter(self) -> None:
        filters = [{"bucket": "public-bucket"}, {"bucket": "unencrypted-bucket"}]
        notifications = {
            Notification(bucket="private-bucket", findings=set()),
            Notification(bucket="public-bucket", findings=set()),
            Notification(bucket="another-bucket", findings=set()),
            Notification(bucket="unencrypted-bucket", findings=set()),
        }
        filtered = NotificationsFilter().do_filter(notifications=notifications, filters=filters)
        self.assertEqual({
            Notification(bucket="private-bucket", findings=set()),
            Notification(bucket="another-bucket", findings=set())
        }, filtered)

    def test_empty_filters(self) -> None:
        notifications = {
            Notification(bucket="private-bucket", findings=set()),
            Notification(bucket="public-bucket", findings=set()),
            Notification(bucket="another-bucket", findings=set()),
            Notification(bucket="unencrypted-bucket", findings=set()),
        }
        filtered = NotificationsFilter().do_filter(notifications=notifications, filters=[])
        self.assertEqual(notifications, filtered)

    def test_empty_notifications(self) -> None:
        filters = [{"bucket": "public-bucket"}, {"bucket": "unencrypted-bucket"}]
        filtered = NotificationsFilter().do_filter(notifications=set(), filters=filters)
        self.assertEqual(set(), filtered)