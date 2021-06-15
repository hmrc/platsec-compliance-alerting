from unittest import TestCase

from src.exceptions import NotificationMappingException
from src.notification_mapping import NotificationMapping


class TestNotificationMapping(TestCase):
    def test_init_with_all_fields(self) -> None:
        filter_config = NotificationMapping.from_dict({"channel": "a-channel", "buckets": ["a", "b", "c", "b"]})
        self.assertEqual(filter_config.channel, "a-channel")
        self.assertEqual(filter_config.buckets, {"a", "c", "b"})

    def test_init_with_missing_mandatory_fields(self) -> None:
        with self.assertRaisesRegex(NotificationMappingException, "channel"):
            NotificationMapping.from_dict({"buckets": ["a", "b", "c"]})

        with self.assertRaisesRegex(NotificationMappingException, "buckets"):
            NotificationMapping.from_dict({"channel": "a-channel"})
