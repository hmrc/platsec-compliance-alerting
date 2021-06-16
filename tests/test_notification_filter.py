from unittest import TestCase

from src.data.notification import Notification
from src.config.notification_filter_config import NotificationFilterConfig
from src.notification_filter import NotificationFilter

private_bucket = Notification(bucket="private-bucket")
public_bucket = Notification(bucket="public-bucket")
another_bucket = Notification(bucket="another-bucket")
unencrypted_bucket = Notification(bucket="unencrypted-bucket")

public_bucket_filter = NotificationFilterConfig("public-bucket")
unencrypted_bucket_filter = NotificationFilterConfig("unencrypted-bucket")


class TestNotificationFilter(TestCase):
    def test_filter(self) -> None:
        notifications = {private_bucket, public_bucket, another_bucket, unencrypted_bucket}
        filters = [public_bucket_filter, unencrypted_bucket_filter]
        self.assertEqual({private_bucket, another_bucket}, NotificationFilter().do_filter(notifications, filters))

    def test_empty_filters(self) -> None:
        notifications = {private_bucket, public_bucket, another_bucket, unencrypted_bucket}
        self.assertEqual(notifications, NotificationFilter().do_filter(notifications=notifications, filters=[]))

    def test_empty_notifications(self) -> None:
        filters = [public_bucket_filter, unencrypted_bucket_filter]
        self.assertEqual(set(), NotificationFilter().do_filter(notifications=set(), filters=filters))
