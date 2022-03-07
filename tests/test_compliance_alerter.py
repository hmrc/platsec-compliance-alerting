from unittest import TestCase
from unittest.mock import patch

import os
from typing import Any, Dict, List

import boto3
import httpretty

import json

from moto import mock_s3, mock_ssm, mock_sts, mock_organizations

from src import compliance_alerter
from src.data.exceptions import UnsupportedEventException

from tests.fixtures.github_compliance import github_report
from tests.fixtures.github_webhook_compliance import github_webhook_report
from tests.fixtures.s3_compliance_alerter import s3_report
from tests.fixtures.vpc_compliance import vpc_report
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
password_policy_key = "password_policy_audit"
slack_api_url = "https://the-slack-api-url.com"
slack_username_key = "the-slack-username-key"
slack_token_key = "the-slack-token-key"


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

        self._assert_slack_message_sent_to_channel("codebuild-alerts")
        self._assert_slack_message_sent("@some-team-name")

    def test_guardduty_sns_event(self) -> None:
        test_event = self.set_event_account_id(
            account_id=self._account_id,
            test_event=TestComplianceAlerter.load_json_resource("guardduty_event.json"),
        )

        compliance_alerter.main(test_event)

        self._assert_slack_message_sent_to_channel("guardduty-alerts")
        self._assert_slack_message_sent_to_channel("the-alerting-channel")
        self._assert_slack_message_sent("test-account-name")
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
    def _setup_environment() -> None:
        patch.dict(
            os.environ,
            {
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
                "LOG_LEVEL": "DEBUG",
                "ORG_ACCOUNT": "ORG-ACCOUNT-ID-12374234",
                "ORG_READ_ROLE": "the-org-read-role",
            },
            clear=True,
        ).start()

    def _setup_report_bucket(self) -> None:
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=report)
        s3.put_object(Bucket=report, Key=s3_key, Body=json.dumps(self.set_account_id_in_bucket_report(s3_report)))
        s3.put_object(
            Bucket=report,
            Key=password_policy_key,
            Body=json.dumps(self.set_account_id_in_bucket_report(password_policy_report)),
        )
        s3.put_object(Bucket=report, Key=vpc_key, Body=json.dumps(self.set_account_id_in_bucket_report(vpc_report)))

        s3.put_object(Bucket=report, Key=github_key, Body=json.dumps(github_report))
        s3.put_object(Bucket=report, Key=github_webhook_key, Body=json.dumps(github_webhook_report))

    def set_account_id_in_bucket_report(self, report_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for report in report_list:
            report["account"]["identifier"] = self._account_id
        return report_list

    @staticmethod
    def _setup_config_bucket() -> None:
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=config)
        s3.put_object(
            Bucket=config, Key="filters/a", Body=json.dumps([{"item": "mischievous-bucket", "reason": "because"}])
        )
        s3.put_object(
            Bucket=config, Key="filters/b", Body=json.dumps([{"item": "bad-repo-no-admin", "reason": "because"}])
        )
        s3.put_object(Bucket=config, Key="mappings/all", Body=json.dumps([{"channel": "the-alerting-channel"}]))
        s3.put_object(
            Bucket=config, Key="mappings/a", Body=json.dumps([{"channel": "alerts", "items": ["bad-bucket"]}])
        )
        s3.put_object(
            Bucket=config, Key="mappings/b", Body=json.dumps([{"channel": "alerts", "items": ["bad-repo-no-signing"]}])
        )
        s3.put_object(
            Bucket=config, Key="mappings/c", Body=json.dumps([{"channel": "alerts", "items": ["VPC flow logs"]}])
        )
        s3.put_object(
            Bucket=config,
            Key="mappings/d",
            Body=json.dumps([{"channel": "alerts", "items": ["https://unknown-host.com"]}]),
        )
        s3.put_object(
            Bucket=config, Key="mappings/e", Body=json.dumps([{"channel": "alerts", "items": ["password policy"]}])
        )
        s3.put_object(
            Bucket=config,
            Key="mappings/codepipeline",
            Body=json.dumps([{"channel": "codepipeline-alerts", "compliance_item_types": ["codepipeline"]}]),
        )
        s3.put_object(
            Bucket=config,
            Key="mappings/codebuild",
            Body=json.dumps([{"channel": "codebuild-alerts", "compliance_item_types": ["codebuild"]}]),
        )
        s3.put_object(
            Bucket=config,
            Key="mappings/guardduty",
            Body=json.dumps([{"channel": "guardduty-alerts", "compliance_item_types": ["guardduty"]}]),
        )

    @staticmethod
    def _setup_ssm_parameters() -> None:
        ssm = boto3.client("ssm")
        ssm.put_parameter(Name=slack_username_key, Value="the-slack-username", Type="SecureString")
        ssm.put_parameter(Name=slack_token_key, Value="the-slack-username", Type="SecureString")

    @staticmethod
    def _setup_org_sub_account() -> str:
        org = boto3.client("organizations")
        org.create_organization(FeatureSet="ALL")
        account_id = org.create_account(AccountName="test-account-name", Email="example@example.com")[
            "CreateAccountStatus"
        ]["AccountId"]
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
