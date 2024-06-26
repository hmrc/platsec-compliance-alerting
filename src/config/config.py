import logging
from logging import Logger
from itertools import chain
from os import environ
from typing import Callable, Dict, Set, List

from src import T, error
from src.clients.aws_s3_client import AwsS3Client
from src.clients.aws_org_client import AwsOrgClient
from src.clients.aws_ssm_client import AwsSsmClient
from src.config.notification_filter_config import NotificationFilterConfig
from src.config.notification_mapping_config import NotificationMappingConfig
from src.config.slack_notifier_config import SlackNotifierConfig
from src.data.exceptions import ComplianceAlertingException, MissingConfigException, InvalidConfigException


class Config:
    def __init__(
        self,
        config_s3_client: AwsS3Client,
        report_s3_client: AwsS3Client,
        ssm_client: AwsSsmClient,
        org_client: AwsOrgClient,
    ):
        self.config_s3_client = config_s3_client
        self.report_s3_client = report_s3_client
        self.ssm_client = ssm_client
        self.org_client = org_client

    @classmethod
    def get_aws_account(self) -> str:
        return self._get_env("AWS_ACCOUNT")

    @classmethod
    def get_config_bucket(self) -> str:
        return self._get_env("CONFIG_BUCKET")

    @classmethod
    def get_config_bucket_read_role(self) -> str:
        return self._get_env("CONFIG_BUCKET_READ_ROLE")

    @classmethod
    def get_audit_report_dashboard_url(self) -> str:
        return self._get_env("AUDIT_REPORT_DASHBOARD_URL")

    @staticmethod
    def get_log_level() -> str:
        log_level_cfg = environ.get("LOG_LEVEL", "WARNING")
        log_level = log_level_cfg.upper()
        if log_level not in ["CRITICAL", "FATAL", "ERROR", "WARNING", "WARN", "INFO", "DEBUG"]:
            raise InvalidConfigException(f"invalid LOG_LEVEL: {log_level_cfg}")

        return log_level

    @classmethod
    def get_report_bucket_read_role(self) -> str:
        return self._get_env("REPORT_BUCKET_READ_ROLE")

    @classmethod
    def get_s3_audit_report_key(self) -> str:
        return self._get_env("S3_AUDIT_REPORT_KEY")

    @classmethod
    def get_iam_audit_report_key(self) -> str:
        return self._get_env("IAM_AUDIT_REPORT_KEY")

    @classmethod
    def get_github_audit_report_key(self) -> str:
        return self._get_env("GITHUB_AUDIT_REPORT_KEY")

    @classmethod
    def get_github_webhook_report_key(self) -> str:
        return self._get_env("GITHUB_WEBHOOK_REPORT_KEY")

    @classmethod
    def get_github_webhook_host_ignore_key(self) -> str:
        return self._get_env("GITHUB_WEBHOOK_HOST_IGNORE_LIST")

    @classmethod
    def get_github_webhook_host_ignore_list(self) -> List[str]:
        return self._get_env("GITHUB_WEBHOOK_HOST_IGNORE_LIST").split(",")

    @classmethod
    def get_guardduty_runbook_url(self) -> str:
        return self._get_env("GUARDDUTY_RUNBOOK_URL")

    @classmethod
    def get_vpc_audit_report_key(self) -> str:
        return self._get_env("VPC_AUDIT_REPORT_KEY")

    @classmethod
    def get_vpc_resolver_audit_report_key(self) -> str:
        return self._get_env("VPC_RESOLVER_AUDIT_REPORT_KEY")

    @classmethod
    def get_public_query_audit_report_key(self) -> str:
        return self._get_env("PUBLIC_QUERY_AUDIT_REPORT_KEY")

    @classmethod
    def get_vpc_peering_audit_report_key(self) -> str:
        return self._get_env("VPC_PEERING_AUDIT_REPORT_KEY")

    @classmethod
    def get_ec2_audit_report_key(self) -> str:
        return self._get_env("EC2_AUDIT_REPORT_KEY")

    @classmethod
    def get_password_policy_audit_report_key(self) -> str:
        return self._get_env("PASSWORD_POLICY_AUDIT_REPORT_KEY")

    @classmethod
    def get_ignorable_report_keys(self) -> List[str]:
        return self._get_env("IGNORABLE_REPORT_KEYS").split(",")

    @classmethod
    def get_ssm_audit_report_key(self) -> str:
        return self._get_env("SSM_AUDIT_REPORT_KEY")

    @classmethod
    def get_slack_api_url(self) -> str:
        return self._get_env("SLACK_API_URL")

    @classmethod
    def get_slack_v2_api_key(self) -> str:
        return self._get_env("SLACK_V2_API_KEY")

    @staticmethod
    def get_slack_emoji() -> str:
        return Config._get_env("SLACK_EMOJI")

    @staticmethod
    def get_service_name() -> str:
        return Config._get_env("SERVICE_NAME")

    @classmethod
    def get_ssm_read_role(self) -> str:
        return self._get_env("SSM_READ_ROLE")

    @classmethod
    def get_org_account(self) -> str:
        return self._get_env("ORG_ACCOUNT")

    @classmethod
    def get_org_read_role(self) -> str:
        return self._get_env("ORG_READ_ROLE")

    def get_slack_notifier_config(self) -> SlackNotifierConfig:
        return SlackNotifierConfig(
            api_v2_key=self.ssm_client.get_parameter(self.get_slack_v2_api_key()),
            api_url=self.get_slack_api_url(),
            emoji=Config.get_slack_emoji(),
            source=Config.get_service_name(),
        )

    @classmethod
    def get_pagerduty_api_url(self) -> str:
        return self._get_env("PAGERDUTY_API_URL")

    def get_report_s3_client(self) -> AwsS3Client:
        return self.report_s3_client

    def get_org_client(self) -> AwsOrgClient:
        return self.org_client

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

    @classmethod
    def get_enable_wiki_checking(self) -> bool:
        return self._get_feature_switch("ENABLE_WIKI_CHECKING")

    @staticmethod
    def _get_feature_switch(key: str) -> bool:
        try:
            return environ[key].strip().upper() == "TRUE"
        except KeyError:
            return False

    def _fetch_config_files(self, prefix: str, mapper: Callable[[Dict[str, str]], T]) -> Set[T]:
        keys = self.config_s3_client.list_objects(self.get_config_bucket(), prefix)
        return set(chain.from_iterable(map(lambda key: self._load(key, mapper), keys)))

    def _load(self, key: str, mapper: Callable[[Dict[str, str]], T]) -> Set[T]:
        try:
            return {mapper(item) for item in self.config_s3_client.read_object(self.get_config_bucket(), key)}
        except ComplianceAlertingException as err:
            error(self, f"unable to load config file '{key}': {err}")
            return set()

    @staticmethod
    def configure_logging() -> Logger:
        logger = logging.getLogger()
        logger.setLevel(Config.get_log_level())
        logging.getLogger("botocore").setLevel(logging.ERROR)
        logging.getLogger("boto3").setLevel(logging.ERROR)
        logging.getLogger("requests").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("s3transfer").setLevel(logging.ERROR)
        return logger
