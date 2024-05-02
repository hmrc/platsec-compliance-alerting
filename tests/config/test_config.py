import logging
import re
from collections import namedtuple
from typing import Any, Dict
from unittest.mock import Mock, patch, call

import pytest

from src.clients.aws_org_client import AwsOrgClient
from src.clients.aws_s3_client import AwsS3Client
from src.config.config import Config
from src.config.notification_filter_config import NotificationFilterConfig
from src.config.notification_mapping_config import NotificationMappingConfig
from src.config.slack_notifier_config import SlackNotifierConfig
from src.data.exceptions import AwsClientException, MissingConfigException, InvalidConfigException


MOCK_CLIENTS: Dict[str, Any] = {
    "config_s3_client": Mock(),
    "report_s3_client": Mock(),
    "ssm_client": Mock(),
    "org_client": Mock(),
}


@pytest.mark.parametrize(
    "env_var_key,config_function",
    [
        ("AWS_ACCOUNT", Config(**MOCK_CLIENTS).get_aws_account),
        ("CONFIG_BUCKET", Config(**MOCK_CLIENTS).get_config_bucket),
        ("CONFIG_BUCKET_READ_ROLE", Config(**MOCK_CLIENTS).get_config_bucket_read_role),
        ("REPORT_BUCKET_READ_ROLE", Config(**MOCK_CLIENTS).get_report_bucket_read_role),
        ("S3_AUDIT_REPORT_KEY", Config(**MOCK_CLIENTS).get_s3_audit_report_key),
        ("IAM_AUDIT_REPORT_KEY", Config(**MOCK_CLIENTS).get_iam_audit_report_key),
        ("GITHUB_AUDIT_REPORT_KEY", Config(**MOCK_CLIENTS).get_github_audit_report_key),
        ("GITHUB_WEBHOOK_REPORT_KEY", Config(**MOCK_CLIENTS).get_github_webhook_report_key),
        ("GITHUB_WEBHOOK_HOST_IGNORE_LIST", Config(**MOCK_CLIENTS).get_github_webhook_host_ignore_key),
        ("GUARDDUTY_RUNBOOK_URL", Config(**MOCK_CLIENTS).get_guardduty_runbook_url),
        ("VPC_AUDIT_REPORT_KEY", Config(**MOCK_CLIENTS).get_vpc_audit_report_key),
        ("VPC_PEERING_AUDIT_REPORT_KEY", Config(**MOCK_CLIENTS).get_vpc_peering_audit_report_key),
        ("IGNORABLE_REPORT_KEYS", Config(**MOCK_CLIENTS).get_ignorable_report_keys),
        ("PUBLIC_QUERY_AUDIT_REPORT_KEY", Config(**MOCK_CLIENTS).get_public_query_audit_report_key),
        ("PASSWORD_POLICY_AUDIT_REPORT_KEY", Config(**MOCK_CLIENTS).get_password_policy_audit_report_key),
        ("SLACK_API_URL", Config(**MOCK_CLIENTS).get_slack_api_url),
        ("SLACK_V2_API_KEY", Config(**MOCK_CLIENTS).get_slack_v2_api_key),
        ("SLACK_EMOJI", Config(**MOCK_CLIENTS).get_slack_emoji),
        ("SSM_READ_ROLE", Config(**MOCK_CLIENTS).get_ssm_read_role),
        ("ORG_ACCOUNT", Config(**MOCK_CLIENTS).get_org_account),
        ("ORG_READ_ROLE", Config(**MOCK_CLIENTS).get_org_read_role),
        ("PAGERDUTY_API_URL", Config(**MOCK_CLIENTS).get_pagerduty_api_url),
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


def feature_switch_defaults_false(monkeypatch: Any) -> None:
    monkeypatch.delenv("ENABLE_WIKI_CHECKING", raising=False)

    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is False


def feature_switch_can_be_disabled(monkeypatch: Any) -> None:
    monkeypatch.setenv("ENABLE_WIKI_CHECKING", "false")
    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is False

    monkeypatch.setenv("ENABLE_WIKI_CHECKING", "False")
    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is False

    monkeypatch.setenv("ENABLE_WIKI_CHECKING", " False ")
    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is False

    monkeypatch.setenv("ENABLE_WIKI_CHECKING", "FALSE")
    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is False


def feature_switch_can_be_enabled(monkeypatch: Any) -> None:
    monkeypatch.setenv("ENABLE_WIKI_CHECKING", "true")
    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is True

    monkeypatch.setenv("ENABLE_WIKI_CHECKING", "True")
    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is True

    monkeypatch.setenv("ENABLE_WIKI_CHECKING", " TRUE")
    assert Config(**MOCK_CLIENTS).get_enable_wiki_checking() is True


def test_get_configured_log_level(monkeypatch: Any) -> None:
    monkeypatch.setenv("LOG_LEVEL", "debug")

    assert Config.get_log_level() == "DEBUG"


def test_get_unsupported_log_level(monkeypatch: Any) -> None:
    monkeypatch.setenv("LOG_LEVEL", "banana")

    with pytest.raises(InvalidConfigException) as ice:
        assert Config.get_log_level()

    assert "LOG_LEVEL" in str(ice)
    assert "banana" in str(ice)


def test_get_ignorable_report_keys(monkeypatch: Any) -> None:
    monkeypatch.setenv("IGNORABLE_REPORT_KEYS", "key_1.json,key_2.json")

    assert Config(**MOCK_CLIENTS).get_ignorable_report_keys() == ["key_1.json", "key_2.json"]


def test_get_slack_notifier_config(monkeypatch: Any) -> None:
    monkeypatch.setenv("SLACK_API_URL", "the-url")
    monkeypatch.setenv("SLACK_V2_API_KEY", "some-test-api-v2-key")
    monkeypatch.setenv("SLACK_EMOJI", ":test-emoji:")
    ssm_client = Mock().return_value
    ssm_client.get_parameter.side_effect = lambda x: {
        "some-test-api-v2-key": "some-test-api-v2-key",
    }[x]
    MOCK_CLIENTS["ssm_client"] = ssm_client

    assert (
        SlackNotifierConfig("some-test-api-v2-key", "the-url", ":test-emoji:")
        == Config(**MOCK_CLIENTS).get_slack_notifier_config()
    )


@patch("src.config.config.Config._fetch_config_files")
def test_get_notification_filters(fetch_config_files: Any) -> None:
    Config(**MOCK_CLIENTS).get_notification_filters()

    fetch_config_files.assert_called_once_with("filters/", NotificationFilterConfig.from_dict)


@patch("src.config.config.Config._fetch_config_files")
def test_get_notification_mappings(fetch_config_files: Any) -> None:
    Config(**MOCK_CLIENTS).get_notification_mappings()

    fetch_config_files.assert_called_once_with("mappings/", NotificationMappingConfig.from_dict)


def test_fetch_config_files(monkeypatch: Any, caplog: Any) -> None:
    bucket = "buck"
    monkeypatch.setenv("CONFIG_BUCKET", bucket)
    s3_client = Mock().return_value
    s3_client.list_objects.return_value = ["1", "2"]
    s3_client.read_object.side_effect = [[{"item": "1"}, {"item": "2"}], AwsClientException("boom")]
    MOCK_CLIENTS["config_s3_client"] = s3_client

    with caplog.at_level(logging.INFO):
        filters = Config(**MOCK_CLIENTS)._fetch_config_files("a-prefix", lambda d: namedtuple("Obj", "item")(**d))

    Obj = namedtuple("Obj", "item")
    assert {Obj(item="1"), Obj(item="2")} == filters
    print(s3_client.mock_calls)
    assert call.list_objects(bucket, "a-prefix") in s3_client.mock_calls
    assert call.read_object(bucket, "1") in s3_client.mock_calls
    assert call.read_object(bucket, "2") in s3_client.mock_calls
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert "unable to load config file '2': boom" in caplog.text


def test_get_report_s3_client() -> None:
    s3_client = AwsS3Client(Mock())
    MOCK_CLIENTS["report_s3_client"] = s3_client

    assert Config(**MOCK_CLIENTS).get_report_s3_client() is s3_client


def test_get_org_client() -> None:
    org_client = AwsOrgClient(Mock())
    MOCK_CLIENTS["org_client"] = org_client

    assert Config(**MOCK_CLIENTS).get_org_client() is org_client
