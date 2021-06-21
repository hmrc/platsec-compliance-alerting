from unittest import TestCase

from src.data.exceptions import NotificationMappingException
from src.config.notification_mapping_config import NotificationMappingConfig


class TestNotificationMapping(TestCase):
    def test_init_with_all_fields(self) -> None:
        filter_config = NotificationMappingConfig.from_dict({"channel": "a-channel", "buckets": ["a", "b", "c", "b"]})
        self.assertEqual(filter_config.channel, "a-channel")
        self.assertEqual(filter_config.buckets, {"a", "c", "b"})

    def test_init_with_unexpected_fields(self) -> None:
        with self.assertRaisesRegex(NotificationMappingException, "huh"):
            NotificationMappingConfig.from_dict({"huh": "huh?"})

    def test_init_with_missing_mandatory_fields(self) -> None:
        with self.assertRaisesRegex(NotificationMappingException, "channel"):
            NotificationMappingConfig.from_dict({"buckets": ["a", "b", "c"]})

        with self.assertRaisesRegex(NotificationMappingException, "buckets"):
            NotificationMappingConfig.from_dict({"channel": "a-channel"})