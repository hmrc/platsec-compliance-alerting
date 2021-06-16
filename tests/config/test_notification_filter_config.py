from unittest import TestCase

from src.config.notification_filter_config import NotificationFilterConfig
from src.data.exceptions import FilterConfigException


class TestNotificationFilterConfig(TestCase):
    def test_init_with_all_fields(self) -> None:
        filter_config = NotificationFilterConfig.from_dict(
            {"bucket": "a-bucket", "team": "a-team", "reason": "a-reason"}
        )
        self.assertEqual(filter_config.bucket, "a-bucket")
        self.assertEqual(filter_config.team, "a-team")
        self.assertEqual(filter_config.reason, "a-reason")

    def test_init_with_missing_optional_fields(self) -> None:
        filter_config = NotificationFilterConfig.from_dict({"bucket": "some-bucket"})
        self.assertEqual(filter_config.bucket, "some-bucket")
        self.assertEqual(filter_config.team, "unset")
        self.assertEqual(filter_config.reason, "unset")

    def test_init_with_missing_mandatory_fields(self) -> None:
        with self.assertRaisesRegex(FilterConfigException, "bucket"):
            NotificationFilterConfig.from_dict({})
