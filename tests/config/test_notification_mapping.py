from unittest import TestCase

from src.data.exceptions import NotificationMappingException
from src.config.notification_mapping_config import NotificationMappingConfig

from tests.test_types_generator import account


class TestNotificationMapping(TestCase):
    def test_init_with_items(self) -> None:
        filter_config = NotificationMappingConfig.from_dict({"channel": "a-channel", "items": ["a", "b", "c", "b"]})
        self.assertEqual(filter_config.channel, "a-channel")
        self.assertEqual(filter_config.items, {"a", "c", "b"})

    def test_init_with_account(self) -> None:
        filter_config = NotificationMappingConfig.from_dict({"channel": "a-channel", "account": "11223344"})
        self.assertEqual(filter_config.channel, "a-channel")
        self.assertEqual(filter_config.account, account("11223344", ""))

    def test_init_with_unexpected_fields(self) -> None:
        with self.assertRaisesRegex(NotificationMappingException, "huh"):
            NotificationMappingConfig.from_dict({"huh": "huh?"})

    def test_init_with_missing_mandatory_fields(self) -> None:
        with self.assertRaisesRegex(NotificationMappingException, "channel"):
            NotificationMappingConfig.from_dict({"items": ["a", "b", "c"]})

        with self.assertRaisesRegex(NotificationMappingException, "[account|items]"):
            NotificationMappingConfig.from_dict({"channel": "a-channel"})

    def test_init_with_too_many_fields(self) -> None:
        with self.assertRaisesRegex(NotificationMappingException, "[account|items]"):
            NotificationMappingConfig.from_dict({"channel": "a", "account": "1234", "items": ["b"]})
