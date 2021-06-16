import boto3

from dataclasses import dataclass

from botocore.client import BaseClient
from botocore.exceptions import ClientError, BotoCoreError

from src.aws_s3_client import AwsS3Client


@dataclass
class AwsCredentials:
    accessKeyId: str
    secretAccessKey: str
    sessionToken: str


class AwsClientFactory:
    def get_s3_client(self, account: str, role: str) -> AwsS3Client:
        return AwsS3Client(self._get_client("s3", account, role))

    def _get_client(self, service_name: str, account: str, role: str) -> BaseClient:
        assumed_role = self._assume_role(account, role)
        return boto3.client(
            service_name=service_name,
            aws_access_key_id=assumed_role.accessKeyId,
            aws_secret_access_key=assumed_role.secretAccessKey,
            aws_session_token=assumed_role.sessionToken,
        )

    def _assume_role(self, account: str, role: str) -> AwsCredentials:
        credentials_dict = boto3.client(service_name="sts").assume_role(
            DurationSeconds=600,
            RoleArn=f"arn:aws:iam::{account}:role/{role}",
            RoleSessionName=f"boto3_assuming_{role}"
        )
        return AwsCredentials(
            accessKeyId=credentials_dict["Credentials"]["AccessKeyId"],
            secretAccessKey=credentials_dict["Credentials"]["SecretAccessKey"],
            sessionToken=credentials_dict["Credentials"]["SessionToken"],
        )
