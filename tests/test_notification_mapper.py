from unittest import TestCase

from src.config.notification_mapping_config import NotificationMappingConfig
from src.notification_mapper import NotificationMapper
from src.slack_notifier import SlackMessage

from tests.test_types_generator import account, notification


notification_a = notification(item="item-a", findings={"a-1", "a-2"}, account=account(identifier="111", name="bbb"))
notification_b = notification(item="item-b", findings={"finding b"}, account=account(identifier="222", name="aaa"))
notification_c = notification(item="item-c", findings={"finding c"}, account=account(identifier="333", name="ccc"))

msg_a = SlackMessage(["central", "channel-2"], "bbb (111)", "item-a", "a-1\na-2", "#ff4d4d")
msg_b = SlackMessage(["central", "channel-1"], "aaa (222)", "item-b", "finding b", "#ff4d4d")
msg_c = SlackMessage(["central", "channel-1", "channel-2"], "ccc (333)", "item-c", "finding c", "#ff4d4d")


class TestNotificationMapper(TestCase):
    def test_notification_mapper_with_items_mapping(self) -> None:
        mapping_1 = NotificationMappingConfig("channel-1", items=["item-b", "item-c"])
        mapping_2 = NotificationMappingConfig("channel-2", items=["item-c", "item-a"])

        notifications = {notification_a, notification_b, notification_c}
        mappings = {mapping_1, mapping_2}
        slack_messages = NotificationMapper().do_map(notifications, mappings, "central")
        self.assertEqual([msg_b, msg_a, msg_c], slack_messages)

    def test_notification_mapper_with_account_mapping(self) -> None:
        mapping_1 = NotificationMappingConfig("channel-1", account="222")
        mapping_2 = NotificationMappingConfig("channel-2", account="111")
        mapping_3 = NotificationMappingConfig("channel-1", account="333")
        mapping_4 = NotificationMappingConfig("channel-2", account="333")

        notifications = {notification_a, notification_b, notification_c}
        mappings = {mapping_1, mapping_2, mapping_3, mapping_4}
        slack_messages = NotificationMapper().do_map(notifications, mappings, "central")
        self.assertEqual([msg_b, msg_a, msg_c], slack_messages)
