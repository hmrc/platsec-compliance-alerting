from dataclasses import dataclass
from unittest.mock import Mock, patch

import os
from copy import deepcopy
from typing import Any, Dict, Iterator, List

import boto3
import httpretty
import pytest

import json

from botocore.client import BaseClient
from moto import mock_s3, mock_ssm, mock_organizations

from src import compliance_alerter
from src.clients.aws_org_client import AwsOrgClient
from src.clients.aws_s3_client import AwsS3Client
from src.clients.aws_ssm_client import AwsSsmClient
from src.config.config import Config
from src.data.exceptions import UnsupportedEventException
from src.data.severity import Severity
from src.slack_notifier import SlackMessage

from tests.fixtures.github_compliance import github_report
from tests.fixtures.github_webhook_compliance import github_webhook_report
from tests.fixtures.s3_compliance_alerter import s3_report
from tests.fixtures.vpc_compliance import vpc_report
from tests.fixtures.vpc_peering_compliance import vpc_peering_audit
from tests.fixtures.password_policy_compliance import password_policy_report

CHANNEL = "the-alerting-channel"
CONFIG_BUCKET = "the_config_bucket"
REPORT_BUCKET = "the_report_bucket"
S3_KEY = "s3_audit"
IAM_KEY = "iam_audit"
GITHUB_KEY = "github_audit"
GITHUB_WEBHOOK_KEY = "github_webhook"
GITHUB_WEBHOOK_HOST_IGNORE_LIST = "known-host.com,known-host2.com"
VPC_KEY = "vpc_audit"
VPC_PEERING_KEY = "vpc_peering_audit"
PUBLIC_QUERY_KEY = "public_query_audit"
EC2_KEY = "ec2_audit"
PASSWORD_POLICY_KEY = "password_policy_audit"
SLACK_API_URL = "https://the-slack-api-url.com"
SLACK_USERNAME_KEY = "the-slack-username-key"
SLACK_TOKEN_KEY = "the-slack-token-key"


@patch("src.compliance_alerter.AwsClientFactory.get_s3_client")
@patch("src.compliance_alerter.AwsClientFactory.get_ssm_client")
@patch("src.compliance_alerter.AwsClientFactory.get_org_client")
@patch("src.compliance_alerter.ComplianceAlerter")
def test_main(
    mock_compliance_alerter: Mock, mock_s3_client: Mock, mock_ssm_client: Mock, mock_org_client: Mock
) -> None:
    message = SlackMessage(
        channels=[CHANNEL],
        header="test-account 111222333444 eu-west-2 @some-team-name",
        title="aTitle",
        text="Words of Advice",
        color=Severity.HIGH,
    )
    mock_compliance_alerter.return_value.send.return_value = Mock()
    _mock = mock_compliance_alerter.return_value
    _mock.generate_slack_messages.return_value = message
    _mock.send.return_value = Mock()
    compliance_alerter.main(build_event(S3_KEY))

    _mock.send.assert_called_once_with(message)


def test_send(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    ca.send(
        slack_messages=[
            SlackMessage(
                channels=[CHANNEL],
                header="test-account 111222333444 eu-west-2 @some-team-name",
                title="aTitle",
                text="Words of Advice",
                color=Severity.HIGH,
            )
        ]
    )
    _assert_slack_message_sent("@some-team-name")


def test_compliance_alerter_main_s3_audit(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(build_event(S3_KEY))
    ca.send(messages)
    _assert_slack_message_sent_to_channel("the-alerting-channel")
    _assert_slack_message_sent("bad-bucket")
    _assert_slack_message_sent("@some-team-name")


def test_compliance_alerter_main_github_audit(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(build_event(GITHUB_KEY))
    ca.send(messages)
    _assert_slack_message_sent_to_channel("the-alerting-channel")
    _assert_slack_message_sent("bad-repo-no-signing")


def test_compliance_alerter_main_github_webhook(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(build_event(GITHUB_WEBHOOK_KEY))
    ca.send(messages)
    _assert_slack_message_sent_to_channel("the-alerting-channel")
    _assert_slack_message_sent("https://unknown-host.com")


def test_compliance_alerter_main_vpc_audit(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(build_event(VPC_KEY))
    ca.send(messages)
    _assert_slack_message_sent_to_channel("the-alerting-channel")
    _assert_slack_message_sent("VPC flow logs compliance enforcement success")
    _assert_slack_message_sent("@some-team-name")


def test_compliance_alerter_main_vpc_peering_audit(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(build_event(VPC_PEERING_KEY))
    ca.send(messages)
    _assert_slack_message_sent_to_channel("vpc-peering-alerts")
    _assert_slack_message_sent("vpc peering connection with unknown account")
    _assert_slack_message_sent("@some-team-name")


def test_compliance_alerter_main_password_policy_audit(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(build_event(PASSWORD_POLICY_KEY))
    ca.send(messages)
    _assert_slack_message_sent_to_channel("the-alerting-channel")
    _assert_slack_message_sent("password policy compliance enforcement success")
    _assert_slack_message_sent("@some-team-name")


def test_codepipeline_sns_event(helper_test_config: Any) -> None:
    test_event = set_event_account_id(
        account_id=helper_test_config.account_id,
        test_event=load_json_resource("codepipeline_event.json"),
    )
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(test_event)
    ca.send(messages)
    _assert_slack_message_sent_to_channel("codepipeline-alerts")
    _assert_slack_message_sent("@some-team-name")


def test_codebuild_sns_event(helper_test_config: Any) -> None:
    test_event = set_event_account_id(
        account_id=helper_test_config.account_id,
        test_event=load_json_resource("codebuild_event.json"),
    )
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(test_event)
    ca.send(messages)
    _assert_slack_message_sent_to_channel("codebuild-alerts")
    _assert_slack_message_sent("@some-team-name")


def test_guardduty_sns_event(helper_test_config: Any, _org_client: BaseClient) -> None:
    mock_org_client = _setup_org_sub_account(org_client=_org_client, account_name="sub-account-name")
    sub_account_id = mock_org_client.list_accounts()["Accounts"][-1]["Id"]
    test_event = set_event_account_id(
        account_id=sub_account_id,
        test_event=load_json_resource("guardduty_event.json"),
    )
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=AwsOrgClient(mock_org_client),
        )
    )

    # we want to alert with the name of the sub account not the main guardduty account
    message = json.loads(test_event["Records"][0]["Sns"]["Message"])
    message["detail"]["accountId"] = sub_account_id
    test_event["Records"][0]["Sns"]["Message"] = json.dumps(message)

    messages = ca.generate_slack_messages(test_event)
    ca.send(messages)

    _assert_slack_message_sent_to_channel("guardduty-alerts")
    _assert_slack_message_sent_to_channel("the-alerting-channel")
    _assert_slack_message_sent("sub-account-name")
    _assert_slack_message_sent("@some-team-name")


def test_unknown_sns_event(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    messages = ca.generate_slack_messages(load_json_resource("unknown_sns_event.json"))
    ca.send(messages)
    _assert_no_slack_message_sent()


def test_unsupported_event(helper_test_config: Any) -> None:
    ca = compliance_alerter.ComplianceAlerter(
        config=Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )
    with pytest.raises(UnsupportedEventException, match="a_value"):
        messages = ca.generate_slack_messages({"a_key": "a_value"})
        ca.send(messages)
    _assert_no_slack_message_sent()


# Helper functions
@dataclass
class HelperTestConfig:
    config_s3_client: AwsS3Client
    report_s3_client: AwsS3Client
    ssm_client: AwsSsmClient
    org_client: AwsOrgClient
    account_id: str


@pytest.fixture(autouse=True)
def helper_test_config(
    _ssm_client: BaseClient, _org_client: BaseClient, _config_s3_client: BaseClient, _report_s3_client: BaseClient
) -> Iterator[HelperTestConfig]:
    mock_org_client = _setup_org_sub_account(_org_client)
    sub_account_id = mock_org_client.list_accounts()["Accounts"][-1]["Id"]
    mock_config_s3_client = setup_config_bucket(_config_s3_client)
    mock_report_s3_client = setup_report_bucket(_report_s3_client, sub_account_id)
    mock_ssm_client = _setup_ssm_parameters(_ssm_client)
    htc = HelperTestConfig(
        config_s3_client=AwsS3Client(mock_config_s3_client),
        report_s3_client=AwsS3Client(mock_report_s3_client),
        ssm_client=AwsSsmClient(mock_ssm_client),
        org_client=AwsOrgClient(mock_org_client),
        account_id=sub_account_id,
    )
    yield htc


@pytest.fixture(autouse=True)
def _setup_environment(monkeypatch: Any) -> None:
    env_vars = {
        "AUDIT_REPORT_DASHBOARD_URL": "the-dashboard",
        "AWS_ACCESS_KEY_ID": "the-access-key-id",
        "AWS_SECRET_ACCESS_KEY": "the-secret-access-key",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_ACCOUNT": "111222333444",
        "CENTRAL_CHANNEL": CHANNEL,
        "CONFIG_BUCKET": CONFIG_BUCKET,
        "CONFIG_BUCKET_READ_ROLE": "the-config-bucket-read-role",
        "REPORT_BUCKET_READ_ROLE": "the-report-bucket-read-role",
        "S3_AUDIT_REPORT_KEY": S3_KEY,
        "IAM_AUDIT_REPORT_KEY": IAM_KEY,
        "GITHUB_AUDIT_REPORT_KEY": GITHUB_KEY,
        "GITHUB_WEBHOOK_REPORT_KEY": GITHUB_WEBHOOK_KEY,
        "GITHUB_WEBHOOK_HOST_IGNORE_LIST": GITHUB_WEBHOOK_HOST_IGNORE_LIST,
        "GUARDDUTY_RUNBOOK_URL": "the-gd-runbook",
        "PASSWORD_POLICY_AUDIT_REPORT_KEY": PASSWORD_POLICY_KEY,
        "SLACK_API_URL": SLACK_API_URL,
        "SLACK_USERNAME_KEY": SLACK_USERNAME_KEY,
        "SLACK_TOKEN_KEY": SLACK_TOKEN_KEY,
        "SSM_READ_ROLE": "the-ssm-read-role",
        "VPC_AUDIT_REPORT_KEY": VPC_KEY,
        "PUBLIC_QUERY_AUDIT_REPORT_KEY": PUBLIC_QUERY_KEY,
        "VPC_PEERING_AUDIT_REPORT_KEY": VPC_PEERING_KEY,
        "EC2_AUDIT_REPORT_KEY": EC2_KEY,
        "LOG_LEVEL": "DEBUG",
        "ORG_ACCOUNT": "ORG-ACCOUNT-ID-12374234",
        "ORG_READ_ROLE": "the-org-read-role",
        "VPC_RESOLVER_AUDIT_REPORT_KEY": "vpc resolver audit report key",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture(autouse=True)
def _ssm_client() -> Iterator[BaseClient]:
    with mock_ssm():
        yield boto3.client("ssm")


def _setup_ssm_parameters(ssm_client: BaseClient) -> BaseClient:
    ssm_client.put_parameter(Name=SLACK_USERNAME_KEY, Value="the-slack-username", Type="SecureString")
    ssm_client.put_parameter(Name=SLACK_TOKEN_KEY, Value="the-slack-username", Type="SecureString")
    return ssm_client


@pytest.fixture(autouse=True)
def _org_client() -> Iterator[BaseClient]:
    with mock_organizations():
        yield boto3.client("organizations")


def _setup_org_sub_account(org_client: BaseClient, account_name: str = "test-account-name") -> BaseClient:
    org_client.create_organization(FeatureSet="ALL")
    account_id = org_client.create_account(AccountName=account_name, Email="example@example.com")[
        "CreateAccountStatus"
    ]["AccountId"]
    org_client.tag_resource(
        ResourceId=account_id,
        Tags=[
            {"Key": "team_slack_handle", "Value": "@some-team-name"},
        ],
    )
    return org_client


@pytest.fixture(autouse=True)
def _config_s3_client() -> Iterator[BaseClient]:
    with mock_s3():
        yield boto3.client("s3")


def setup_config_bucket(s3_client: BaseClient) -> BaseClient:
    s3_client.create_bucket(Bucket=CONFIG_BUCKET)
    s3_client.put_object(
        Bucket=CONFIG_BUCKET, Key="filters/a", Body=json.dumps([{"item": "mischievous-bucket", "reason": "because"}])
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET, Key="filters/b", Body=json.dumps([{"item": "bad-repo-no-admin", "reason": "because"}])
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET, Key="mappings/all", Body=json.dumps([{"channel": "the-alerting-channel"}])
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET, Key="mappings/a", Body=json.dumps([{"channel": "alerts", "items": ["bad-bucket"]}])
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET,
        Key="mappings/b",
        Body=json.dumps([{"channel": "alerts", "items": ["bad-repo-no-signing"]}]),
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET, Key="mappings/c", Body=json.dumps([{"channel": "alerts", "items": ["VPC flow logs"]}])
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET,
        Key="mappings/d",
        Body=json.dumps([{"channel": "alerts", "items": ["https://unknown-host.com"]}]),
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET, Key="mappings/e", Body=json.dumps([{"channel": "alerts", "items": ["password policy"]}])
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET,
        Key="mappings/codepipeline",
        Body=json.dumps([{"channel": "codepipeline-alerts", "compliance_item_types": ["codepipeline"]}]),
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET,
        Key="mappings/codebuild",
        Body=json.dumps([{"channel": "codebuild-alerts", "compliance_item_types": ["codebuild"]}]),
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET,
        Key="mappings/guardduty",
        Body=json.dumps([{"channel": "guardduty-alerts", "compliance_item_types": ["guardduty"]}]),
    )
    s3_client.put_object(
        Bucket=CONFIG_BUCKET,
        Key="mappings/vpc_peering",
        Body=json.dumps([{"channel": "vpc-peering-alerts", "compliance_item_types": ["vpc_peering"]}]),
    )
    return s3_client


@pytest.fixture(autouse=True)
def _report_s3_client() -> Iterator[BaseClient]:
    with mock_s3():
        yield boto3.client("s3")


def setup_report_bucket(s3_client: BaseClient, account_id: str) -> BaseClient:
    s3_client = boto3.client("s3")
    s3_client.create_bucket(Bucket=REPORT_BUCKET)
    s3_client.put_object(
        Bucket=REPORT_BUCKET, Key=S3_KEY, Body=json.dumps(set_account_id_in_report(account_id, s3_report))
    )
    s3_client.put_object(
        Bucket=REPORT_BUCKET,
        Key=PASSWORD_POLICY_KEY,
        Body=json.dumps(set_account_id_in_report(account_id, password_policy_report)),
    )
    s3_client.put_object(
        Bucket=REPORT_BUCKET, Key=VPC_KEY, Body=json.dumps(set_account_id_in_report(account_id, vpc_report))
    )
    s3_client.put_object(
        Bucket=REPORT_BUCKET,
        Key=VPC_PEERING_KEY,
        Body=json.dumps(set_account_id_in_report(account_id, deepcopy(vpc_peering_audit))),
    )
    s3_client.put_object(Bucket=REPORT_BUCKET, Key=GITHUB_KEY, Body=json.dumps(github_report))
    s3_client.put_object(Bucket=REPORT_BUCKET, Key=GITHUB_WEBHOOK_KEY, Body=json.dumps(github_webhook_report))
    return s3_client


def set_account_id_in_report(account_id: str, report_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for report in report_list:
        report["account"]["identifier"] = account_id
    return report_list


@pytest.fixture(autouse=True)
def _mock_slack_notifier() -> Iterator[Any]:
    httpretty.enable()
    httpretty.register_uri(
        httpretty.POST, SLACK_API_URL, body=json.dumps({"successfullySentTo": [CHANNEL]}), status=200
    )
    yield
    httpretty.disable()
    httpretty.reset()


def set_event_account_id(account_id: str, test_event: Dict[str, Any]) -> Dict[str, Any]:
    # moto does not let us set the expected account id
    # so we change the event to match the mocked value
    message = json.loads(test_event["Records"][0]["Sns"]["Message"])
    message["account"] = account_id
    test_event["Records"][0]["Sns"]["Message"] = json.dumps(message)
    return dict(test_event)


def build_event(report_key: str) -> Dict[str, Any]:
    return {
        "Records": [{"eventVersion": "2.1", "s3": {"bucket": {"name": REPORT_BUCKET}, "object": {"key": report_key}}}]
    }


def _assert_slack_message_sent(message: str) -> None:
    message_request = httpretty.last_request().body.decode("utf-8")
    print("_assert_slack_message_sent ===> ", message_request)
    assert message in message_request


def _assert_slack_message_sent_to_channel(channel: str) -> None:
    last_request = httpretty.last_request()
    assert type(last_request) is not httpretty.core.HTTPrettyRequestEmpty, "No requests were made to slack"
    message_request = last_request.body.decode("utf-8")
    message_json = json.loads(message_request)
    assert channel in message_json["channelLookup"]["slackChannels"]


def _assert_no_slack_message_sent() -> None:
    last_request = httpretty.last_request()
    assert type(last_request) is httpretty.core.HTTPrettyRequestEmpty, "A request was made to slack"


def load_json_resource(filename: str) -> Any:
    with open(os.path.join("tests", "resources", filename), "r") as json_file:
        resource = json.load(json_file)
    return resource
