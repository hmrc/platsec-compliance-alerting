from unittest import TestCase
from unittest.mock import patch

from os import environ
from typing import Any, Dict

import boto3
import httpretty

from json import dumps
from moto import mock_s3, mock_ssm, mock_sts

from src import compliance_alerter

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
@httpretty.activate
class TestComplianceAlerter(TestCase):
    def setUp(self) -> None:
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
        self._assert_slack_message_sent("bad-bucket")

    def test_compliance_alerter_main_github_audit(self) -> None:
        compliance_alerter.main(self.build_event(github_key))
        self._assert_slack_message_sent("bad-repo-no-signing")

    def test_compliance_alerter_main_github_webhook(self) -> None:
        compliance_alerter.main(self.build_event(github_webhook_key))
        self._assert_slack_message_sent("```unknown-host.com```")

    def test_compliance_alerter_main_vpc_audit(self) -> None:
        compliance_alerter.main(self.build_event(vpc_key))
        self._assert_slack_message_sent("VPC flow logs compliance enforcement success")

    def test_compliance_alerter_main_password_policy_audit(self) -> None:
        compliance_alerter.main(self.build_event(password_policy_key))
        self._assert_slack_message_sent("password policy compliance enforcement success")

    @staticmethod
    def build_event(report_key: str) -> Dict[str, Any]:
        return {"Records": [{"eventVersion": "2.1", "s3": {"bucket": {"name": report}, "object": {"key": report_key}}}]}

    @staticmethod
    def _setup_environment() -> None:
        patch.dict(
            environ,
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
                "PASSWORD_POLICY_AUDIT_REPORT_KEY": password_policy_key,
                "SLACK_API_URL": slack_api_url,
                "SLACK_USERNAME_KEY": slack_username_key,
                "SLACK_TOKEN_KEY": slack_token_key,
                "SSM_READ_ROLE": "the-ssm-read-role",
                "VPC_AUDIT_REPORT_KEY": vpc_key,
            },
            clear=True,
        ).start()

    @staticmethod
    def _setup_report_bucket() -> None:
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=report)
        s3.put_object(Bucket=report, Key=s3_key, Body=dumps(s3_report))
        s3.put_object(Bucket=report, Key=github_key, Body=dumps(github_report))
        s3.put_object(Bucket=report, Key=github_webhook_key, Body=dumps(github_webhook_report))
        s3.put_object(Bucket=report, Key=vpc_key, Body=dumps(vpc_report))
        s3.put_object(Bucket=report, Key=password_policy_key, Body=dumps(password_policy_report))

    @staticmethod
    def _setup_config_bucket() -> None:
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=config)
        s3.put_object(Bucket=config, Key="filters/a", Body=dumps([{"item": "mischievous-bucket", "reason": "because"}]))
        s3.put_object(Bucket=config, Key="filters/b", Body=dumps([{"item": "bad-repo-no-admin", "reason": "because"}]))
        s3.put_object(Bucket=config, Key="mappings/all", Body=dumps([{"channel": "the-alerting-channel"}]))
        s3.put_object(Bucket=config, Key="mappings/a", Body=dumps([{"channel": "alerts", "items": ["bad-bucket"]}]))
        s3.put_object(
            Bucket=config, Key="mappings/b", Body=dumps([{"channel": "alerts", "items": ["bad-repo-no-signing"]}])
        )
        s3.put_object(Bucket=config, Key="mappings/c", Body=dumps([{"channel": "alerts", "items": ["VPC flow logs"]}]))
        s3.put_object(
            Bucket=config, Key="mappings/d", Body=dumps([{"channel": "alerts", "items": ["```unknown-host.com```"]}])
        )
        s3.put_object(
            Bucket=config, Key="mappings/e", Body=dumps([{"channel": "alerts", "items": ["password policy"]}])
        )

    @staticmethod
    def _setup_ssm_parameters() -> None:
        ssm = boto3.client("ssm")
        ssm.put_parameter(Name=slack_username_key, Value="the-slack-username", Type="SecureString")
        ssm.put_parameter(Name=slack_token_key, Value="the-slack-username", Type="SecureString")

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
        httpretty.register_uri(httpretty.POST, slack_api_url, body=dumps({"successfullySentTo": [channel]}), status=200)

    def _assert_slack_message_sent(self, message: str) -> None:
        message_request = httpretty.last_request().body.decode("utf-8")
        print(message_request)
        self.assertIn(message, message_request)
        self.assertIn('"slackChannels": ["alerts", "the-alerting-channel"]', message_request)
