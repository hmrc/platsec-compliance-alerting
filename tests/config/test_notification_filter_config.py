from unittest import TestCase

from src.config.notification_filter_config import NotificationFilterConfig
from src.data.exceptions import FilterConfigException


class TestNotificationFilterConfig(TestCase):
    def test_init_with_all_fields(self) -> None:
        filter_config = NotificationFilterConfig.from_dict({"item": "an-item", "reason": "a-reason"})
        self.assertEqual(filter_config.item, "an-item")
        self.assertEqual(filter_config.reason, "a-reason")

    def test_init_with_unexpected_fields(self) -> None:
        with self.assertRaisesRegex(FilterConfigException, "what"):
            NotificationFilterConfig.from_dict({"what": "wat?"})

    def test_init_with_missing_mandatory_fields(self) -> None:
        with self.assertRaisesRegex(FilterConfigException, "item"):
            NotificationFilterConfig.from_dict({"reason": "a-reason"})

        with self.assertRaisesRegex(FilterConfigException, "reason"):
            NotificationFilterConfig.from_dict({"item": "an-item"})
