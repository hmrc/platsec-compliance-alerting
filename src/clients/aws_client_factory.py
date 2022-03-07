import boto3

from botocore.client import BaseClient
from botocore.exceptions import BotoCoreError, ClientError

from dataclasses import dataclass

from src.clients.aws_org_client import AwsOrgClient
from src.clients.aws_s3_client import AwsS3Client
from src.clients.aws_ssm_client import AwsSsmClient
from src.data.exceptions import ClientFactoryException


@dataclass(frozen=True)
class AwsCredentials:
    accessKeyId: str
    secretAccessKey: str
    sessionToken: str


class AwsClientFactory:
    def get_s3_client(self, account: str, role: str) -> AwsS3Client:
        return AwsS3Client(self._get_client("s3", account, role))

    def get_ssm_client(self, account: str, role: str) -> AwsSsmClient:
        return AwsSsmClient(self._get_client("ssm", account, role))

    def get_org_client(self, account: str, role: str) -> AwsOrgClient:
        return AwsOrgClient(self._get_client("organizations", account, role))

    def _get_client(self, service_name: str, account: str, role: str) -> BaseClient:
        assumed_role = self._assume_role(account, role)
        return boto3.client(
            service_name=service_name,
            aws_access_key_id=assumed_role.accessKeyId,
            aws_secret_access_key=assumed_role.secretAccessKey,
            aws_session_token=assumed_role.sessionToken,
        )

    @staticmethod
    def _assume_role(account: str, role: str) -> AwsCredentials:
        try:
            credentials_dict = boto3.client(service_name="sts").assume_role(
                DurationSeconds=900,
                RoleArn=f"arn:aws:iam::{account}:role/{role}",
                RoleSessionName=f"{role}",
            )
            return AwsCredentials(
                accessKeyId=credentials_dict["Credentials"]["AccessKeyId"],
                secretAccessKey=credentials_dict["Credentials"]["SecretAccessKey"],
                sessionToken=credentials_dict["Credentials"]["SessionToken"],
            )
        except (BotoCoreError, ClientError) as error:
            raise ClientFactoryException(f"unable to assume role '{role}' in account '{account}': {error}") from None
