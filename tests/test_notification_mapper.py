from unittest import TestCase

from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.notification import Notification
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage


notification_a = Notification("item-a", findings={"item a-1", "item a-2"})
notification_b = Notification("item-b", findings={"item b"})
notification_c = Notification("item-c", findings={"item c"})

mapping_1 = NotificationMappingConfig("channel-1", ["item-b", "item-c"])
mapping_2 = NotificationMappingConfig("channel-2", ["item-c", "item-a"])

msg_a = SlackMessage(["central", "channel-2"], "Alert", "item-a", "item a-1\nitem a-2", "#ff4d4d")
msg_b = SlackMessage(["central", "channel-1"], "Alert", "item-b", "item b", "#ff4d4d")
msg_c = SlackMessage(["central", "channel-1", "channel-2"], "Alert", "item-c", "item c", "#ff4d4d")


class TestNotificationMapper(TestCase):
    def test_notification_mapper(self) -> None:
        notifications = {notification_a, notification_b, notification_c}
        mappings = {mapping_1, mapping_2}
        slack_messages = NotificationMapper().do_map(notifications, mappings, "central")
        self.assertEqual([msg_a, msg_b, msg_c], slack_messages)
