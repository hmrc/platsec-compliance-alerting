from unittest import TestCase
from unittest.mock import Mock, call, patch

from src.aws_client_factory import AwsClientFactory
from src.aws_s3_client import AwsS3Client


class TestAwsClientFactory(TestCase):
    def test_get_s3_client(self) -> None:
        boto_credentials = {
            "Credentials": {
                "AccessKeyId": "some_access_key",
                "SecretAccessKey": "some_secret_access_key",
                "SessionToken": "some_session_token",
            }
        }
        mock_sts_client = Mock(assume_role=Mock(return_value=boto_credentials))
        mock_s3_client = Mock()
        mock_boto3 = Mock(client=Mock(side_effect=[mock_sts_client, mock_s3_client]))

        with patch("src.aws_client_factory.boto3", mock_boto3):
            s3_client = AwsClientFactory().get_s3_client("some-account", "some-role")
            self.assertEqual(mock_s3_client, s3_client._s3)

        mock_boto3.client.assert_has_calls([
            call(service_name="sts"),
            call(
                service_name="s3",
                aws_access_key_id="some_access_key",
                aws_secret_access_key="some_secret_access_key",
                aws_session_token="some_session_token"
            ),
        ])
        mock_sts_client.assume_role.assert_called_once_with(
            DurationSeconds=600,
            RoleArn="arn:aws:iam::some-account:role/some-role",
            RoleSessionName="boto3_assuming_some-role"
        )
