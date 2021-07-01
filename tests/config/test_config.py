from unittest import TestCase
from unittest.mock import Mock, patch

from collections import namedtuple
from contextlib import redirect_stderr
from io import StringIO
from os import environ
from typing import Dict, List


from src.clients.aws_client_factory import AwsClientFactory
from src.clients.aws_s3_client import AwsS3Client
from src.clients.aws_ssm_client import AwsSsmClient
from src.config.config import Config
from src.config.notification_filter_config import NotificationFilterConfig
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.exceptions import AwsClientException, MissingConfigException
from src.slack_notifier import SlackNotifierConfig

from tests.config import _raise


class TestConfig(TestCase):
    @patch.dict(environ, {"CENTRAL_CHANNEL": "the-central-channel"}, clear=True)
    def test_get_configured_central_channel(self) -> None:
        self.assertEqual("the-central-channel", Config().get_central_channel())

    def test_get_default_central_channel(self) -> None:
        self.assertEqual("", Config().get_central_channel())

    @patch.dict(environ, {}, clear=True)
    def test_missing_env_vars(self) -> None:
        env_map = {
            "AWS_ACCOUNT": lambda: Config().get_aws_account(),
            "CONFIG_BUCKET": lambda: Config().get_config_bucket(),
            "CONFIG_BUCKET_READ_ROLE": lambda: Config().get_config_bucket_read_role(),
            "REPORT_BUCKET_READ_ROLE": lambda: Config().get_report_bucket_read_role(),
            "S3_AUDIT_REPORT_KEY": lambda: Config().get_s3_audit_report_key(),
            "SLACK_API_URL": lambda: Config().get_slack_api_url(),
            "SLACK_USERNAME_KEY": lambda: Config().get_slack_username_key(),
            "SLACK_TOKEN_KEY": lambda: Config().get_slack_token_key(),
            "SSM_READ_ROLE": lambda: Config().get_ssm_read_role(),
        }
        for key, getter in env_map.items():
            self.assertRaisesRegex(MissingConfigException, key, getter)

    def test_get_default_log_level(self) -> None:
        self.assertEqual("ERROR", Config.get_log_level())

    @patch.dict(environ, {"LOG_LEVEL": "debug"}, clear=True)
    def test_get_configured_log_level(self) -> None:
        self.assertEqual("DEBUG", Config.get_log_level())

    @patch.dict(environ, {"LOG_LEVEL": "banana"}, clear=True)
    def test_get_unsupported_log_level(self) -> None:
        self.assertEqual("ERROR", Config.get_log_level())

    @patch.dict(
        environ,
        {
            "AWS_ACCOUNT": "22",
            "SLACK_API_URL": "the-url",
            "SLACK_USERNAME_KEY": "username-key",
            "SLACK_TOKEN_KEY": "token-key",
            "SSM_READ_ROLE": "ssm-role",
        },
        clear=True,
    )
    def test_get_slack_notifier_config(self) -> None:
        def get_ssm_client(account: str, role: str) -> AwsSsmClient:
            return AwsSsmClient(Mock()) if account == "22" and role == "ssm-role" else None

        def get_parameter(parameter_name: str) -> str:
            return {"username-key": "the-user", "token-key": "the-token"}[parameter_name]

        with patch.object(AwsClientFactory, "get_ssm_client", side_effect=get_ssm_client):
            with patch.object(AwsSsmClient, "get_parameter", side_effect=get_parameter):
                self.assertEqual(
                    SlackNotifierConfig("the-user", "the-token", "the-url"), Config().get_slack_notifier_config()
                )

    def test_get_notification_filters(self) -> None:
        with patch.object(Config, "_fetch_config_files") as mock_fetch:
            Config().get_notification_filters()
        mock_fetch.assert_called_once_with("filters/", NotificationFilterConfig.from_dict)

    def test_get_notification_mappings(self) -> None:
        with patch.object(Config, "_fetch_config_files") as mock_fetch:
            Config().get_notification_mappings()
        mock_fetch.assert_called_once_with("mappings/", NotificationMappingConfig.from_dict)

    @patch.dict(environ, {"AWS_ACCOUNT": "99", "CONFIG_BUCKET": "buck", "CONFIG_BUCKET_READ_ROLE": "role"}, clear=True)
    def test_fetch_config_files(self) -> None:
        def get_s3_client(account: str, role: str) -> AwsS3Client:
            return AwsS3Client(Mock()) if account == "99" and role == "role" else None

        def list_objects(bucket: str, prefix: str) -> List[str]:
            return ["1", "2"] if bucket == "buck" and prefix == "a-prefix" else None

        def read_object(bucket: str, key: str) -> Dict[str, str]:
            return (
                {"1": lambda: [{"item": "1"}, {"item": "2"}], "2": lambda: _raise(AwsClientException("boom"))}[key]()
                if bucket == "buck"
                else None
            )

        with patch.object(AwsClientFactory, "get_s3_client", side_effect=get_s3_client):
            with patch.object(AwsS3Client, "list_objects", side_effect=list_objects):
                with patch.object(AwsS3Client, "read_object", side_effect=read_object):
                    with redirect_stderr(StringIO()) as err:
                        filters = Config()._fetch_config_files("a-prefix", lambda d: namedtuple("Obj", "item")(**d))
        self.assertEqual({namedtuple("Obj", "item")(item="1"), namedtuple("Obj", "item")(item="2")}, filters)
        self.assertEqual("unable to load config file '2': boom", err.getvalue().strip())

    @patch.dict(environ, {"AWS_ACCOUNT": "88", "REPORT_BUCKET_READ_ROLE": "read-report"}, clear=True)
    def test_get_report_s3_client(self) -> None:
        s3_client = AwsS3Client(Mock())

        def get_s3_client(account: str, role: str) -> AwsS3Client:
            return s3_client if account == "88" and role == "read-report" else None

        with patch.object(AwsClientFactory, "get_s3_client", side_effect=get_s3_client):
            self.assertEqual(s3_client, Config().get_report_s3_client())
