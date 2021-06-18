from logging import getLogger
from os import environ
from typing import Callable, Dict, List, Optional

from src import T
from src.clients.aws_s3_client import AwsS3Client
from src.clients.aws_client_factory import AwsClientFactory
from src.config.notification_filter_config import NotificationFilterConfig
from src.config.notification_mapping_config import NotificationMappingConfig
from src.data.exceptions import ComplianceAlertingException, MissingConfigException


class Config:
    def __init__(self) -> None:
        self._logger = getLogger(self.__class__.__name__)

    def get_aws_account(self) -> str:
        return self._get_env("AWS_ACCOUNT")

    def get_central_channel(self) -> str:
        return self._get_env("CENTRAL_CHANNEL")

    def get_config_bucket(self) -> str:
        return self._get_env("CONFIG_BUCKET")

    def get_config_bucket_read_role(self) -> str:
        return self._get_env("CONFIG_BUCKET_READ_ROLE")

    @staticmethod
    def _get_env(key: str) -> str:
        try:
            return environ[key]
        except KeyError:
            raise MissingConfigException(f"environment variable {key}")

    def get_notification_filters(self) -> List[NotificationFilterConfig]:
        return self._fetch_config_files("filters/", NotificationFilterConfig.from_dict)

    def get_notification_mappings(self) -> List[NotificationMappingConfig]:
        return self._fetch_config_files("mappings/", NotificationMappingConfig.from_dict)

    def _fetch_config_files(self, prefix: str, mapper: Callable[[Dict[str, str]], T]) -> List[T]:
        s3 = AwsClientFactory().get_s3_client(self.get_aws_account(), self.get_config_bucket_read_role())
        keys = s3.list_objects(self.get_config_bucket(), prefix)
        return list(filter(None, map(lambda key: self._load(key, mapper, s3), keys)))

    def _load(self, key: str, mapper: Callable[[Dict[str, str]], T], s3: AwsS3Client) -> Optional[T]:
        try:
            return mapper(s3.read_object(self.get_config_bucket(), key))
        except ComplianceAlertingException as err:
            self._logger.error(err)
            return None
