from unittest import TestCase

from src.config.notification_mapping_config import NotificationMappingConfig
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage

from tests.test_types_generator import account, notification


notification_a = notification(item="item-a", findings={"finding a-1", "finding a-2"})
notification_b = notification(item="item-b", findings={"finding b"}, account=account(name="aaa"))
notification_c = notification(item="item-c", findings={"finding c"})

mapping_1 = NotificationMappingConfig("channel-1", ["item-b", "item-c"])
mapping_2 = NotificationMappingConfig("channel-2", ["item-c", "item-a"])

msg_a = SlackMessage(["central", "channel-2"], "test-account (1234)", "item-a", "finding a-1\nfinding a-2", "#ff4d4d")
msg_b = SlackMessage(["central", "channel-1"], "aaa (1234)", "item-b", "finding b", "#ff4d4d")
msg_c = SlackMessage(["central", "channel-1", "channel-2"], "test-account (1234)", "item-c", "finding c", "#ff4d4d")


class TestNotificationMapper(TestCase):
    def test_notification_mapper(self) -> None:
        notifications = {notification_a, notification_b, notification_c}
        mappings = {mapping_1, mapping_2}
        slack_messages = NotificationMapper().do_map(notifications, mappings, "central")
        self.assertEqual([msg_b, msg_a, msg_c], slack_messages)
