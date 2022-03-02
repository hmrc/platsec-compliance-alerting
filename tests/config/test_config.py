import logging
import re
from collections import namedtuple
from typing import Any
from unittest.mock import Mock, patch, call

import pytest

from src.clients.aws_s3_client import AwsS3Client
from src.config.config import Config
from src.config.notification_filter_config import NotificationFilterConfig
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.exceptions import AwsClientException, MissingConfigException, InvalidConfigException
from src.slack_notifier import SlackNotifierConfig


@pytest.mark.parametrize(
    "env_var_key,config_function",
    [
        ("AWS_ACCOUNT", Config().get_aws_account),
        ("CONFIG_BUCKET", Config().get_config_bucket),
        ("CONFIG_BUCKET_READ_ROLE", Config().get_config_bucket_read_role),
        ("REPORT_BUCKET_READ_ROLE", Config().get_report_bucket_read_role),
        ("S3_AUDIT_REPORT_KEY", Config().get_s3_audit_report_key),
        ("IAM_AUDIT_REPORT_KEY", Config().get_iam_audit_report_key),
        ("GITHUB_AUDIT_REPORT_KEY", Config().get_github_audit_report_key),
        ("GITHUB_WEBHOOK_REPORT_KEY", Config().get_github_webhook_report_key),
        ("GITHUB_WEBHOOK_HOST_IGNORE_LIST", Config().get_github_webhook_host_ignore_key),
        ("GUARDDUTY_RUNBOOK_URL", Config().get_guardduty_runbook_url),
        ("VPC_AUDIT_REPORT_KEY", Config().get_vpc_audit_report_key),
        ("PASSWORD_POLICY_AUDIT_REPORT_KEY", Config().get_password_policy_audit_report_key),
        ("SLACK_API_URL", Config().get_slack_api_url),
        ("SLACK_USERNAME_KEY", Config().get_slack_username_key),
        ("SLACK_TOKEN_KEY", Config().get_slack_token_key),
        ("SSM_READ_ROLE", Config().get_ssm_read_role),
    ],
)
def test_missing_env_vars(env_var_key: str, config_function: Any, monkeypatch: Any) -> None:
    monkeypatch.delenv(env_var_key, raising=False)

    with pytest.raises(MissingConfigException) as mce:
        config_function()

    assert re.search(env_var_key, str(mce)) is not None


def test_get_default_log_level(monkeypatch: Any) -> None:
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    assert Config.get_log_level() == "WARNING"


def test_get_configured_log_level(monkeypatch: Any) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")

    assert Config.get_log_level() == "DEBUG"


def test_get_unsupported_log_level(monkeypatch: Any) -> None:
    monkeypatch.setenv("LOG_LEVEL", "banana")

    with pytest.raises(InvalidConfigException) as ice:
        assert Config.get_log_level()

    assert "LOG_LEVEL" in str(ice)
    assert "banana" in str(ice)


@patch("src.clients.aws_client_factory.AwsClientFactory.get_ssm_client")
def test_get_slack_notifier_config(get_ssm_client: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("AWS_ACCOUNT", "22")
    monkeypatch.setenv("SLACK_API_URL", "the-url")
    monkeypatch.setenv("SLACK_USERNAME_KEY", "username-key")
    monkeypatch.setenv("SLACK_TOKEN_KEY", "token-key")
    monkeypatch.setenv("SSM_READ_ROLE", "ssm-role")
    get_ssm_client.return_value.get_parameter.side_effect = lambda x: {
        "username-key": "the-user",
        "token-key": "the-token",
    }[x]

    assert SlackNotifierConfig("the-user", "the-token", "the-url") == Config().get_slack_notifier_config()

    get_ssm_client.assert_called_with("22", "ssm-role")


@patch("src.config.config.Config._fetch_config_files")
def test_get_notification_filters(fetch_config_files: Any) -> None:
    Config().get_notification_filters()

    fetch_config_files.assert_called_once_with("filters/", NotificationFilterConfig.from_dict)


@patch("src.config.config.Config._fetch_config_files")
def test_get_notification_mappings(fetch_config_files: Any) -> None:
    Config().get_notification_mappings()

    fetch_config_files.assert_called_once_with("mappings/", NotificationMappingConfig.from_dict)


@patch("src.clients.aws_client_factory.AwsClientFactory.get_s3_client")
def test_fetch_config_files(get_s3_client: Any, monkeypatch: Any, caplog: Any) -> None:
    aws_account = "99"
    bucket = "buck"
    read_role = "role"
    monkeypatch.setenv("AWS_ACCOUNT", aws_account)
    monkeypatch.setenv("CONFIG_BUCKET", bucket)
    monkeypatch.setenv("CONFIG_BUCKET_READ_ROLE", read_role)
    get_s3_client.return_value.list_objects.return_value = ["1", "2"]
    get_s3_client.return_value.read_object.side_effect = [[{"item": "1"}, {"item": "2"}], AwsClientException("boom")]

    with caplog.at_level(logging.INFO):
        filters = Config()._fetch_config_files("a-prefix", lambda d: namedtuple("Obj", "item")(**d))

    Obj = namedtuple("Obj", "item")
    assert {Obj(item="1"), Obj(item="2")} == filters
    get_s3_client.assert_called_with(aws_account, read_role)
    assert call().list_objects(bucket, "a-prefix") in get_s3_client.mock_calls
    assert call().read_object(bucket, "1") in get_s3_client.mock_calls
    assert call().read_object(bucket, "2") in get_s3_client.mock_calls
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert "unable to load config file '2': boom" in caplog.text


@patch("src.clients.aws_client_factory.AwsClientFactory.get_s3_client")
def test_get_report_s3_client(get_s3_client: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("AWS_ACCOUNT", "88")
    monkeypatch.setenv("REPORT_BUCKET_READ_ROLE", "read-report")
    s3_client = AwsS3Client(Mock())
    get_s3_client.return_value = s3_client

    assert Config().get_report_s3_client() is s3_client

    get_s3_client.assert_called_with("88", "read-report")


@patch("src.clients.aws_client_factory.AwsClientFactory.get_s3_client")
def test_get_slack_mappings(get_s3_client: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("AWS_ACCOUNT", "88")
    monkeypatch.setenv("CONFIG_BUCKET_READ_ROLE", "config-bucket-read-role")
    monkeypatch.setenv("CONFIG_BUCKET", "config-bucket")
    monkeypatch.setenv("SLACK_MAPPINGS_FILENAME", "slack-map-file")
    s3_client = Mock(spec=AwsS3Client, read_raw_object=Mock(return_value='{"team-a": ["account-1", "account-2"]}'))
    get_s3_client.return_value = s3_client

    assert {"team-a": ["account-1", "account-2"]} == Config().get_slack_mappings()

    get_s3_client.assert_called_with("88", "config-bucket-read-role")
    s3_client.read_raw_object.assert_called_once_with("config-bucket", "guardduty_alerts_mappings/slack-map-file")


@patch("src.clients.aws_client_factory.AwsClientFactory.get_s3_client")
def test_get_account_mappings(get_s3_client: Any, monkeypatch: Any) -> None:
    monkeypatch.setenv("ACCOUNT_MAPPINGS_FILENAME", "account-map-file")
    monkeypatch.setenv("AWS_ACCOUNT", "88")
    monkeypatch.setenv("CONFIG_BUCKET_READ_ROLE", "config-bucket-read-role")
    monkeypatch.setenv("CONFIG_BUCKET", "config-bucket")
    s3_client = Mock(spec=AwsS3Client, read_raw_object=Mock(return_value='{"1234": "account-1", "5678": "account-2"}'))
    get_s3_client.return_value = s3_client

    assert {"1234": "account-1", "5678": "account-2"} == Config().get_account_mappings()

    get_s3_client.assert_called_with("88", "config-bucket-read-role")
    s3_client.read_raw_object.assert_called_once_with("config-bucket", "guardduty_alerts_mappings/account-map-file")
