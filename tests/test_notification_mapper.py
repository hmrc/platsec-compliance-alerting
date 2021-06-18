from unittest import TestCase

from src.data.notification import Notification
from src.notification_mapper import NotificationMapper
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.slack_notification import SlackNotification


notification_a = Notification("bucket-a")
notification_b = Notification("bucket-b")
notification_c = Notification("bucket-c")

mapping_1 = NotificationMappingConfig("channel-1", ["bucket-b", "bucket-c"])
mapping_2 = NotificationMappingConfig("channel-2", ["bucket-c", "bucket-a"])

slack_a = SlackNotification(notification_a, {"central", "channel-2"})
slack_b = SlackNotification(notification_b, {"central", "channel-1"})
slack_c = SlackNotification(notification_c, {"central", "channel-1", "channel-2"})


class TestNotificationMapper(TestCase):
    def test_notification_mapper(self) -> None:
        notifications = {notification_a, notification_b, notification_c}
        mappings = {mapping_1, mapping_2}
        slack_notifications = NotificationMapper().do_map(notifications, mappings, "central")
        self.assertEqual({slack_a, slack_b, slack_c}, slack_notifications)
