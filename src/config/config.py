from itertools import chain
from os import environ
from typing import Callable, Dict, Set

from src import T, error
from src.clients.aws_s3_client import AwsS3Client
from src.clients.aws_client_factory import AwsClientFactory
from src.config.notification_filter_config import NotificationFilterConfig
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.exceptions import ComplianceAlertingException, MissingConfigException, InvalidConfigException
from src.slack_notifier import SlackNotifierConfig


class Config:
    def get_aws_account(self) -> str:
        return self._get_env("AWS_ACCOUNT")

    def get_config_bucket(self) -> str:
        return self._get_env("CONFIG_BUCKET")

    def get_config_bucket_read_role(self) -> str:
        return self._get_env("CONFIG_BUCKET_READ_ROLE")

    @staticmethod
    def get_log_level() -> str:
        log_level_cfg = environ.get("LOG_LEVEL", "WARNING")
        log_level = log_level_cfg.upper()
        if log_level not in ["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG"]:
            raise InvalidConfigException(f"invalid LOG_LEVEL: {log_level_cfg}")

        return log_level

    def get_report_bucket_read_role(self) -> str:
        return self._get_env("REPORT_BUCKET_READ_ROLE")

    def get_s3_audit_report_key(self) -> str:
        return self._get_env("S3_AUDIT_REPORT_KEY")

    def get_iam_audit_report_key(self) -> str:
        return self._get_env("IAM_AUDIT_REPORT_KEY")

    def get_github_audit_report_key(self) -> str:
        return self._get_env("GITHUB_AUDIT_REPORT_KEY")

    def get_github_webhook_report_key(self) -> str:
        return self._get_env("GITHUB_WEBHOOK_REPORT_KEY")

    def get_vpc_audit_report_key(self) -> str:
        return self._get_env("VPC_AUDIT_REPORT_KEY")

    def get_slack_api_url(self) -> str:
        return self._get_env("SLACK_API_URL")

    def get_slack_username_key(self) -> str:
        return self._get_env("SLACK_USERNAME_KEY")

    def get_slack_token_key(self) -> str:
        return self._get_env("SLACK_TOKEN_KEY")

    def get_ssm_read_role(self) -> str:
        return self._get_env("SSM_READ_ROLE")

    def get_slack_notifier_config(self) -> SlackNotifierConfig:
        ssm = AwsClientFactory().get_ssm_client(self.get_aws_account(), self.get_ssm_read_role())
        return SlackNotifierConfig(
            username=ssm.get_parameter(self.get_slack_username_key()),
            token=ssm.get_parameter(self.get_slack_token_key()),
            api_url=self.get_slack_api_url(),
        )

    def get_report_s3_client(self) -> AwsS3Client:
        return AwsClientFactory().get_s3_client(self.get_aws_account(), self.get_report_bucket_read_role())

    def get_notification_filters(self) -> Set[NotificationFilterConfig]:
        return self._fetch_config_files("filters/", NotificationFilterConfig.from_dict)

    def get_notification_mappings(self) -> Set[NotificationMappingConfig]:
        return self._fetch_config_files("mappings/", NotificationMappingConfig.from_dict)

    @staticmethod
    def _get_env(key: str) -> str:
        try:
            return environ[key]
        except KeyError:
            raise MissingConfigException(f"environment variable {key}") from None

    def _fetch_config_files(self, prefix: str, mapper: Callable[[Dict[str, str]], T]) -> Set[T]:
        s3 = AwsClientFactory().get_s3_client(self.get_aws_account(), self.get_config_bucket_read_role())
        keys = s3.list_objects(self.get_config_bucket(), prefix)
        return set(chain.from_iterable(map(lambda key: self._load(key, mapper, s3), keys)))

    def _load(self, key: str, mapper: Callable[[Dict[str, str]], T], s3: AwsS3Client) -> Set[T]:
        try:
            return {mapper(item) for item in s3.read_object(self.get_config_bucket(), key)}
        except ComplianceAlertingException as err:
            error(self, f"unable to load config file '{key}': {err}")
            return set()
