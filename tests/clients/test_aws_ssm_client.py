from unittest import TestCase
from moto import mock_ssm

import boto3

from src.clients.aws_ssm_client import AwsSsmClient
from src.data.exceptions import AwsClientException


@mock_ssm
class TestAwsSsmClient(TestCase):
    def setUp(self) -> None:
        self.client = AwsSsmClient(boto3.client("ssm", region_name="us-east-1"))
        self.client._ssm.put_parameter(Name="test_parameter", Description="A test parameter", Value="test_param_value", Type="SecureString")

    def test_get_parameter(self) -> None:
        self.assertEqual("test_param_value", self.client.get_parameter("test_parameter"))
