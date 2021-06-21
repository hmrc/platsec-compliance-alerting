from unittest import TestCase

from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.notification import Notification
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage


notification_a = Notification("bucket-a", findings={"item a-1", "item a-2"})
notification_b = Notification("bucket-b", findings={"item b"})
notification_c = Notification("bucket-c", findings={"item c"})

mapping_1 = NotificationMappingConfig("channel-1", ["bucket-b", "bucket-c"])
mapping_2 = NotificationMappingConfig("channel-2", ["bucket-c", "bucket-a"])

msg_a = SlackMessage(["central", "channel-2"], "Alert", "bucket-a", "item a-1\nitem a-2")
msg_b = SlackMessage(["central", "channel-1"], "Alert", "bucket-b", "item b")
msg_c = SlackMessage(["central", "channel-1", "channel-2"], "Alert", "bucket-c", "item c")


class TestNotificationMapper(TestCase):
    def test_notification_mapper(self) -> None:
        notifications = {notification_a, notification_b, notification_c}
        mappings = {mapping_1, mapping_2}
        slack_messages = NotificationMapper().do_map(notifications, mappings, "central")
        self.assertEqual([msg_a, msg_b, msg_c], slack_messages)
