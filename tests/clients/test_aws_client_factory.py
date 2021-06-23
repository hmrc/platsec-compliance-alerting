from unittest import TestCase
from unittest.mock import Mock, call, patch

from botocore.client import BaseClient

from src.clients import aws_client_factory
from src.clients.aws_client_factory import AwsClientFactory
from src.data.exceptions import ClientFactoryException

from tests import client_error


class TestAwsClientFactory(TestCase):
    def test_get_s3_client(self) -> None:
        boto_s3_client = Mock()

        def _get_client(service_name: str, account: str, role: str) -> BaseClient:
            return boto_s3_client if service_name == "s3" and account == "an-account" and role == "a-role" else None

        with patch.object(AwsClientFactory, "_get_client", side_effect=_get_client):
            self.assertEqual(boto_s3_client, AwsClientFactory().get_s3_client("an-account", "a-role")._s3)

    def test_get_ssm_client(self) -> None:
        boto_ssm_client = Mock()

        def _get_client(service_name: str, account: str, role: str) -> BaseClient:
            return boto_ssm_client if service_name == "ssm" and account == "ssm-acc" and role == "ssm-role" else None

        with patch.object(AwsClientFactory, "_get_client", side_effect=_get_client):
            self.assertEqual(boto_ssm_client, AwsClientFactory().get_ssm_client("ssm-acc", "ssm-role")._ssm)

    def test_get_client(self) -> None:
        boto_credentials = {
            "Credentials": {
                "AccessKeyId": "some_access_key",
                "SecretAccessKey": "some_secret_access_key",
                "SessionToken": "some_session_token",
            }
        }
        mock_sts_client = Mock(assume_role=Mock(return_value=boto_credentials))
        mock_client = Mock()
        mock_boto3 = Mock(client=Mock(side_effect=[mock_sts_client, mock_client]))

        with patch.object(aws_client_factory, "boto3", mock_boto3):
            client = AwsClientFactory()._get_client("some-service", "some-account", "some-role")
            self.assertEqual(mock_client, client)

        mock_boto3.client.assert_has_calls(
            [
                call(service_name="sts"),
                call(
                    service_name="some-service",
                    aws_access_key_id="some_access_key",
                    aws_secret_access_key="some_secret_access_key",
                    aws_session_token="some_session_token",
                ),
            ]
        )
        mock_sts_client.assume_role.assert_called_once_with(
            DurationSeconds=900,
            RoleArn="arn:aws:iam::some-account:role/some-role",
            RoleSessionName="boto3_assuming_some-role",
        )

    def test_get_client_failure(self) -> None:
        with patch.object(aws_client_factory, "boto3", Mock(client=Mock(side_effect=client_error()))):
            with self.assertRaisesRegex(ClientFactoryException, "AccessDenied"):
                AwsClientFactory()._get_client("service", "account", "role")
