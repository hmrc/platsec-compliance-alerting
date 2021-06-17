from unittest import TestCase
from unittest.mock import Mock, patch

from os import environ
from typing import Dict, List

from src.clients.aws_client_factory import AwsClientFactory
from src.clients.aws_s3_client import AwsS3Client
from src.config.config import Config
from src.config.notification_filter_config import NotificationFilterConfig
from src.data.exceptions import MissingConfigException


class TestConfig(TestCase):
    @patch.dict(environ, {"CENTRAL_CHANNEL": "the-central-channel"}, clear=True)
    def test_get_central_channel(self) -> None:
        self.assertEqual("the-central-channel", Config().get_central_channel())

    @patch.dict(environ, {}, clear=True)
    def test_missing_env_vars(self) -> None:
        env_map = {
            "AWS_ACCOUNT": lambda: Config().get_aws_account(),
            "CENTRAL_CHANNEL": lambda: Config().get_central_channel(),
            "CONFIG_BUCKET": lambda: Config().get_config_bucket(),
            "CONFIG_BUCKET_READ_ROLE": lambda: Config().get_config_bucket_read_role(),
        }
        for key, getter in env_map.items():
            self.assertRaisesRegex(MissingConfigException, key, getter)

    @patch.dict(
        environ,
        {
            "AWS_ACCOUNT": "111222333444",
            "CONFIG_BUCKET": "config-bucket",
            "CONFIG_BUCKET_READ_ROLE": "config-bucket-read-role",
        },
        clear=True,
    )
    def test_get_notification_filters(self) -> None:
        def get_s3_client(account: str, role: str) -> AwsS3Client:
            return AwsS3Client(Mock()) if account == "111222333444" and role == "config-bucket-read-role" else None

        def list_objects(bucket: str, prefix: str) -> List[str]:
            return ["1", "2"] if bucket == "config-bucket" and prefix == "filters/" else None

        def read_object(bucket: str, key: str) -> Dict[str, str]:
            return (
                {
                    "1": {"bucket": "bucket-1", "team": "team-1", "reason": "reason-1"},
                    "2": {"bucket": "bucket-2", "team": "team-2", "reason": "reason-2"},
                }[key]
                if bucket == "config-bucket"
                else None
            )

        with patch.object(AwsClientFactory, "get_s3_client", side_effect=get_s3_client):
            with patch.object(AwsS3Client, "list_objects", side_effect=list_objects):
                with patch.object(AwsS3Client, "read_object", side_effect=read_object):
                    filters = Config().get_notification_filters()
                    self.assertEqual(
                        [
                            NotificationFilterConfig("bucket-1", "team-1", "reason-1"),
                            NotificationFilterConfig("bucket-2", "team-2", "reason-2"),
                        ],
                        filters,
                    )
