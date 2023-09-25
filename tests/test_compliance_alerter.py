from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import Mock, patch

import os
from copy import deepcopy
from typing import Any, Dict, List

import boto3
import httpretty
import pytest

import json

from moto import mock_s3, mock_ssm, mock_sts, mock_organizations

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

channel = "the-alerting-channel"
config = "the_config_bucket"
report = "the_report_bucket"
s3_key = "s3_audit"
iam_key = "iam_audit"
github_key = "github_audit"
github_webhook_key = "github_webhook"
github_webhook_host_ignore_list = "known-host.com,known-host2.com"
vpc_key = "vpc_audit"
vpc_peering_key = "vpc_peering_audit"
public_query_key = "public_query_audit"
ec2_key = "ec2_audit"
password_policy_key = "password_policy_audit"
slack_api_url = "https://the-slack-api-url.com"
slack_username_key = "the-slack-username-key"
slack_token_key = "the-slack-token-key"

@dataclass
class HelperTestConfig():
    config_s3_client: AwsS3Client
    report_s3_client: AwsS3Client
    ssm_client: AwsSsmClient
    org_client: AwsOrgClient
    account_id: str


@pytest.fixture(autouse=True)
def _setup_environment(monkeypatch):
    env_vars = {
        "AUDIT_REPORT_DASHBOARD_URL": "the-dashboard",
        "AWS_ACCESS_KEY_ID": "the-access-key-id",
        "AWS_SECRET_ACCESS_KEY": "the-secret-access-key",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_ACCOUNT": "111222333444",
        "CENTRAL_CHANNEL": channel,
        "CONFIG_BUCKET": config,
        "CONFIG_BUCKET_READ_ROLE": "the-config-bucket-read-role",
        "REPORT_BUCKET_READ_ROLE": "the-report-bucket-read-role",
        "S3_AUDIT_REPORT_KEY": s3_key,
        "IAM_AUDIT_REPORT_KEY": iam_key,
        "GITHUB_AUDIT_REPORT_KEY": github_key,
        "GITHUB_WEBHOOK_REPORT_KEY": github_webhook_key,
        "GITHUB_WEBHOOK_HOST_IGNORE_LIST": github_webhook_host_ignore_list,
        "GUARDDUTY_RUNBOOK_URL": "the-gd-runbook",
        "PASSWORD_POLICY_AUDIT_REPORT_KEY": password_policy_key,
        "SLACK_API_URL": slack_api_url,
        "SLACK_USERNAME_KEY": slack_username_key,
        "SLACK_TOKEN_KEY": slack_token_key,
        "SSM_READ_ROLE": "the-ssm-read-role",
        "VPC_AUDIT_REPORT_KEY": vpc_key,
        "PUBLIC_QUERY_AUDIT_REPORT_KEY": public_query_key,
        "VPC_PEERING_AUDIT_REPORT_KEY": vpc_peering_key,
        "EC2_AUDIT_REPORT_KEY": ec2_key,
        "LOG_LEVEL": "DEBUG",
        "ORG_ACCOUNT": "ORG-ACCOUNT-ID-12374234",
        "ORG_READ_ROLE": "the-org-read-role",
        "VPC_RESOLVER_AUDIT_REPORT_KEY": "vpc resolver audit report key",
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)


@pytest.fixture(autouse=True)
def _setup_ssm_parameters():
    with mock_ssm():
        ssm_client =  boto3.client('ssm')
        ssm_client.put_parameter(Name=slack_username_key, Value="the-slack-username", Type="SecureString")
        ssm_client.put_parameter(Name=slack_token_key, Value="the-slack-username", Type="SecureString")
        yield ssm_client


@pytest.fixture(autouse=True)
def _setup_org_sub_account(account_name: str = "test-account-name") -> str:
    with mock_organizations():
        org_client = boto3.client("organizations")
        org_client.create_organization(FeatureSet="ALL")
        account_id = org_client.create_account(AccountName=account_name, Email="example@example.com")["CreateAccountStatus"][
            "AccountId"
        ]
        org_client.tag_resource(
            ResourceId=account_id,
            Tags=[
                {"Key": "team_slack_handle", "Value": "@some-team-name"},
            ],
        )
        yield org_client
        # return str(account_id)

@pytest.fixture(autouse=True)
def _setup_config_bucket():
    with mock_s3():
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=config)
        s3_client.put_object(
            Bucket=config, Key="filters/a", Body=json.dumps([{"item": "mischievous-bucket", "reason": "because"}])
        )
        s3_client.put_object(
            Bucket=config, Key="filters/b", Body=json.dumps([{"item": "bad-repo-no-admin", "reason": "because"}])
        )
        s3_client.put_object(Bucket=config, Key="mappings/all", Body=json.dumps([{"channel": "the-alerting-channel"}]))
        s3_client.put_object(
            Bucket=config, Key="mappings/a", Body=json.dumps([{"channel": "alerts", "items": ["bad-bucket"]}])
        )
        s3_client.put_object(
            Bucket=config, Key="mappings/b", Body=json.dumps([{"channel": "alerts", "items": ["bad-repo-no-signing"]}])
        )
        s3_client.put_object(
            Bucket=config, Key="mappings/c", Body=json.dumps([{"channel": "alerts", "items": ["VPC flow logs"]}])
        )
        s3_client.put_object(
            Bucket=config,
            Key="mappings/d",
            Body=json.dumps([{"channel": "alerts", "items": ["https://unknown-host.com"]}]),
        )
        s3_client.put_object(
            Bucket=config, Key="mappings/e", Body=json.dumps([{"channel": "alerts", "items": ["password policy"]}])
        )
        s3_client.put_object(
            Bucket=config,
            Key="mappings/codepipeline",
            Body=json.dumps([{"channel": "codepipeline-alerts", "compliance_item_types": ["codepipeline"]}]),
        )
        s3_client.put_object(
            Bucket=config,
            Key="mappings/codebuild",
            Body=json.dumps([{"channel": "codebuild-alerts", "compliance_item_types": ["codebuild"]}]),
        )
        s3_client.put_object(
            Bucket=config,
            Key="mappings/guardduty",
            Body=json.dumps([{"channel": "guardduty-alerts", "compliance_item_types": ["guardduty"]}]),
        )
        s3_client.put_object(
            Bucket=config,
            Key="mappings/vpc_peering",
            Body=json.dumps([{"channel": "vpc-peering-alerts", "compliance_item_types": ["vpc_peering"]}]),
        )
        yield s3_client

# @pytest.fixture(autouse=True)
def setup_report_bucket(account_id):
    with mock_s3():
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=report)
        s3_client.put_object(Bucket=report, Key=s3_key, Body=json.dumps(set_account_id_in_report(account_id, s3_report)))
        s3_client.put_object(
            Bucket=report,
            Key=password_policy_key,
            Body=json.dumps(self.set_account_id_in_report(password_policy_report)),
        )
        s3_client.put_object(Bucket=report, Key=vpc_key, Body=json.dumps(set_account_id_in_report(account_id, vpc_report)))
        s3_client.put_object(
            Bucket=report,
            Key=vpc_peering_key,
            Body=json.dumps(set_account_id_in_report(account_id, deepcopy(vpc_peering_audit))),
        )
        s3_client.put_object(Bucket=report, Key=github_key, Body=json.dumps(github_report))
        s3_client.put_object(Bucket=report, Key=github_webhook_key, Body=json.dumps(github_webhook_report))
        yield s3_client

def set_account_id_in_report(self, account_id: str, report_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for report in report_list:
        report["account"]["identifier"] = account_id
    return report_list

@pytest.fixture(autouse=True)
def helper_test_config(_setup_ssm_parameters, _setup_org_sub_account, _setup_config_bucket) -> HelperTestConfig:
    mock_report_s3_client = setup_report_bucket(_setup_org_sub_account)
    first_sub_account_id = _setup_org_sub_account.list_accounts()["Accounts"][0]["Id"]
    htc = HelperTestConfig(
        config_s3_client=AwsS3Client(_setup_config_bucket),
        report_s3_client=AwsS3Client(mock_report_s3_client),
        ssm_client=AwsSsmClient(_setup_ssm_parameters),
        org_client=AwsOrgClient(_setup_org_sub_account),
        account_id=first_sub_account_id
    )
    print("HTC")
    print(htc.config_s3_client.list_objects("the_config_bucket", "filter/"))
    
    yield htc


@pytest.fixture(autouse=True)
def _mock_slack_notifier():
    httpretty.enable()
    httpretty.register_uri(
        httpretty.POST, slack_api_url, body=json.dumps({"successfullySentTo": [channel]}), status=200
    )
    yield
    httpretty.disable()


def test_send(helper_test_config):
    print(helper_test_config.ssm_client.get_parameter(slack_username_key))
    print(helper_test_config.config_s3_client.list_objects("the_config_bucket", "filter/"))
    ca = compliance_alerter.ComplianceAlerter(
        config = Config(
            config_s3_client=helper_test_config.config_s3_client,
            report_s3_client=helper_test_config.report_s3_client,
            ssm_client=helper_test_config.ssm_client,
            org_client=helper_test_config.org_client,
        )
    )

    un = ca.debug_get_slack_username()
    assert un == "the-slack-username"

    ca.send(
        slack_messages=[
            SlackMessage(
                channels=[channel],
                header="test-account 111222333444 eu-west-2 @some-team-name",
                title="aTitle",
                text="Words of Advice",
                color=Severity.HIGH
            )
        ]
    )

    message = "@some-team-name"
    message_request = httpretty.last_request().body.decode("utf-8")
    assert message in  message_request


def set_event_account_id(account_id: str, test_event: Dict[str, Any]) -> Dict[str, Any]:
    # moto does not let us set the expected account id
    # so we change the event to match the mocked value
    message = json.loads(test_event["Records"][0]["Sns"]["Message"])
    message["account"] = account_id
    test_event["Records"][0]["Sns"]["Message"] = json.dumps(message)
    return dict(test_event)

def test_new_codebuild_sns_event(helper_test_config) -> None:
    test_event = set_event_account_id(
        account_id=helper_test_config.account_id,
        test_event=TestComplianceAlerter.load_json_resource("codebuild_event.json"),
    )
    print("ACCT_ID", helper_test_config.account_id)
    print("Config S3 client", helper_test_config.config_s3_client)
    helper_test_config.config_s3_client.list_objects("the_config_bucket", "filter/")

    ca = compliance_alerter.ComplianceAlerter(
        config = Config(
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
    # message_request = httpretty.last_request().body.decode("utf-8")
    # assert "@some-team-name" in  message_request

def _assert_slack_message_sent(message: str) -> None:
    message_request = httpretty.last_request().body.decode("utf-8")
    print(message_request)
    assert message in  message_request

def _assert_slack_message_sent_to_channel(channel: str) -> None:
    last_request = httpretty.last_request()
    assert type(last_request) != httpretty.core.HTTPrettyRequestEmpty, "No requests were made to slack"
    message_request = last_request.body.decode("utf-8")
    message_json = json.loads(message_request)
    assert channel in message_json["channelLookup"]["slackChannels"]

def _assert_no_slack_message_sent() -> None:
    last_request = httpretty.last_request()
    assert type(last_request) == httpretty.core.HTTPrettyRequestEmpty, "A request was made to slack"







@mock_s3
@mock_ssm
@mock_sts
@mock_organizations
@httpretty.activate
class TestComplianceAlerter(TestCase):
    def setUp(self) -> None:
        self._account_id = self._setup_org_sub_account()
        self._setup_environment()
        self._setup_report_bucket()
        self._setup_config_bucket()
        self._setup_ssm_parameters()
        self._mock_slack_notifier()
        print("1) ***httpretty.is_enabled", httpretty.is_enabled())

    def tearDown(self) -> None:
        self._delete_bucket(report)
        self._delete_bucket(config)
        self._delete_ssm_parameters()

    def test_compliance_alerter_main_s3_audit(self) -> None:
        compliance_alerter.main(self.build_event(s3_key))
        self._assert_slack_message_sent_to_channel("the-alerting-channel")
        self._assert_slack_message_sent("bad-bucket")
        self._assert_slack_message_sent("@some-team-name")

    def test_compliance_alerter_main_github_audit(self) -> None:
        compliance_alerter.main(self.build_event(github_key))
        self._assert_slack_message_sent_to_channel("the-alerting-channel")
        self._assert_slack_message_sent("bad-repo-no-signing")

    def test_compliance_alerter_main_github_webhook(self) -> None:
        compliance_alerter.main(self.build_event(github_webhook_key))
        self._assert_slack_message_sent_to_channel("the-alerting-channel")
        self._assert_slack_message_sent("https://unknown-host.com")

    def test_compliance_alerter_main_vpc_audit(self) -> None:
        compliance_alerter.main(self.build_event(vpc_key))
        self._assert_slack_message_sent_to_channel("the-alerting-channel")
        self._assert_slack_message_sent("VPC flow logs compliance enforcement success")
        self._assert_slack_message_sent("@some-team-name")

    def test_compliance_alerter_main_vpc_peering_audit(self) -> None:
        compliance_alerter.main(self.build_event(vpc_peering_key))
        self._assert_slack_message_sent_to_channel("vpc-peering-alerts")
        self._assert_slack_message_sent("vpc peering connection with unknown account")
        self._assert_slack_message_sent("@some-team-name")

    def test_compliance_alerter_main_password_policy_audit(self) -> None:
        compliance_alerter.main(self.build_event(password_policy_key))
        self._assert_slack_message_sent_to_channel("the-alerting-channel")
        self._assert_slack_message_sent("password policy compliance enforcement success")
        self._assert_slack_message_sent("@some-team-name")

    def test_codepipeline_sns_event(self) -> None:
        test_event = self.set_event_account_id(
            account_id=self._account_id,
            test_event=TestComplianceAlerter.load_json_resource("codepipeline_event.json"),
        )
        compliance_alerter.main(test_event)
        self._assert_slack_message_sent_to_channel("codepipeline-alerts")
        self._assert_slack_message_sent("@some-team-name")

    def test_codebuild_sns_event(self) -> None:
        test_event = self.set_event_account_id(
            account_id=self._account_id,
            test_event=TestComplianceAlerter.load_json_resource("codebuild_event.json"),
        )
        compliance_alerter.main(test_event)

        # self._assert_slack_message_sent_to_channel("codebuild-alerts")
        # self._assert_slack_message_sent("@some-team-name")

    def test_guardduty_sns_event(self) -> None:
        test_event = self.set_event_account_id(
            account_id=self._account_id,
            test_event=TestComplianceAlerter.load_json_resource("guardduty_event.json"),
        )

        # we want to alert with the name of the sub account not the main guardduty account
        sub_account_id = self._setup_org_sub_account(account_name="sub-account-name")
        message = json.loads(test_event["Records"][0]["Sns"]["Message"])
        message["detail"]["accountId"] = sub_account_id
        test_event["Records"][0]["Sns"]["Message"] = json.dumps(message)

        compliance_alerter.main(test_event)

        self._assert_slack_message_sent_to_channel("guardduty-alerts")
        self._assert_slack_message_sent_to_channel("the-alerting-channel")
        self._assert_slack_message_sent("sub-account-name")
        self._assert_slack_message_sent("@some-team-name")

    def set_event_account_id(self, account_id: str, test_event: Dict[str, Any]) -> Dict[str, Any]:
        # moto does not let us set the expected account id
        # so we change the event to match the mocked value
        message = json.loads(test_event["Records"][0]["Sns"]["Message"])
        message["account"] = account_id
        test_event["Records"][0]["Sns"]["Message"] = json.dumps(message)
        return dict(test_event)

    def test_unknown_sns_event(self) -> None:
        compliance_alerter.main(TestComplianceAlerter.load_json_resource("unknown_sns_event.json"))
        self._assert_no_slack_message_sent()

    def test_unsupported_event(self) -> None:
        with self.assertRaisesRegex(UnsupportedEventException, "a_value"):
            compliance_alerter.main({"a_key": "a_value"})
        self._assert_no_slack_message_sent()

    @staticmethod
    def build_event(report_key: str) -> Dict[str, Any]:
        return {"Records": [{"eventVersion": "2.1", "s3": {"bucket": {"name": report}, "object": {"key": report_key}}}]}

    @staticmethod
    def _setup_org_sub_account(account_name: str = "test-account-name") -> str:
        org = boto3.client("organizations")
        org.create_organization(FeatureSet="ALL")
        account_id = org.create_account(AccountName=account_name, Email="example@example.com")["CreateAccountStatus"][
            "AccountId"
        ]
        org.tag_resource(
            ResourceId=account_id,
            Tags=[
                {"Key": "team_slack_handle", "Value": "@some-team-name"},
            ],
        )
        return str(account_id)

    @staticmethod
    def _delete_ssm_parameters() -> None:
        ssm = boto3.client("ssm")
        ssm.delete_parameter(Name=slack_username_key)
        ssm.delete_parameter(Name=slack_token_key)

    @staticmethod
    def _delete_bucket(bucket_name: str) -> None:
        config_bucket = boto3.resource("s3").Bucket(bucket_name)
        config_bucket.objects.all().delete()
        config_bucket.delete()

    @staticmethod
    def _mock_slack_notifier() -> None:
        httpretty.register_uri(
            httpretty.POST, slack_api_url, body=json.dumps({"successfullySentTo": [channel]}), status=200
        )

    def _assert_slack_message_sent(self, message: str) -> None:
        message_request = httpretty.last_request().body.decode("utf-8")
        self.assertIn(message, message_request)

    def _assert_slack_message_sent_to_channel(self, channel: str) -> None:
        last_request = httpretty.last_request()
        assert type(last_request) != httpretty.core.HTTPrettyRequestEmpty, "No requests were made to slack"
        message_request = last_request.body.decode("utf-8")
        message_json = json.loads(message_request)
        self.assertIn(channel, message_json["channelLookup"]["slackChannels"])

    def _assert_no_slack_message_sent(self) -> None:
        last_request = httpretty.last_request()
        assert type(last_request) == httpretty.core.HTTPrettyRequestEmpty, "A request was made to slack"

    @staticmethod
    def load_json_resource(filename: str) -> Any:
        with open(os.path.join("tests", "resources", filename), "r") as json_file:
            resource = json.load(json_file)
        return resource
